"""
Web Application Scanning (WAS) operations module for Qualys WAS API integration.
"""

import logging
import traceback
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Create logger for this module
logger = logging.getLogger("regscale")

# XML constants to avoid duplication
XML_SERVICE_REQUEST_OPEN = "<ServiceRequest>"
XML_SERVICE_REQUEST_CLOSE = "</ServiceRequest>"
XML_FILTERS_OPEN = "<filters>"
XML_FILTERS_CLOSE = "</filters>"


def auth_was_api() -> tuple[str, dict]:
    """
    Authenticate WAS API using HTTP Basic Auth (same credentials as VMDR)

    :return: A tuple of the base URL and a dictionary of headers
    :rtype: tuple[str, dict]
    """
    from . import QUALYS_API, _get_config  # noqa: C0415

    config = _get_config()
    # Use qualysMockUrl if available (for testing), otherwise use qualysUrl
    qualys_url = config.get("qualysMockUrl") or config.get("qualysUrl")
    user = config.get("qualysUserName")
    password = config.get("qualysPassword")

    logger.debug("WAS Auth - Configuring authentication for %s", qualys_url)

    # Transform to qualysapi subdomain for WAS API (matching production behavior)
    if qualys_url and "qualysguard" in qualys_url:
        base_url = qualys_url.replace("qualysguard", "qualysapi")
        logger.debug("WAS: Transformed qualysguard -> qualysapi: %s", base_url)
    else:
        base_url = qualys_url

    # WAS uses XML format - set appropriate content-type header
    headers = {"content-type": "text/xml", "X-Requested-With": "RegScale CLI"}

    # HTTP Basic Auth handled by QUALYS_API session
    QUALYS_API.auth = (user, password)

    logger.debug("WAS API authentication configured for XML endpoints")
    return base_url, headers


def _parse_xml_response(xml_string: str) -> Optional[ET.Element]:
    """
    Parse XML response and return root element

    :param str xml_string: The XML string to parse
    :return: Root element or None if parsing fails
    :rtype: Optional[ET.Element]
    """
    try:
        return ET.fromstring(xml_string)
    except ET.ParseError as e:
        logger.error("XML parsing error: %s", e)
        logger.debug("Raw XML: %s", xml_string[:500])
        return None


def _make_was_api_request(current_url: str, headers: dict, xml_body: str = "<ServiceRequest></ServiceRequest>") -> dict:
    """
    Make API request to WAS endpoints using XML format (production-compatible)

    :param str current_url: The URL for the API request
    :param dict headers: Headers to include in the request
    :param str xml_body: XML body for the request (default: empty ServiceRequest)
    :return: Response data containing WAS data parsed from XML
    :rtype: dict
    """
    from . import QUALYS_API  # noqa: C0415

    # Make API request with XML body (POST request matching production)
    response = QUALYS_API.post(url=current_url, headers=headers, data=xml_body)

    # Validate response
    if not response.ok:
        logger.error("WAS API request failed: %s - %s", response.status_code, response.text[:500])
        if response.status_code == 404:
            logger.error("WAS API - TROUBLESHOOTING:")
            logger.error("  1. Verify Web Application Scanning (WAS) module is enabled in your Qualys account")
            logger.error("  2. Verify you have web applications configured in Qualys WAS")
            logger.error("  3. Contact Qualys support if WAS module is not available")
            logger.error("  Note: 404 typically indicates WAS module is not enabled or no webapps exist")
        return {"data": [], "count": 0, "hasMoreRecords": False}

    # Parse XML response
    root = _parse_xml_response(response.text)
    if root is None:
        logger.error("Failed to parse WAS XML response")
        return {"data": [], "count": 0, "hasMoreRecords": False}

    # Extract metadata from ServiceResponse
    response_code = root.findtext("responseCode", "UNKNOWN")
    count_text = root.findtext("count", "0")
    has_more_text = root.findtext("hasMoreRecords", "false")

    try:
        count = int(count_text)
    except ValueError:
        count = 0

    has_more = has_more_text.lower() == "true"

    logger.debug("WAS XML Response: responseCode=%s, count=%s, hasMore=%s", response_code, count, has_more)

    # Check for INVALID_API_VERSION error
    if response_code == "INVALID_API_VERSION":
        error_msg = root.findtext("responseErrorDetails/errorMessage", "Unknown API version error")
        logger.warning("WAS API version error: %s", error_msg)
        return {
            "data": [],
            "count": 0,
            "hasMoreRecords": False,
            "responseCode": response_code,
            "error": error_msg,
            "_root": root,
        }

    return {
        "data": root.find("data"),  # Return data element for further processing
        "count": count,
        "hasMoreRecords": has_more,
        "responseCode": response_code,
        "_root": root,  # Keep root for advanced processing
    }


