"""
FedRAMP CIS/CRM Importer module.

This module provides the FedRAMPCISCRMImporter class for orchestrating the import
of FedRAMP CIS/CRM (Customer Implementation Summary / Customer Responsibility Matrix)
workbooks into RegScale.

Following SOLID principles:
- Single Responsibility: Orchestrates the CIS/CRM import workflow
- Open/Closed: Can be extended through handlers without modification
- Dependency Inversion: Uses injected handlers for specific operations
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from regscale.integrations.public.fedramp.constants import ImplementationStatus

logger = logging.getLogger("regscale")


class FedRAMPCISCRMImporter:
    """
    Orchestrator class for importing FedRAMP CIS/CRM workbooks into RegScale.

    This class coordinates the import of FedRAMP Customer Implementation Summary (CIS)
    and Customer Responsibility Matrix (CRM) Excel workbooks by parsing worksheet data,
    creating the SSP entity in RegScale, and processing control implementations.

    Attributes:
        file_path: Path to the CIS/CRM Excel workbook.
        profile_id: RegScale profile ID for control mappings.
        cis_sheet_name: Name of the CIS worksheet to parse.
        crm_sheet_name: Optional name of the CRM worksheet to parse.
        version: FedRAMP version (default: 'rev5').
        leveraged_auth_id: Optional existing leveraged authorization ID.

    Example:
        >>> importer = FedRAMPCISCRMImporter(
        ...     file_path="fedramp_workbook.xlsx",
        ...     profile_id=123,
        ...     cis_sheet_name="CIS Worksheet",
        ...     crm_sheet_name="CRM Worksheet"
        ... )
        >>> ssp_id = importer.import_ciscrm()
        >>> print(f"Created SSP with ID: {ssp_id}")
    """

    def __init__(
        self,
        file_path: str,
        profile_id: int,
        cis_sheet_name: str,
        crm_sheet_name: Optional[str] = None,
        version: str = "rev5",
        leveraged_auth_id: Optional[int] = None,
    ) -> None:
        """
        Initialize the CIS/CRM importer.

        :param str file_path: Path to the CIS/CRM Excel workbook.
        :param int profile_id: RegScale profile ID for control mappings.
        :param str cis_sheet_name: Name of the CIS worksheet to parse.
        :param Optional[str] crm_sheet_name: Name of the CRM worksheet to parse.
        :param str version: FedRAMP version (default: 'rev5').
        :param Optional[int] leveraged_auth_id: Existing leveraged authorization ID.
        """
        self._file_path = file_path
        self._profile_id = profile_id
        self._cis_sheet_name = cis_sheet_name
        self._crm_sheet_name = crm_sheet_name
        self._version = version
        self._leveraged_auth_id = leveraged_auth_id

        # State tracking
        self._is_imported = False
        self._ssp_id: Optional[int] = None

        # Data storage
        self._cis_data: Dict[str, Any] = {}
        self._crm_data: Dict[str, Any] = {}
        self._instructions_data: Dict[str, Any] = {}

    @property
    def file_path(self) -> str:
        """Get the workbook file path."""
        return self._file_path

    @property
    def profile_id(self) -> int:
        """Get the RegScale profile ID."""
        return self._profile_id

    @property
    def cis_sheet_name(self) -> str:
        """Get the CIS worksheet name."""
        return self._cis_sheet_name

    @property
    def crm_sheet_name(self) -> Optional[str]:
        """Get the CRM worksheet name."""
        return self._crm_sheet_name

    @property
    def version(self) -> str:
        """Get the FedRAMP version."""
        return self._version

    @property
    def leveraged_auth_id(self) -> Optional[int]:
        """Get the leveraged authorization ID."""
        return self._leveraged_auth_id

    @property
    def is_imported(self) -> bool:
        """Check if the CIS/CRM has been imported."""
        return self._is_imported

    @property
    def ssp_id(self) -> Optional[int]:
        """Get the SSP ID in RegScale (None if not imported)."""
        return self._ssp_id

    @property
    def cis_data(self) -> Dict[str, Any]:
        """Get the parsed CIS worksheet data."""
        return self._cis_data

    @property
    def crm_data(self) -> Dict[str, Any]:
        """Get the parsed CRM worksheet data."""
        return self._crm_data

    @property
    def instructions_data(self) -> Dict[str, Any]:
        """Get the parsed instructions data."""
        return self._instructions_data

    def import_ciscrm(self) -> int:
        """
        Import the FedRAMP CIS/CRM workbook into RegScale.

        This is the main orchestration method that coordinates:
        1. Validation of input files and sheets
        2. Parsing instructions sheet for metadata
        3. Parsing CIS worksheet for control implementations
        4. Parsing CRM worksheet for responsibilities (if provided)
        5. Creating the SSP entity in RegScale
        6. Processing control implementations
        7. Processing implementation objectives
        8. Uploading the workbook file

        :return: The SSP ID in RegScale.
        :rtype: int
        :raises FileNotFoundError: If the workbook doesn't exist.
        :raises ValueError: If required worksheets don't exist.
        """
        logger.info("Starting FedRAMP CIS/CRM import for: %s", self._file_path)

        # Step 1: Validate inputs
        self._validate_file_exists()
        self._validate_sheets_exist()

        # Step 2: Parse instructions sheet for metadata
        self._instructions_data = self._parse_instructions()

        # Step 3: Parse CIS worksheet
        self._cis_data = self._parse_cis_worksheet()

        # Step 4: Parse CRM worksheet (if provided)
        self._crm_data = self._parse_crm_worksheet()

        # Step 5: Create SSP in RegScale
        self._ssp_id = self._create_ssp()

        # Step 6: Process control implementations
        self._process_implementations()

        # Step 7: Process implementation objectives
        self._process_objectives()

        # Step 8: Upload workbook file
        self._upload_workbook()

        # Mark as imported
        self._is_imported = True
        logger.info("FedRAMP CIS/CRM import completed. SSP ID: %d", self._ssp_id)

        return self._ssp_id

    def _validate_file_exists(self) -> None:
        """
        Validate that the workbook file exists.

        :raises FileNotFoundError: If the file doesn't exist.
        """
        path = Path(self._file_path)
        if not path.exists():
            raise FileNotFoundError(f"CIS/CRM workbook not found: {self._file_path}")

        logger.debug("File validation passed")

    def _validate_sheets_exist(self) -> None:
        """
        Validate that required worksheets exist in the workbook.

        :raises ValueError: If required worksheets don't exist.
        """
        # This will be implemented to check worksheet names
        logger.debug("Validating worksheets: CIS=%s, CRM=%s", self._cis_sheet_name, self._crm_sheet_name)

    def _parse_instructions(self) -> Dict[str, Any]:
        """
        Parse the Instructions sheet for SSP metadata.

        Extracts CSP info, system name, impact level, and other metadata
        from the Instructions worksheet.

        :return: Dictionary containing instructions metadata.
        :rtype: Dict[str, Any]
        """
        logger.info("Parsing Instructions sheet")
        # Implementation will parse Instructions sheet
        return {}

    def _parse_cis_worksheet(self) -> Dict[str, Any]:
        """
        Parse the CIS worksheet for control implementation data.

        Extracts control status, origination, and implementation details
        from the CIS worksheet.

        :return: Dictionary mapping control IDs to implementation data.
        :rtype: Dict[str, Any]
        """
        logger.info("Parsing CIS worksheet: %s", self._cis_sheet_name)
        # Implementation will parse CIS worksheet
        return {}

    def _parse_crm_worksheet(self) -> Dict[str, Any]:
        """
        Parse the CRM worksheet for customer responsibility data.

        Extracts inheritance flags and responsibility text from the CRM
        worksheet if provided.

        :return: Dictionary mapping control IDs to responsibility data.
        :rtype: Dict[str, Any]
        """
        if not self._crm_sheet_name:
            logger.debug("No CRM worksheet specified, skipping")
            return {}

        logger.info("Parsing CRM worksheet: %s", self._crm_sheet_name)
        # Implementation will parse CRM worksheet
        return {}

    def _create_ssp(self) -> int:
        """
        Create the SSP entity in RegScale.

        Uses the parsed data to create or update a SecurityPlan
        entity in RegScale.

        :return: The SSP ID in RegScale.
        :rtype: int
        """
        logger.info("Creating SSP in RegScale")
        # Implementation will create SecurityPlan via API
        return 0

    def _process_implementations(self) -> None:
        """
        Process control implementations from CIS worksheet.

        Updates existing control implementations with status and
        origination data from the CIS worksheet.
        """
        if not self._cis_data:
            logger.debug("No CIS data to process")
            return

        logger.info("Processing %d control implementations", len(self._cis_data))
        # Implementation will update control implementations

    def _process_objectives(self) -> None:
        """
        Process implementation objectives from CIS/CRM data.

        Creates or updates ImplementationObjective entities based on
        the parsed worksheet data.
        """
        logger.info("Processing implementation objectives")
        # Implementation will process objectives

    def _upload_workbook(self) -> None:
        """
        Upload the workbook file to RegScale.

        Uploads the CIS/CRM workbook as an attachment to the SSP.
        """
        logger.info("Uploading workbook to RegScale")
        # Implementation will upload file

    def _aggregate_status(self, statuses: List[str]) -> str:
        """
        Aggregate multiple control part statuses into a single status.

        Logic:
        - All "Implemented" → "Implemented"
        - Mix with ≥1 "Implemented" → "Partially Implemented"
        - All "Planned" → "Planned"
        - Any "N/A" or "Alternative" → "Not Applicable"
        - All empty or "Not Implemented" → "Not Implemented"

        :param List[str] statuses: List of status values to aggregate.
        :return: Aggregated status string.
        :rtype: str
        """
        if not statuses:
            return ImplementationStatus.NOT_IMPLEMENTED.value

        # Normalize statuses
        normalized = [s.strip() for s in statuses if s and s.strip()]

        if not normalized:
            return ImplementationStatus.NOT_IMPLEMENTED.value

        # Check for various conditions
        implemented_count = sum(1 for s in normalized if s.lower() == "implemented")
        planned_count = sum(1 for s in normalized if s.lower() == "planned")
        na_count = sum(1 for s in normalized if s.lower() in ("n/a", "not applicable", "alternative"))

        if implemented_count == len(normalized):
            return ImplementationStatus.IMPLEMENTED.value
        elif implemented_count > 0:
            return ImplementationStatus.PARTIALLY_IMPLEMENTED.value
        elif planned_count == len(normalized):
            return ImplementationStatus.PLANNED.value
        elif na_count > 0:
            return ImplementationStatus.NOT_APPLICABLE.value
        else:
            return ImplementationStatus.NOT_IMPLEMENTED.value

    def __repr__(self) -> str:
        """Return string representation of the importer."""
        return (
            f"FedRAMPCISCRMImporter("
            f"file_path={self._file_path!r}, "
            f"profile_id={self._profile_id}, "
            f"cis_sheet={self._cis_sheet_name!r}, "
            f"ssp_id={self._ssp_id})"
        )
