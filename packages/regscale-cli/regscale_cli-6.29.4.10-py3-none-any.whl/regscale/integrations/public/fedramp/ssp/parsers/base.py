"""
Base parser abstract class for FedRAMP document parsing.

This module provides the foundational abstract base class for all FedRAMP
document parsers. It defines the interface contract that all parsers must follow.

Following SOLID principles:
- Single Responsibility: Only defines the parsing interface
- Open/Closed: Can be extended without modification
- Liskov Substitution: All subclasses can be used interchangeably
- Interface Segregation: Minimal interface with only essential methods
- Dependency Inversion: Depends on abstractions, not concrete implementations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseParser(ABC):
    """
    Abstract base class for FedRAMP document parsers.

    This class defines the interface contract for all document parsers.
    Concrete implementations must implement the `parse()` method.

    Attributes:
        filename: Path to the document being parsed.
        _parsed: Internal flag tracking whether parsing has completed.

    Example:
        >>> class MyParser(BaseParser):
        ...     def parse(self) -> Dict[str, Any]:
        ...         self._parsed = True
        ...         return {"key": "value"}
        ...
        >>> parser = MyParser("document.docx")
        >>> parser.is_parsed
        False
        >>> result = parser.parse()
        >>> parser.is_parsed
        True
    """

    def __init__(self, filename: str) -> None:
        """
        Initialize the parser with a document filename.

        :param str filename: Path to the document to parse.
        """
        self._filename = filename
        self._parsed = False

    @property
    def filename(self) -> str:
        """
        Get the filename of the document being parsed.

        :return: The filename/path of the document.
        :rtype: str
        """
        return self._filename

    @property
    def is_parsed(self) -> bool:
        """
        Check if the document has been parsed.

        :return: True if parse() has been called and completed, False otherwise.
        :rtype: bool
        """
        return self._parsed

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        Parse the document and return the extracted data.

        This is the main parsing method that concrete implementations must
        override. Implementations should set `self._parsed = True` when
        parsing completes successfully.

        :return: Dictionary containing the parsed data.
        :rtype: Dict[str, Any]
        """
        pass

    def __repr__(self) -> str:
        """
        Return a string representation of the parser.

        :return: String representation including class name and filename.
        :rtype: str
        """
        return f"{self.__class__.__name__}(filename={self._filename!r})"