def _make_was_api_request_with_fallback(
    base_url: str, endpoint: str, headers: dict, xml_body: str = "<ServiceRequest></ServiceRequest>"
) -> tuple[dict, str]:
    """
    Make WAS API request with automatic API version fallback

    Tries API versions in order: 3.0, 2.0 (skipping 4.0 as it's known to be problematic)

    :param str base_url: The base URL for the Qualys WAS API
    :param str endpoint: The API endpoint (e.g., "search/was/webapp")
    :param dict headers: Headers to include in the request
    :param str xml_body: XML body for the request
    :return: Tuple of (response_data dict, successful_version str)
    :rtype: tuple[dict, str]
    """
    from .url_utils import get_api_versions  # noqa: C0415

    # Get supported versions, but skip 4.0 (known issue with Qualys)
    all_versions = get_api_versions("was")
    versions_to_try = [v for v in all_versions if v != "4.0"]

    if not versions_to_try:
        versions_to_try = ["3.0", "2.0"]  # Fallback to known working versions

    logger.debug("WAS API: Will try versions in order: %s", versions_to_try)

    last_error = None
    for version in versions_to_try:
        url = urljoin(base_url, f"/qps/rest/{version}/{endpoint}")
        logger.debug("WAS API: Trying version %s at %s", version, url)

        response_data = _make_was_api_request(url, headers, xml_body)
        response_code = response_data.get("responseCode", "UNKNOWN")

        if response_code == "INVALID_API_VERSION":
            logger.info("WAS API: Version %s not supported, trying next version...", version)
            last_error = response_data.get("error", f"API version {version} not supported")
            continue

        # Success or other error (not version-related)
        logger.info("WAS API: Using version %s successfully", version)
        return response_data, version

    # All versions failed
    logger.error("WAS API: All versions failed. Last error: %s", last_error)
    return {"data": [], "count": 0, "hasMoreRecords": False, "error": last_error or "All API versions failed"}, None


def _parse_webapp_xml(webapp_element: ET.Element) -> Dict:
    """
    Parse a single WebApp XML element into a dictionary

    :param ET.Element webapp_element: The WebApp XML element
    :return: Dictionary representation of the webapp
    :rtype: Dict
    """
    webapp = {}

    # Extract simple text fields
    webapp["id"] = webapp_element.findtext("id", "")
    webapp["name"] = webapp_element.findtext("name", "")
    webapp["url"] = webapp_element.findtext("url", "")
    webapp["domain"] = webapp_element.findtext("domain", "")
    webapp["owner"] = webapp_element.findtext("owner/username", "")
    webapp["technology"] = webapp_element.findtext("technology", "")
    webapp["created"] = webapp_element.findtext("created", "")
    webapp["lastScanned"] = webapp_element.findtext("lastScanDate", "")
    webapp["scanStatus"] = webapp_element.findtext("scanStatus", "")

    # Parse tags if present
    tags_element = webapp_element.find("tags")
    if tags_element is not None:
        webapp["tags"] = {}
        for tag in tags_element.findall("Tag"):
            tag_name = tag.findtext("name", "")
            tag_value = tag.findtext("value", "")
            if tag_name:
                webapp["tags"][tag_name] = tag_value

    # Parse vulnerability counts if present
    vuln_stats = webapp_element.find("vulnStats")
    if vuln_stats is not None:
        webapp["vulnerabilityCount"] = {
            "critical": int(vuln_stats.findtext("critical", "0")),
            "high": int(vuln_stats.findtext("high", "0")),
            "medium": int(vuln_stats.findtext("medium", "0")),
            "low": int(vuln_stats.findtext("low", "0")),
            "info": int(vuln_stats.findtext("info", "0")),
        }

    # Generate webappId (use 'id' field for consistency)
    webapp["webappId"] = webapp["id"]

    return webapp


