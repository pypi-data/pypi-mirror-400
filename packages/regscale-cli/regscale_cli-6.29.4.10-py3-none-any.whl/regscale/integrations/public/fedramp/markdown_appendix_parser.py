"""
This module provides a markdown-based parser for FedRAMP Appendix A documents.

The MarkdownAppendixParser uses pypandoc to convert DOCX files to markdown,
which properly handles content that spans page breaks in the original document.
This approach is more reliable than parsing Word XML directly because:
1. Pandoc normalizes the document structure
2. Page breaks are handled transparently
3. Tables split by page breaks are properly merged in the output
"""

import logging
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pypandoc

from regscale.integrations.public.fedramp.fedramp_common import CHECKBOX_CHARS

logger = logging.getLogger("regscale")

# Suppress pypandoc debug logging
logging.getLogger("pypandoc").setLevel(logging.WARNING)

# Control section markers
CONTROL_SUMMARY_MARKER = "Control Summary Information"
SOLUTION_MARKER = "What is the solution and how is it implemented?"

# Implementation statuses
STATUSES = [
    "Implemented",
    "Partially Implemented",
    "Planned",
    "In Remediation",
    "Inherited",
    "Alternative Implementation",
    "Not Applicable",
    "Archived",
    "Risk Accepted",
]

# Control originations
ORIGINATIONS = [
    "Service Provider Corporate",
    "Service Provider System Specific",
    "Service Provider Hybrid (Corporate and System Specific)",
    "Configured by Customer (Customer System Specific)",
    "Provided by Customer (Customer System Specific)",
    "Shared (Service Provider and Customer Responsibility)",
    "Inherited from pre-existing FedRAMP Authorization",
]

# Regex patterns - Control ID pattern for markdown tables (may have ** bold markers)
# Pattern to find "AC-2 Control Summary" or similar in tables
# Use bounded quantifiers to prevent ReDoS attacks
CONTROL_SUMMARY_PATTERN = re.compile(r"\*?\*?([A-Z]{2}-\d+(?:\(\d+\))?)\s{1,10}Control\s{1,10}Summary", re.IGNORECASE)
# Pattern to find control ID at start of section (e.g., "AC-2 Account Management")
# Pattern for control section headers - handles both plain text and markdown headers
# Use #+\s{0,5} (1+ hashes) instead of #*\s{0,5} to avoid matching empty string
CONTROL_SECTION_PATTERN = re.compile(r"^(?:#{1,6}\s{0,5})?([A-Z]{2}-\d+(?:\(\d+\))?)\s{1,10}[A-Za-z]", re.MULTILINE)
# Use atomic patterns with negated character classes to avoid backtracking
PART_PATTERN = re.compile(r"Part\s{1,5}([a-z])\s*:", re.IGNORECASE)

# Extended part patterns for various FedRAMP document formats
# Use bounded quantifiers to prevent ReDoS attacks
EXTENDED_PART_PATTERNS = [
    PART_PATTERN,
    re.compile(r"(?:^|\n)\s{0,10}\(([a-z])\)\s{0,5}[:\.\-]", re.MULTILINE),  # "(a):" or "(a)." format
    re.compile(r"(?:Item|Section)\s{1,10}([a-z])\s{0,5}[:\-]", re.IGNORECASE),  # "Item a:" format
    re.compile(r"(?:^|\n)\s{0,10}([a-z])\)\s{0,5}", re.MULTILINE),  # "a)" format at line start
]

# Parameter patterns: matches various FedRAMP parameter formats
# Use bounded quantifiers and negated character classes to prevent ReDoS attacks
PARAMETER_PATTERNS = [
    # Standard: "Parameter AC-2(a): value" - use negated character class instead of .+?
    re.compile(
        r"Parameter\s{1,10}([A-Z]{2}-\d{1,3}(?:\([a-z0-9]{1,5}\))?)\s{0,5}[:\-]\s{0,5}([^\n]{1,1000})",
        re.IGNORECASE,
    ),
    # Assignment format: "AC-2(a) Assignment: value"
    re.compile(
        r"([A-Z]{2}-\d{1,3}(?:\([a-z0-9]{1,5}\))?)\s{0,5}(?:Assignment|Selection|Value)\s{0,5}[:\-]\s{0,5}([^\n]{1,1000})",
        re.IGNORECASE,
    ),
    # Simple numbered parameter: "Parameter 1: value"
    re.compile(
        r"Parameter\s{0,5}(\d+)\s{0,5}[:\-]\s{0,5}([^\n]{1,1000})",
        re.IGNORECASE,
    ),
    # Fallback single-line pattern for basic cases
    re.compile(
        r"Parameter\s{1,10}([A-Z]{2}-\d{1,3}(?:\([a-z0-9]{1,5}\))?):\s{0,5}([^\n]{1,500})",
        re.IGNORECASE,
    ),
]


