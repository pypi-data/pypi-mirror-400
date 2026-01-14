"""
FedRAMP SSP Importer module.

This module provides the FedRAMPSSPImporter class for orchestrating the import
of FedRAMP System Security Plan (SSP) documents into RegScale.

Following SOLID principles:
- Single Responsibility: Orchestrates the SSP import workflow
- Open/Closed: Can be extended through handlers without modification
- Dependency Inversion: Uses injected handlers for specific operations
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("regscale")


class FedRAMPSSPImporter:
    """
    Orchestrator class for importing FedRAMP SSP documents into RegScale.

    This class coordinates the import of FedRAMP System Security Plan (SSP)
    documents by parsing the main document, Appendix A (control implementations),
    creating the SSP entity in RegScale, and processing all related data.

    Uses a dual-parser strategy for Appendix A to combine the strengths of
    DOCX parsing (checkbox/status detection) and Markdown parsing (page-spanning content).

    Attributes:
        file_path: Path to the SSP DOCX document.
        profile_id: RegScale profile ID for control mappings.
        appendix_a_path: Optional path to Appendix A document.
        version: FedRAMP version (default: 'rev5').
        save_data: Whether to save parsed data as JSON.
        add_missing: Whether to create missing controls from profile.

    Example:
        >>> importer = FedRAMPSSPImporter(
        ...     file_path="ssp.docx",
        ...     profile_id=123,
        ...     appendix_a_path="appendix_a.docx"
        ... )
        >>> ssp_id = importer.import_ssp()
        >>> print(f"Created SSP with ID: {ssp_id}")
    """

    def __init__(
        self,
        file_path: str,
        profile_id: int,
        appendix_a_path: Optional[str] = None,
        version: str = "rev5",
        save_data: bool = False,
        add_missing: bool = False,
    ) -> None:
        """
        Initialize the SSP importer.

        :param str file_path: Path to the SSP DOCX document.
        :param int profile_id: RegScale profile ID for control mappings.
        :param Optional[str] appendix_a_path: Path to Appendix A document.
        :param str version: FedRAMP version (default: 'rev5').
        :param bool save_data: Whether to save parsed data as JSON.
        :param bool add_missing: Whether to create missing controls from profile.
        """
        self._file_path = file_path
        self._profile_id = profile_id
        self._appendix_a_path = appendix_a_path
        self._version = version
        self._save_data = save_data
        self._add_missing = add_missing

        # State tracking
        self._is_imported = False
        self._ssp_id: Optional[int] = None

        # Data storage
        self._parsed_data: Dict[str, Any] = {}
        self._controls_data: Dict[str, Any] = {}

    @property
    def file_path(self) -> str:
        """Get the SSP document file path."""
        return self._file_path

    @property
    def profile_id(self) -> int:
        """Get the RegScale profile ID."""
        return self._profile_id

    @property
    def appendix_a_path(self) -> Optional[str]:
        """Get the Appendix A document path."""
        return self._appendix_a_path

    @property
    def version(self) -> str:
        """Get the FedRAMP version."""
        return self._version

    @property
    def save_data(self) -> bool:
        """Get the save_data flag."""
        return self._save_data

    @property
    def add_missing(self) -> bool:
        """Get the add_missing flag."""
        return self._add_missing

    @property
    def is_imported(self) -> bool:
        """Check if the SSP has been imported."""
        return self._is_imported

    @property
    def ssp_id(self) -> Optional[int]:
        """Get the SSP ID in RegScale (None if not imported)."""
        return self._ssp_id

    @property
    def parsed_data(self) -> Dict[str, Any]:
        """Get the parsed document data."""
        return self._parsed_data

    @property
    def controls_data(self) -> Dict[str, Any]:
        """Get the parsed controls data."""
        return self._controls_data

    def import_ssp(self) -> int:
        """
        Import the FedRAMP SSP document into RegScale.

        This is the main orchestration method that coordinates:
        1. Validation of input files and profile
        2. Parsing the main SSP document
        3. Parsing Appendix A (control implementations)
        4. Creating the SSP entity in RegScale
        5. Processing control implementations
        6. Extracting and uploading embedded images

        :return: The SSP ID in RegScale.
        :rtype: int
        :raises FileNotFoundError: If the SSP document doesn't exist.
        :raises ValueError: If the profile doesn't exist.
        """
        logger.info("Starting FedRAMP SSP import for: %s", self._file_path)

        # Step 1: Validate inputs
        self._validate_file_exists()
        self._validate_profile_exists()

        # Step 2: Parse main SSP document
        self._parsed_data = self._parse_document()

        # Step 3: Parse Appendix A (control implementations)
        self._controls_data = self._parse_appendix_a()

        # Step 4: Create SSP in RegScale
        self._ssp_id = self._create_ssp()

        # Step 5: Process control implementations
        self._process_controls()

        # Step 6: Extract and upload images
        self._extract_images()

        # Mark as imported
        self._is_imported = True
        logger.info("FedRAMP SSP import completed. SSP ID: %d", self._ssp_id)

        return self._ssp_id

    def _validate_file_exists(self) -> None:
        """
        Validate that the SSP document file exists.

        :raises FileNotFoundError: If the file doesn't exist.
        """
        path = Path(self._file_path)
        if not path.exists():
            raise FileNotFoundError(f"SSP document not found: {self._file_path}")

        if self._appendix_a_path:
            appendix_path = Path(self._appendix_a_path)
            if not appendix_path.exists():
                raise FileNotFoundError(f"Appendix A document not found: {self._appendix_a_path}")

        logger.debug("File validation passed")

    def _validate_profile_exists(self) -> None:
        """
        Validate that the RegScale profile exists.

        :raises ValueError: If the profile doesn't exist.
        """
        # This will be implemented to check profile via API
        # For now, just log that we would validate
        logger.debug("Validating profile ID: %d", self._profile_id)

    def _parse_document(self) -> Dict[str, Any]:
        """
        Parse the main SSP document.

        Uses SSPDocParser to extract metadata, tables, and text content
        from the FedRAMP SSP DOCX document.

        :return: Dictionary containing parsed SSP data.
        :rtype: Dict[str, Any]
        """
        logger.info("Parsing SSP document: %s", self._file_path)
        # Implementation will use SSPDocParser
        # For now, return empty dict as placeholder
        return {}

    def _parse_appendix_a(self) -> Dict[str, Any]:
        """
        Parse Appendix A using dual-parser strategy.

        Uses both DOCX parser (for checkboxes/status) and Markdown parser
        (for page-spanning content), then merges results for best coverage.

        :return: Dictionary containing merged control implementation data.
        :rtype: Dict[str, Any]
        """
        if not self._appendix_a_path:
            logger.debug("No Appendix A path provided, skipping")
            return {}

        logger.info("Parsing Appendix A: %s", self._appendix_a_path)

        # Import parsers
        try:
            from regscale.integrations.public.fedramp.appendix_parser import AppendixAParser
            from regscale.integrations.public.fedramp.markdown_appendix_parser import MarkdownAppendixParser
        except ImportError as e:
            logger.warning("Could not import appendix parsers: %s", e)
            return {}

        # Parse with DOCX parser
        docx_data: Dict[str, Any] = {}
        try:
            docx_parser = AppendixAParser(self._appendix_a_path)
            docx_data = docx_parser.fetch_controls_implementations()
            logger.debug("DOCX parser found %d controls", len(docx_data))
        except Exception as e:
            logger.warning("DOCX parsing failed: %s", e)

        # Parse with Markdown parser
        md_data: Dict[str, Any] = {}
        try:
            md_parser = MarkdownAppendixParser(self._appendix_a_path)
            md_data = md_parser.fetch_controls_implementations()
            logger.debug("Markdown parser found %d controls", len(md_data))
        except Exception as e:
            logger.warning("Markdown parsing failed: %s", e)

        # Merge results
        merged = self._merge_parser_results(docx_data, md_data)
        logger.info("Merged appendix data: %d controls", len(merged))

        return merged

    def _merge_parser_results(self, docx_data: Dict[str, Any], md_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge results from DOCX and Markdown parsers.

        DOCX parser is preferred for status/checkboxes, Markdown for parts/content.

        :param Dict[str, Any] docx_data: Data from DOCX parser.
        :param Dict[str, Any] md_data: Data from Markdown parser.
        :return: Merged data dictionary.
        :rtype: Dict[str, Any]
        """
        merged: Dict[str, Any] = {}

        # Get all control IDs from both parsers
        all_control_ids = set(docx_data.keys()) | set(md_data.keys())

        for control_id in all_control_ids:
            docx_control = docx_data.get(control_id, {})
            md_control = md_data.get(control_id, {})

            # Start with DOCX data (better for status)
            merged[control_id] = dict(docx_control)

            # Merge in Markdown data (better for parts)
            for key, value in md_control.items():
                # Use markdown value if: key missing, existing value is empty, or key is 'parts'
                # Markdown parts are preferred as they handle page-spanning better
                should_use_md = key not in merged[control_id] or not merged[control_id][key] or key == "parts"
                if should_use_md and value:
                    merged[control_id][key] = value

        return merged

    def _create_ssp(self) -> int:
        """
        Create the SSP entity in RegScale.

        Uses the parsed document data to create or update a SecurityPlan
        entity in RegScale.

        :return: The SSP ID in RegScale.
        :rtype: int
        """
        logger.info("Creating SSP in RegScale")
        # Implementation will create SecurityPlan via API
        # For now, return placeholder
        return 0

    def _process_controls(self) -> None:
        """
        Process control implementations from Appendix A.

        Creates or updates ControlImplementation entities in RegScale
        based on the parsed control data.
        """
        if not self._controls_data:
            logger.debug("No controls data to process")
            return

        logger.info("Processing %d controls", len(self._controls_data))
        # Implementation will process each control
        # and create ControlImplementation entities

    def _extract_images(self) -> None:
        """
        Extract and upload embedded images from the SSP document.

        Extracts images from the DOCX file and uploads them as
        attachments to the SSP in RegScale.
        """
        logger.info("Extracting images from SSP document")
        # Implementation will extract embedded images
        # and upload to RegScale

    def __repr__(self) -> str:
        """Return string representation of the importer."""
        return (
            f"FedRAMPSSPImporter("
            f"file_path={self._file_path!r}, "
            f"profile_id={self._profile_id}, "
            f"ssp_id={self._ssp_id})"
        )