def _parse_finding_xml(finding_element: ET.Element) -> Dict:
    """
    Parse a single Finding XML element into a dictionary

    :param ET.Element finding_element: The Finding XML element
    :return: Dictionary representation of the finding
    :rtype: Dict
    """
    finding = {}

    # Extract simple text fields
    finding["id"] = finding_element.findtext("id", "")
    finding["uniqueId"] = finding_element.findtext("uniqueId", "")
    finding["qid"] = finding_element.findtext("qid", "")
    finding["type"] = finding_element.findtext("type", "")
    finding["severity"] = finding_element.findtext("severity", "")
    finding["status"] = finding_element.findtext("status", "")
    finding["firstDetectedDate"] = finding_element.findtext("firstDetectedDate", "")
    finding["lastDetectedDate"] = finding_element.findtext("lastDetectedDate", "")
    finding["lastTestedDate"] = finding_element.findtext("lastTestedDate", "")
    finding["url"] = finding_element.findtext("url", "")
    finding["webAppId"] = finding_element.findtext("webApp/id", "")
    finding["webAppName"] = finding_element.findtext("webApp/name", "")

    # Parse vulnerability details if present
    vuln = finding_element.find("vuln")
    if vuln is not None:
        finding["title"] = vuln.findtext("title", "")
        finding["description"] = vuln.findtext("description", "")
        finding["solution"] = vuln.findtext("solution", "")
        finding["impact"] = vuln.findtext("impact", "")
        finding["category"] = vuln.findtext("category", "")
        finding["owasp"] = vuln.findtext("owasp", "")
        finding["wasc"] = vuln.findtext("wasc", "")
        finding["cve"] = vuln.findtext("cve", "")

    return finding


def _build_xml_request_body(filters: Optional[Dict], limit: int, last_id: Optional[str] = None) -> str:
    """
    Build XML request body for WAS API with filters and pagination.

    :param Optional[Dict] filters: Filters to apply
    :param int limit: Results limit per page
    :param Optional[str] last_id: Last ID for cursor-based pagination
    :return: XML request body string
    :rtype: str
    """
    xml_body = XML_SERVICE_REQUEST_OPEN

    if filters:
        xml_body += XML_FILTERS_OPEN
        for key, value in filters.items():
            xml_body += f"<{key}>{value}</{key}>"
        xml_body += XML_FILTERS_CLOSE

    if last_id:
        xml_body += f"{XML_FILTERS_OPEN}<Criteria field='id' operator='GREATER'>{last_id}</Criteria>{XML_FILTERS_CLOSE}"

    xml_body += f"<preferences><limitResults>{limit}</limitResults></preferences>"
    xml_body += XML_SERVICE_REQUEST_CLOSE

    return xml_body


def _process_pagination_page(
    response_data: dict, page: int, item_type: str, parser_func
) -> tuple[List[Dict], bool, Optional[str]]:
    """
    Process a single pagination page response.

    :param dict response_data: Response data from WAS API
    :param int page: Current page number
    :param str item_type: Type of item being fetched (WebApp or Finding)
    :param parser_func: Function to parse individual items
    :return: Tuple of (items, has_more, last_id)
    :rtype: tuple[List[Dict], bool, Optional[str]]
    """
    data_element = response_data.get("data")
    if data_element is None:
        logger.warning("No data element found in WAS response")
        return [], False, None

    item_elements = data_element.findall(item_type)
    items = [parser_func(item) for item in item_elements]

    if not items:
        logger.debug("No more %ss found, ending pagination", item_type.lower())
        return [], False, None

    logger.debug("Fetched page %s: %s %ss", page + 1, len(items), item_type.lower())

    # Check for more pages
    has_more = response_data.get("hasMoreRecords", False)
    if not has_more:
        logger.debug("No more records available (hasMoreRecords=false)")
        return items, False, None

    # Get lastId for next page
    response_root = response_data.get("_root")
    if response_root is None:
        logger.warning("No response root available for pagination, ending")
        return items, False, None

    last_id = response_root.findtext("lastId")
    if not last_id:
        logger.warning("hasMoreRecords=true but no lastId found, ending pagination")
        return items, False, None

    logger.debug("Using lastId for next page: %s", last_id)
    return items, True, last_id


