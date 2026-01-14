"""
Base appendix parser abstract class for FedRAMP Appendix A document parsing.

This module provides the abstract base class for FedRAMP Appendix A parsers,
which extract control implementation data from SSP appendices.

Following SOLID principles:
- Single Responsibility: Only defines the appendix parsing interface
- Open/Closed: Can be extended without modification
- Liskov Substitution: All subclasses can be used interchangeably
"""

from abc import abstractmethod
from typing import Dict, List, Optional

from regscale.integrations.control_matcher import ControlMatcher
from regscale.integrations.public.fedramp.ssp.parsers.base import BaseParser


class BaseAppendixParser(BaseParser):
    """
    Abstract base class for FedRAMP Appendix A parsers.

    This class extends BaseParser with functionality specific to parsing
    FedRAMP Appendix A documents, which contain control implementation
    details organized by control ID.

    Concrete implementations must implement `fetch_controls_implementations()`
    to extract control data from their specific document format (DOCX, Markdown, etc.).

    Attributes:
        filename: Path to the document being parsed.
        controls_implementations: Dictionary mapping control IDs to implementation data.

    Example:
        >>> class DocxAppendixParser(BaseAppendixParser):
        ...     def fetch_controls_implementations(self) -> Dict[str, Dict]:
        ...         # Parse DOCX and populate self.controls_implementations
        ...         self.controls_implementations = {"AC-1": {"status": "Implemented"}}
        ...         return self.controls_implementations
        ...
        ...     def parse(self) -> Dict:
        ...         return self.fetch_controls_implementations()
        ...
        >>> parser = DocxAppendixParser("appendix_a.docx")
        >>> data = parser.fetch_controls_implementations()
        >>> parser.control_ids
        ['AC-1']
    """

    def __init__(self, filename: str) -> None:
        """
        Initialize the appendix parser with a document filename.

        :param str filename: Path to the appendix document to parse.
        """
        super().__init__(filename)
        self.controls_implementations: Dict[str, Dict] = {}

    @abstractmethod
    def fetch_controls_implementations(self) -> Dict[str, Dict]:
        """
        Extract control implementations from the document.

        This is the main extraction method that concrete implementations must
        override. Implementations should populate `self.controls_implementations`
        with the extracted data.

        :return: Dictionary mapping control IDs to their implementation data.
        :rtype: Dict[str, Dict]
        """
        pass

    @staticmethod
    def normalize_control_id(control_id: Optional[str]) -> str:
        """
        Normalize a control ID to its canonical form.

        Uses ControlMatcher for consistent normalization across all parsers.

        - Removes leading zeros: AC-01 -> AC-1
        - Converts parentheses to dot: AC-2(1) -> AC-2.1
        - Removes spaces: AC-2 (1) -> AC-2.1
        - Uppercase family and enhancement letter

        :param Optional[str] control_id: Control ID to normalize.
        :return: Normalized control ID.
        :rtype: str
        """
        if not control_id:
            return ""
        parsed = ControlMatcher.parse_control_id(control_id)
        return parsed if parsed else control_id.strip()

    def get_control_implementation(self, control_id: str) -> Optional[Dict]:
        """
        Get the implementation data for a specific control.

        Performs lookup using normalized control ID to handle format variations.

        :param str control_id: The control ID to look up (e.g., "AC-1", "AC-01").
        :return: Implementation data dictionary or None if not found.
        :rtype: Optional[Dict]
        """
        if not control_id:
            return None

        # Try direct lookup first
        if control_id in self.controls_implementations:
            return self.controls_implementations[control_id]

        # Try normalized lookup
        normalized = self.normalize_control_id(control_id)
        if normalized in self.controls_implementations:
            return self.controls_implementations[normalized]

        # Try to find using variations
        matcher = ControlMatcher()
        variations = matcher._get_control_id_variations(control_id)
        for variation in variations:
            if variation in self.controls_implementations:
                return self.controls_implementations[variation]

        return None

    @property
    def control_ids(self) -> List[str]:
        """
        Get list of all control IDs in the parsed document.

        :return: List of control IDs.
        :rtype: List[str]
        """
        return list(self.controls_implementations.keys())