class MarkdownAppendixParser:
    """
    A parser for FedRAMP Appendix A documents that uses markdown conversion.

    This parser converts DOCX files to markdown using pypandoc, then extracts
    control implementation data from the resulting markdown tables. This approach
    handles page breaks gracefully because the markdown output properly merges
    content that was split across pages in the original document.
    """

    def __init__(self, filename: str):
        """
        Initialize the parser with a DOCX file.

        :param str filename: Path to the DOCX file to parse.
        """
        self.filename = filename
        self.markdown_content = ""
        self.controls_implementations: Dict[str, Dict] = {}
        self._convert_to_markdown()

    def _convert_to_markdown(self) -> None:
        """Convert the DOCX file to markdown using pypandoc."""
        try:
            self.markdown_content = pypandoc.convert_file(
                self.filename, "markdown", extra_args=["--wrap=none"]  # Prevent line wrapping in output
            )
            logger.debug("Successfully converted DOCX to markdown (%d characters)", len(self.markdown_content))
        except Exception as e:
            logger.error("Failed to convert DOCX to markdown: %s", e)
            raise

    def fetch_controls_implementations(self) -> Dict[str, Dict]:
        """
        Extract control implementations from the markdown content.

        :return: Dictionary mapping control IDs to their implementation data.
        :rtype: Dict[str, Dict]
        """
        self._parse_markdown_content()
        return self.controls_implementations

    def _parse_markdown_content(self) -> None:
        """Parse the markdown content to extract control implementations."""
        # Split content into control sections
        control_sections = self._split_into_control_sections()

        for control_id, section_content in control_sections.items():
            control_data = self._parse_control_section(section_content, control_id)
            if control_data:
                self.controls_implementations[control_id] = control_data

        logger.debug("Parsed %d controls from markdown", len(self.controls_implementations))

    def _split_into_control_sections(self) -> Dict[str, str]:
        """
        Split markdown content into sections by control ID.

        The markdown structure has:
        1. Control section headers like "AC-2 Account Management (L)(M)(H)"
        2. Control tables with "**AC-2 Control Summary Information**"

        :return: Dictionary mapping control IDs to their section content.
        :rtype: Dict[str, str]
        """
        sections = {}

        # Find all control summary sections using the table pattern
        # This is more reliable than section headers
        for match in CONTROL_SUMMARY_PATTERN.finditer(self.markdown_content):
            control_id = match.group(1)

            # Find the start of this control's content (look backward for section start)
            match_pos = match.start()
            section_start = self._find_section_start(match_pos)

            # Find the end of this control's content (next control or end of doc)
            section_end = self._find_section_end(match_pos)

            # DEBUG: Log AC-2 section boundaries
            if control_id.upper() == "AC-2":
                logger.debug(
                    "[DEBUG AC-2] Section boundaries: start=%d, end=%d, total_len=%d",
                    section_start,
                    section_end,
                    len(self.markdown_content),
                )
                # Check what comes after the section end
                if section_end < len(self.markdown_content):
                    next_chars = self.markdown_content[section_end : section_end + 200]
                    logger.debug("[DEBUG AC-2] Content after section ends: %s", next_chars[:200])

            # Extract the section
            section_content = self.markdown_content[section_start:section_end]
            sections[control_id] = section_content

        logger.debug("Found %d control sections in markdown", len(sections))
        return sections

    def _find_section_start(self, summary_pos: int) -> int:
        """
        Find the start of a control section by looking backward from the summary table.

        :param int summary_pos: Position of the Control Summary table.
        :return: Start position of the section.
        :rtype: int
        """
        # Look backward for a control section header or previous table end
        search_text = self.markdown_content[:summary_pos]

        # Find the last control section pattern before this position
        last_section_match = None
        for match in CONTROL_SECTION_PATTERN.finditer(search_text):
            last_section_match = match

        if last_section_match:
            return last_section_match.start()

        # If no section header found, start from beginning or last table end
        return max(0, summary_pos - 5000)  # Reasonable lookback

    def _find_section_end(self, summary_pos: int) -> int:
        """
        Find the end of a control section.

        :param int summary_pos: Position of current Control Summary table.
        :return: End position of the section.
        :rtype: int
        """
        # Look for the next control summary table
        search_text = self.markdown_content[summary_pos + 50 :]

        next_match = CONTROL_SUMMARY_PATTERN.search(search_text)
        if next_match:
            # Also look for the section header of the next control
            section_match = CONTROL_SECTION_PATTERN.search(search_text)
            if section_match and section_match.start() < next_match.start():
                return summary_pos + 50 + section_match.start()
            return summary_pos + 50 + next_match.start()

        return len(self.markdown_content)

    def _parse_control_section(self, section: str, control_id: str = "") -> Optional[Dict]:
        """
        Parse a single control section to extract implementation data.

        :param str section: The section content.
        :param str control_id: Control ID for debug logging.
        :return: Dictionary containing control implementation data.
        :rtype: Optional[Dict]
        """
        control_data: Dict = {}

        # DEBUG: Log section boundaries for AC-2
        if control_id and control_id.upper() == "AC-2":
            logger.debug("[DEBUG AC-2] Section length: %d chars", len(section))

        # Extract status
        status = self._extract_status(section)
        if status:
            control_data["status"] = status

        # Extract origination
        origination = self._extract_origination(section)
        if origination:
            control_data["origination"] = origination

        # Extract parameters
        parameters = self._extract_parameters(section)
        if parameters:
            control_data["parameters"] = parameters

        # Extract parts (implementation statements)
        parts = self._extract_parts(section, control_id)
        if parts:
            control_data["parts"] = parts

        # Extract responsibility
        responsibility = self._extract_responsibility(section)
        if responsibility:
            control_data["responsibility"] = responsibility

        return control_data if control_data else None

    def _extract_status(self, section: str) -> Optional[str]:
        """
        Extract implementation status from section.

        :param str section: The section content.
        :return: The implementation status.
        :rtype: Optional[str]
        """
        for status in STATUSES:
            # Look for checked status
            for char in CHECKBOX_CHARS:
                pattern = f"{char}\\s*{re.escape(status)}"
                if re.search(pattern, section, re.IGNORECASE):
                    return status
        return None

    def _extract_origination(self, section: str) -> Optional[str]:
        """
        Extract control origination from section.

        :param str section: The section content.
        :return: Comma-separated origination values.
        :rtype: Optional[str]
        """
        found_originations = []

        for origination in ORIGINATIONS:
            for char in CHECKBOX_CHARS:
                # Check for checked origination
                pattern = f"{char}\\s*{re.escape(origination)}"
                if re.search(pattern, section, re.IGNORECASE):
                    if origination not in found_originations:
                        found_originations.append(origination)
                    break

        return ",".join(found_originations) if found_originations else None

    def _extract_parameters(self, section: str) -> List[Dict[str, str]]:
        """
        Extract parameters from section using multiple pattern formats.

        :param str section: The section content.
        :return: List of parameter dictionaries.
        :rtype: List[Dict[str, str]]
        """
        parameters = []
        found_names: set = set()

        for pattern in PARAMETER_PATTERNS:
            for match in pattern.finditer(section):
                param_name = match.group(1).strip()
                param_value = match.group(2).strip()

                # Clean up multi-line values
                param_value = re.sub(r"\s+", " ", param_value)
                # Reasonable limit on value length
                param_value = param_value[:1000]

                # Avoid duplicates
                if param_name not in found_names and param_value:
                    parameters.append({"name": param_name, "value": param_value})
                    found_names.add(param_name)

        return parameters

    def _extract_parts(self, section: str, control_id: str = "") -> List[Dict[str, str]]:
        """
        Extract implementation parts from section.

        This method finds the "What is the solution" section and extracts
        all parts (Part a, Part b, etc.) along with their content.
        Content that spans page breaks is properly merged.

        :param str section: The section content.
        :param str control_id: Control ID for debug logging.
        :return: List of part dictionaries.
        :rtype: List[Dict[str, str]]
        """
        parts = []

        # Find the solution section
        solution_idx = section.lower().find("what is the solution")
        if solution_idx == -1:
            return parts

        solution_section = section[solution_idx:]

        # Extract content from markdown tables
        table_content = self._extract_table_content(solution_section)

        if not table_content:
            return parts

        # DEBUG: Log for AC-2 to trace Part I extraction
        if control_id and control_id.upper() == "AC-2":
            logger.debug("[DEBUG AC-2] Solution section length: %d chars", len(solution_section))
            logger.debug("[DEBUG AC-2] Table content length: %d chars", len(table_content))
            # Check if Part I exists in the content
            part_i_found = "part i" in table_content.lower()
            logger.debug("[DEBUG AC-2] 'Part I' found in table content: %s", part_i_found)
            if not part_i_found:
                # Show last 500 chars of table content to see where it ends
                logger.debug(
                    "[DEBUG AC-2] Table content ends with: ...%s",
                    table_content[-500:] if len(table_content) > 500 else table_content,
                )

        # Parse parts from the combined table content
        parts = self._parse_parts_from_content(table_content)

        # DEBUG: Log extracted parts for AC-2
        if control_id and control_id.upper() == "AC-2":
            part_names = [p.get("name", "") for p in parts]
            logger.debug("[DEBUG AC-2] Extracted parts: %s", part_names)

        return parts

    def _extract_table_content(self, section: str) -> str:
        """
        Extract and merge content from markdown/HTML tables.

        This method handles tables that were split by page breaks by
        collecting all table content until a new control section starts.
        Supports both pipe-style markdown tables and HTML tables from pandoc.

        :param str section: The section containing tables.
        :return: Combined table content with preserved formatting.
        :rtype: str
        """
        # Check if content has HTML tables (from pandoc conversion)
        if "<table" in section.lower() or "<td" in section.lower():
            return self._extract_html_table_content(section)

        # Fall back to pipe-style markdown tables
        return self._extract_markdown_table_content(section)

    def _extract_html_table_content(self, section: str) -> str:
        """
        Extract content from HTML tables produced by pandoc conversion.

        :param str section: Section containing HTML tables.
        :return: Extracted text content.
        :rtype: str
        """
        # Remove HTML tags but preserve paragraph breaks
        content = section

        # Convert paragraph tags to newlines for structure
        content = re.sub(r"<p>", "\n", content, flags=re.IGNORECASE)
        content = re.sub(r"</p>", "\n", content, flags=re.IGNORECASE)

        # Convert list items to newlines
        content = re.sub(r"<li[^>]*>", "\n• ", content, flags=re.IGNORECASE)
        content = re.sub(r"</li>", "", content, flags=re.IGNORECASE)

        # Convert table rows to newlines
        content = re.sub(r"</tr>", "\n", content, flags=re.IGNORECASE)
        content = re.sub(r"</td>", " ", content, flags=re.IGNORECASE)
        content = re.sub(r"</th>", " ", content, flags=re.IGNORECASE)

        # Remove all remaining HTML tags
        content = re.sub(r"<[^>]+>", " ", content)

        # Clean up HTML entities - use str.replace() for simple literal replacements
        content = content.replace("&nbsp;", " ")
        content = content.replace("&amp;", "&")
        content = content.replace("&lt;", "<")
        content = content.replace("&gt;", ">")
        content = content.replace("&quot;", '"')
        content = re.sub(r"&#\d+;", " ", content)  # Keep regex for numeric entities

        # Clean up excessive whitespace while preserving paragraph breaks
        # Use bounded quantifiers to prevent ReDoS attacks
        content = re.sub(r"[ \t]{1,100}", " ", content)
        content = re.sub(r"\n[ \t]{1,100}", "\n", content)
        content = re.sub(r"[ \t]{1,100}\n", "\n", content)
        content = re.sub(r"\n{3,}", "\n\n", content)

        return content.strip()

    def _extract_markdown_table_content(self, section: str) -> str:
        """
        Extract content from pipe-style markdown tables.

        :param str section: Section containing markdown tables.
        :return: Extracted text content.
        :rtype: str
        """
        content_lines = []
        lines = section.split("\n")
        in_table = False
        current_paragraph = []

        for line in lines:
            # Check if we're in a table (pipe characters or table borders)
            if line.strip().startswith("|") or line.strip().startswith("+"):
                in_table = True
                # Extract content from table row
                content = self._extract_line_content(line)
                if content:
                    current_paragraph.append(content)
                elif current_paragraph:
                    # Empty content line - end of paragraph
                    content_lines.append(" ".join(current_paragraph))
                    current_paragraph = []
            elif in_table and not line.strip():
                # Empty line - preserve paragraph break
                if current_paragraph:
                    content_lines.append(" ".join(current_paragraph))
                    current_paragraph = []
            elif line.strip().startswith("="):
                # Table header separator
                pass

        # Don't forget last paragraph
        if current_paragraph:
            content_lines.append(" ".join(current_paragraph))

        # Join paragraphs with double newline to preserve structure
        return "\n\n".join(content_lines)

    def _extract_line_content(self, line: str) -> str:
        """
        Extract text content from a markdown table line.

        :param str line: A markdown table line.
        :return: Extracted text content.
        :rtype: str
        """
        # Remove table border characters
        content = line.strip()
        if content.startswith("|"):
            content = content[1:]
        if content.endswith("|"):
            content = content[:-1]
        if content.startswith("+") or content.endswith("+"):
            return ""
        if all(c in "-=+" for c in content):
            return ""

        # Clean up extra whitespace
        content = " ".join(content.split())
        return content.strip()

    def _parse_parts_from_content(self, content: str) -> List[Dict[str, str]]:
        """
        Parse part sections from combined content using multiple pattern formats.

        :param str content: Combined table content.
        :return: List of part dictionaries.
        :rtype: List[Dict[str, str]]
        """
        parts = []

        # Try each pattern until we find matches
        part_matches = []
        for pattern in EXTENDED_PART_PATTERNS:
            part_matches = list(pattern.finditer(content))
            if part_matches:
                break

        if not part_matches:
            # No explicit parts, treat as single part
            clean_content = self._clean_solution_content(content)
            if clean_content:
                parts.append({"name": "Default Part", "value": clean_content})
            return parts

        for i, match in enumerate(part_matches):
            part_letter = match.group(1).lower()
            part_name = f"Part {part_letter}"

            # Get content until next part or end
            start_idx = match.end()
            if i + 1 < len(part_matches):
                end_idx = part_matches[i + 1].start()
            else:
                end_idx = len(content)

            part_content = content[start_idx:end_idx].strip()
            part_content = self._clean_solution_content(part_content)

            if part_content:
                parts.append({"name": part_name, "value": part_content})

        return parts

    def _clean_solution_content(self, content: str) -> str:
        """
        Clean solution content by removing table and HTML artifacts while preserving formatting.

        :param str content: Raw content from table.
        :return: Cleaned content with preserved paragraph structure.
        :rtype: str
        """
        # Remove the "What is the solution" header if present
        content = re.sub(r"What is the solution and how is it implemented\??\s*", "", content, flags=re.IGNORECASE)

        # Remove table border artifacts
        content = re.sub(r"\+[-=]+\+", "", content)
        content = content.replace("|", "")

        # Remove markdown blockquote artifacts (> followed by optional whitespace and period)
        content = re.sub(r">\s*\.", "", content)
        # Remove standalone > characters (blockquote markers)
        content = re.sub(r"^\s*>\s*$", "", content, flags=re.MULTILINE)

        # Remove residual HTML-like artifacts from conversion
        content = re.sub(r"</?(?:p|br|strong|em|u|span|div|table|tr|td|th)[^>]*>", " ", content, flags=re.IGNORECASE)
        # Remove HTML entities
        content = re.sub(r"&nbsp;|&amp;|&lt;|&gt;|&quot;|&#\d+;", " ", content)
        # Remove markdown bold/italic markers that may have been left over
        content = re.sub(r"\*\*|\*|__", "", content)

        # Clean up each paragraph while preserving structure
        paragraphs = content.split("\n\n")
        cleaned_paragraphs = []
        for para in paragraphs:
            # Normalize whitespace within paragraph only
            cleaned = " ".join(para.split())
            if cleaned and cleaned.strip(": "):
                cleaned_paragraphs.append(cleaned.strip(": "))

        # Rejoin with double newlines to preserve paragraph breaks
        return "\n\n".join(cleaned_paragraphs)

    def _extract_responsibility(self, section: str) -> Optional[str]:
        """
        Extract responsible role from section.

        :param str section: The section content.
        :return: The responsible role.
        :rtype: Optional[str]
        """
        # Use bounded quantifiers to prevent ReDoS attacks
        match = re.search(r"Responsible\s{1,10}Role[:\s]{1,5}([^\n|+]+)", section, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None


def _get_preferred_value(docx_data: Dict, md_data: Dict, key: str, prefer_docx: bool = True) -> Optional[str]:
    """
    Get the preferred value for a field from DOCX or markdown parser results.

    :param Dict docx_data: Data from DOCX parser.
    :param Dict md_data: Data from markdown parser.
    :param str key: The key to look up.
    :param bool prefer_docx: If True, prefer DOCX parser value; otherwise prefer markdown.
    :return: The preferred value or None.
    :rtype: Optional[str]
    """
    if prefer_docx:
        return docx_data.get(key) or md_data.get(key)
    return md_data.get(key) or docx_data.get(key)


def _build_statement_from_parts(parts: List[Dict[str, str]]) -> str:
    """
    Build a combined implementation statement from parts with HTML formatting.

    :param List[Dict[str, str]] parts: List of part dictionaries with 'name' and 'value'.
    :return: Combined statement with part labels and HTML formatting.
    :rtype: str
    """
    if not parts:
        return ""
    statement_parts = []
    for part in parts:
        name = part.get("name", "")
        value = part.get("value", "")
        if value:
            # Convert newlines to HTML paragraphs for proper formatting in RegScale
            # Double newlines become paragraph breaks, single newlines become line breaks
            formatted_value = value.replace("\n\n", "</p><p>").replace("\n", "<br/>")
            # Wrap in paragraph tags
            formatted_value = f"<p>{formatted_value}</p>"
            # Format as "Part a: content" with bold part label
            statement_parts.append(f"<p><strong>{name}:</strong></p>{formatted_value}")
    return "".join(statement_parts)


def _choose_part_value(md_value: str, docx_value: str, name: str) -> str:
    """
    Choose the best value between markdown and DOCX based on content quality.

    :param md_value: Value from markdown parser.
    :param docx_value: Value from DOCX parser.
    :param name: Part name for logging.
    :return: Chosen value.
    """
    if not md_value:
        return docx_value
    if not docx_value:
        return md_value

    # Both have content - prefer markdown if it has substantial content (>=50%)
    if len(md_value) >= len(docx_value) * 0.5:
        return md_value

    logger.debug(
        "Using DOCX content for %s (markdown has only %d%% of DOCX content)",
        name,
        int(len(md_value) / len(docx_value) * 100),
    )
    return docx_value


def _part_sort_key(part: Dict) -> str:
    """Extract sort key from part name (e.g., 'a' from 'Part a')."""
    name = part.get("name", "").lower()
    if "part" in name:
        parts_list = name.split()
        if len(parts_list) >= 2:
            return parts_list[1]
    return name


def _merge_parts(docx_parts: List[Dict[str, str]], md_parts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Merge parts from DOCX and markdown parsers with quality-based selection.

    For parts found in both:
    - Use markdown content if it has at least 50% of DOCX content length
    - Fall back to DOCX if markdown content is significantly shorter (incomplete extraction)
    Include any parts from DOCX that markdown didn't find (don't lose data).

    :param List[Dict[str, str]] docx_parts: Parts from DOCX parser.
    :param List[Dict[str, str]] md_parts: Parts from markdown parser.
    :return: Merged list of parts.
    :rtype: List[Dict[str, str]]
    """
    if not docx_parts:
        return md_parts or []
    if not md_parts:
        return docx_parts

    # Build lookups by normalized name
    md_lookup = {p.get("name", "").lower().strip(): p for p in md_parts}
    docx_lookup = {p.get("name", "").lower().strip(): p for p in docx_parts}

    merged_parts = []
    all_names = set(md_lookup.keys()) | set(docx_lookup.keys())

    for name in all_names:
        md_part = md_lookup.get(name, {})
        docx_part = docx_lookup.get(name, {})
        chosen_value = _choose_part_value(md_part.get("value", ""), docx_part.get("value", ""), name)

        if chosen_value:
            display_name = md_part.get("name") or docx_part.get("name") or name
            merged_parts.append({"name": display_name, "value": chosen_value})

    return sorted(merged_parts, key=_part_sort_key)


def _merge_originations(docx_orig: str, md_orig: str) -> Optional[str]:
    """
    Merge origination values from both parsers, combining unique values.

    :param str docx_orig: Origination from DOCX parser.
    :param str md_orig: Origination from markdown parser.
    :return: Merged origination string or None.
    :rtype: Optional[str]
    """
    if docx_orig and md_orig:
        all_origs = {o.strip() for o in docx_orig.split(",") if o.strip()}
        all_origs.update(o.strip() for o in md_orig.split(",") if o.strip())
        return ",".join(sorted(all_origs))
    return docx_orig or md_orig or None


def _merge_parameters_dedup(docx_params: List, md_params: List) -> List:
    """
    Merge parameters from both parsers, avoiding duplicates by name.

    :param List docx_params: Parameters from DOCX parser.
    :param List md_params: Parameters from markdown parser.
    :return: Merged parameters list without duplicates.
    :rtype: List
    """
    merged_params = []
    param_names: set = set()
    for params in [docx_params, md_params]:
        for param in params:
            name = param.get("name", "")
            if name and name not in param_names:
                merged_params.append(param)
                param_names.add(name)
    return merged_params


def _merge_single_control(docx_data: Dict, md_data: Dict) -> Dict:
    """
    Merge data for a single control from both parsers with enhanced logic.

    :param Dict docx_data: Data from DOCX parser for this control.
    :param Dict md_data: Data from markdown parser for this control.
    :return: Merged control data.
    :rtype: Dict
    """
    merged_control: Dict = {}

    # Status: Prefer DOCX (better checkbox detection) unless empty
    status = docx_data.get("status") or md_data.get("status")
    if status:
        merged_control["status"] = status

    # Origination: Merge from both parsers, combine unique values
    if merged_orig := _merge_originations(docx_data.get("origination", ""), md_data.get("origination", "")):
        merged_control["origination"] = merged_orig

    # Parameters: Combine from both, avoid duplicates
    if merged_params := _merge_parameters_dedup(docx_data.get("parameters", []), md_data.get("parameters", [])):
        merged_control["parameters"] = merged_params

    # Merge parts from both parsers - markdown for content quality, DOCX for completeness
    merged_parts = _merge_parts(docx_data.get("parts", []), md_data.get("parts", []))
    if merged_parts:
        merged_control["parts"] = merged_parts
        merged_control["statement"] = _build_statement_from_parts(merged_parts)
    elif docx_data.get("statement"):
        merged_control["statement"] = docx_data["statement"]

    # Only use statement if we don't have parts (fallback case)
    if "parts" not in merged_control:
        if value := _get_preferred_value(docx_data, md_data, "statement", prefer_docx=False):
            merged_control["statement"] = value

    # Use DOCX parser for responsibility
    if value := _get_preferred_value(docx_data, md_data, "responsibility", prefer_docx=True):
        merged_control["responsibility"] = value

    # Merge additional FedRAMP fields (new fields from enhanced extraction)
    for field in ["planned_implementation_date", "exclusion_justification", "alternative_implementation"]:
        if value := (docx_data.get(field) or md_data.get(field)):
            merged_control[field] = value

    return merged_control


def merge_parser_results(docx_parser_results: Dict, md_parser_results: Dict) -> Dict:
    """
    Merge results from the DOCX parser and markdown parser.

    The DOCX parser is better at extracting checkbox states and statuses,
    while the markdown parser handles page-spanning content better.

    :param Dict docx_parser_results: Results from AppendixAParser.
    :param Dict md_parser_results: Results from MarkdownAppendixParser.
    :return: Merged results using best data from each parser.
    :rtype: Dict
    """
    merged = {}
    all_control_ids = set(docx_parser_results.keys()) | set(md_parser_results.keys())

    for control_id in all_control_ids:
        docx_data = docx_parser_results.get(control_id, {})
        md_data = md_parser_results.get(control_id, {})
        merged_control = _merge_single_control(docx_data, md_data)
        if merged_control:
            merged[control_id] = merged_control

    return merged