def fetch_all_webapps(filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Fetch all web applications with pagination using XML API with automatic API version fallback

    :param Optional[Dict] filters: Filters to apply to the web applications
    :param int limit: Number of web applications to fetch per page
    :return: A list of web applications
    :rtype: List[Dict]
    """
    base_url, headers = auth_was_api()

    all_webapps = []
    page = 0
    last_id = None
    api_version = None  # Will be determined by fallback logic

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=None,
    )

    with progress:
        task = progress.add_task("[green]Fetching WAS web applications...", total=None)

        while True:
            xml_body = _build_xml_request_body(filters, limit, last_id)

            # Use fallback for first request to determine working API version
            if api_version is None:
                response_data, api_version = _make_was_api_request_with_fallback(
                    base_url, "search/was/webapp", headers, xml_body
                )
                if api_version is None:
                    logger.error("Failed to find working WAS API version")
                    break
            else:
                # Use determined version for subsequent requests
                current_url = urljoin(base_url, f"/qps/rest/{api_version}/search/was/webapp")
                response_data = _make_was_api_request(current_url, headers, xml_body)

            webapps, has_more, next_last_id = _process_pagination_page(response_data, page, "WebApp", _parse_webapp_xml)

            if not webapps:
                break

            all_webapps.extend(webapps)
            progress.update(
                task,
                description=f"[green]Fetching WAS web applications... (Page {page + 1}, Total: {len(all_webapps)})",
            )

            if not has_more:
                break

            last_id = next_last_id
            page += 1

        progress.update(task, total=len(all_webapps), completed=len(all_webapps))

    logger.info("Fetched %s web applications from WAS", len(all_webapps))
    return all_webapps


def fetch_all_findings(filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Fetch all WAS findings with pagination using XML API with automatic API version fallback

    :param Optional[Dict] filters: Filters to apply to the findings
    :param int limit: Number of findings to fetch per page
    :return: A list of findings
    :rtype: List[Dict]
    """
    base_url, headers = auth_was_api()

    all_findings = []
    page = 0
    last_id = None
    api_version = None  # Will be determined by fallback logic

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=None,
    )

    with progress:
        task = progress.add_task("[green]Fetching WAS findings...", total=None)

        while True:
            xml_body = _build_xml_request_body(filters, limit, last_id)

            # Use fallback for first request to determine working API version
            if api_version is None:
                response_data, api_version = _make_was_api_request_with_fallback(
                    base_url, "search/was/finding", headers, xml_body
                )
                if api_version is None:
                    logger.error("Failed to find working WAS API version")
                    break
            else:
                # Use determined version for subsequent requests
                current_url = urljoin(base_url, f"/qps/rest/{api_version}/search/was/finding")
                response_data = _make_was_api_request(current_url, headers, xml_body)

            findings, has_more, next_last_id = _process_pagination_page(
                response_data, page, "Finding", _parse_finding_xml
            )

            if not findings:
                break

            all_findings.extend(findings)
            progress.update(
                task,
                description=f"[green]Fetching WAS findings... (Page {page + 1}, Total: {len(all_findings)})",
            )

            if not has_more:
                break

            last_id = next_last_id
            page += 1

        progress.update(task, total=len(all_findings), completed=len(all_findings))

    logger.info("Fetched %s findings from WAS", len(all_findings))
    return all_findings


def fetch_latest_scan_for_webapp(_webapp_id: str) -> Optional[Dict]:
    """
    Fetch the most recent completed scan for a web application

    NOTE: This function is deprecated and not used in the XML-based workflow.
    WAS findings are fetched directly, not through scans.

    :param str _webapp_id: The UUID of the web application (unused - deprecated)
    :return: The most recent scan or None if not found
    :rtype: Optional[Dict]
    """
    logger.warning("fetch_latest_scan_for_webapp is deprecated - use fetch_all_findings instead")
    return None


def fetch_scan_vulnerabilities(_scan_id: str) -> List[Dict]:
    """
    Fetch all vulnerabilities for a specific scan

    NOTE: This function is deprecated and not used in the XML-based workflow.
    WAS findings are fetched directly, not through scans.

    :param str _scan_id: The UUID of the scan (unused - deprecated)
    :return: A list of vulnerabilities
    :rtype: List[Dict]
    """
    logger.warning("fetch_scan_vulnerabilities is deprecated - use fetch_all_findings instead")
    return []


def fetch_all_was_vulnerabilities(filters: Optional[Dict] = None, _max_workers: int = 10) -> List[Dict]:
    """
    Fetch all web applications and their findings/vulnerabilities

    This function now uses the XML-based WAS findings API to fetch vulnerabilities
    directly, matching production Qualys behavior.

    :param Optional[Dict] filters: Filters to apply to the web applications and findings
    :param int _max_workers: Maximum number of worker threads (unused in XML workflow)
    :return: A list of web applications with vulnerabilities attached
    :rtype: List[Dict]
    """
    # Fetch all webapps first
    webapps = fetch_all_webapps(filters)

    if not webapps:
        logger.info("No web applications found to fetch vulnerabilities for")
        return []

    # Fetch all findings
    findings = fetch_all_findings(filters)

    logger.info("Fetched %s findings across all WAS webapps", len(findings))

    # Group findings by webAppId and attach to corresponding webapp
    findings_by_webapp = {}
    for finding in findings:
        webapp_id = finding.get("webAppId")
        if webapp_id:
            if webapp_id not in findings_by_webapp:
                findings_by_webapp[webapp_id] = []
            findings_by_webapp[webapp_id].append(finding)

    # Attach findings to webapps
    for webapp in webapps:
        webapp_id = webapp.get("id")
        webapp["vulnerabilities"] = findings_by_webapp.get(webapp_id, [])
        logger.debug(
            "Webapp %s (%s) has %s vulnerabilities", webapp.get("name"), webapp_id, len(webapp["vulnerabilities"])
        )

    logger.info("Completed attaching vulnerabilities to %s webapps", len(webapps))
    return webapps


# ==================================================================================
# WAS Scan Listing Functions
# ==================================================================================


def _parse_wasscan_xml(scan_element: ET.Element):
    """
    Parse a single WasScan XML element into a dictionary.

    :param ET.Element scan_element: The WasScan XML element
    :return: Dictionary representation of the scan
    :rtype: Dict
    """
    scan = {}

    # Extract simple text fields
    scan["id"] = scan_element.findtext("id", "")
    scan["name"] = scan_element.findtext("name", "")
    scan["reference"] = scan_element.findtext("reference", "")
    scan["type"] = scan_element.findtext("type", "")
    scan["mode"] = scan_element.findtext("mode", "")
    scan["status"] = scan_element.findtext("status", "")
    scan["launchedDate"] = scan_element.findtext("launchedDate", "")
    scan["launchedBy"] = scan_element.findtext("launchedBy/username", "")

    # Parse target info
    target = scan_element.find("target")
    if target is not None:
        scan["targetWebAppId"] = target.findtext("webApp/id", "")
        scan["targetWebAppName"] = target.findtext("webApp/name", "")

    # Parse results (vulnerability counts)
    results = scan_element.find("results")
    if results is not None:
        scan["resultsCritical"] = int(results.findtext("critical", "0"))
        scan["resultsHigh"] = int(results.findtext("high", "0"))
        scan["resultsMedium"] = int(results.findtext("medium", "0"))
        scan["resultsLow"] = int(results.findtext("low", "0"))
        scan["resultsInfo"] = int(results.findtext("info", "0"))

    return scan


def _wasscan_to_summary(scan: Dict):
    """
    Convert WAS scan dict to ScanSummary.

    :param Dict scan: Raw WAS scan data
    :return: Normalized scan summary or None
    :rtype: Optional[ScanSummary]
    """
    from .vmdr import ScanSummary  # noqa: C0415

    try:
        scan_id = scan.get("id", "")
        scan_name = scan.get("name", "") or scan.get("reference", "")
        title = scan_name if scan_name else f"WAS Scan {scan_id}"
        status = scan.get("status", "Unknown")

        # Parse scan date
        launch_date_str = scan.get("launchedDate", "")
        scan_date = None
        if launch_date_str:
            try:
                # Try common ISO formats
                for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        scan_date = datetime.strptime(launch_date_str, fmt)
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.debug("Could not parse WAS scan date: %s - %s", launch_date_str, e)

        # Calculate total vulnerability count
        vuln_count = (
            scan.get("resultsCritical", 0)
            + scan.get("resultsHigh", 0)
            + scan.get("resultsMedium", 0)
            + scan.get("resultsLow", 0)
            + scan.get("resultsInfo", 0)
        )

        # Target count is 1 (single webapp per scan)
        target_count = 1 if scan.get("targetWebAppId") else None

        return ScanSummary(
            scan_id=scan_id,
            scan_type="WAS",
            title=title,
            status=status,
            scan_date=scan_date,
            target_count=target_count,
            vuln_count=vuln_count if vuln_count > 0 else None,
            duration=None,
            module="was",
        )
    except Exception as e:
        logger.warning("Failed to parse WAS scan: %s", e)
        return None


def list_was_scans(days: int) -> list:
    """
    List WAS scans from the last N days.

    Queries the Qualys WAS API /qps/rest/3.0/search/was/wasscan endpoint to retrieve
    scan metadata with cursor-based pagination. Only returns scans launched after the
    specified date threshold.

    :param int days: Number of days to look back for scans
    :return: List of scan summaries, sorted by date (newest first)
    :rtype: List[ScanSummary]
    """
    from .vmdr import ScanSummary  # noqa: C0415

    logger.info("Fetching WAS scans from last %s days", days)

    try:
        base_url, headers = auth_was_api()
        current_url = urljoin(base_url, "/qps/rest/3.0/search/was/wasscan")

        # Calculate date filter
        scan_date_since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Build date filter for WAS API
        filters = {"Criteria": f'<Criteria field="launchedDate" operator="GREATER">{scan_date_since}</Criteria>'}

        all_scans = []
        page = 0
        last_id = None
        limit = 100

        logger.debug("Fetching WAS scans launched after %s", scan_date_since)

        while True:
            xml_body = _build_xml_request_body(filters, limit, last_id)
            response_data = _make_was_api_request(current_url, headers, xml_body)

            scans, has_more, next_last_id = _process_pagination_page(response_data, page, "WasScan", _parse_wasscan_xml)

            if not scans:
                break

            all_scans.extend(scans)
            logger.debug("Fetched page %s: %s WAS scans (Total: %s)", page + 1, len(scans), len(all_scans))

            if not has_more:
                break

            last_id = next_last_id
            page += 1

        # Convert to ScanSummary objects
        scan_summaries = []
        for scan in all_scans:
            summary = _wasscan_to_summary(scan)
            if summary:
                scan_summaries.append(summary)

        # Sort by date (newest first)
        scan_summaries.sort(key=lambda s: s.scan_date or datetime.min, reverse=True)

        logger.info("Retrieved %s WAS scans", len(scan_summaries))
        return scan_summaries

    except requests.RequestException as e:
        logger.error("WAS API request failed: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error fetching WAS scans: %s", e)
        logger.debug(traceback.format_exc())
        return []
