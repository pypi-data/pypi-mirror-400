"""
Qualys VMDR (Vulnerability Management, Detection and Response) API integration

This module provides functions to interact with the Qualys VMDR API for fetching
vulnerability scan data and enriching it with Knowledge Base information.
"""

import csv
import logging
import os
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth

from regscale.core.app import create_logger

logger = logging.getLogger(__name__)

# Constants
RESPONSE_LOG_FORMAT = "Response: %s"


@dataclass
class ScanSummary:
    """
    Standardized scan summary across all Qualys modules.

    This dataclass provides a consistent format for scan metadata from different
    Qualys modules (VMDR, WAS, Container Security, Total Cloud).
    """

    scan_id: str
    scan_type: str  # "VMDR", "WAS", "Container Security", "Total Cloud"
    title: str
    status: str
    scan_date: Optional[datetime]
    target_count: Optional[int]  # Number of hosts/apps/containers scanned
    vuln_count: Optional[int]  # Total vulnerabilities found (if available)
    duration: Optional[str]  # Human-readable duration
    module: str  # Source module identifier

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.

        :return: Dictionary representation of scan summary
        :rtype: dict
        """
        return {
            "scan_id": self.scan_id,
            "scan_type": self.scan_type,
            "title": self.title,
            "status": self.status,
            "scan_date": self.scan_date.isoformat() if self.scan_date else None,
            "target_count": self.target_count,
            "vuln_count": self.vuln_count,
            "duration": self.duration,
            "module": self.module,
        }


def auth_vmdr_api() -> tuple[str, HTTPBasicAuth, dict]:
    """
    Authenticate with Qualys VMDR API and return credentials

    :return: Tuple of (base_url, auth, headers)
    :rtype: tuple[str, HTTPBasicAuth, dict]
    """
    from . import _get_config  # noqa: C0415

    config = _get_config()

    username = config.get("qualysUserName")
    password = config.get("qualysPassword")
    base_url = config.get("qualysUrl")

    if not all([username, password, base_url]):
        raise ValueError("Qualys credentials not configured. Please check init.yaml or environment variables.")

    auth = HTTPBasicAuth(username, password)
    headers = {"X-Requested-With": "RegScale CLI"}

    logger.info("Authenticated with Qualys VMDR API")
    return base_url, auth, headers


def _make_vmdr_request(url: str, auth: HTTPBasicAuth, headers: dict, params: dict, timeout: int = 120) -> str:
    """
    Make a POST request to Qualys VMDR API and return response text

    :param str url: API endpoint URL
    :param HTTPBasicAuth auth: Authentication object
    :param dict headers: HTTP headers
    :param dict params: Request parameters
    :param int timeout: Request timeout in seconds
    :return: Response text
    :rtype: str
    """
    from . import QUALYS_API

    response = QUALYS_API.post(url=url, auth=auth, headers=headers, data=params, timeout=timeout)

    if not response.ok:
        logger.error("VMDR API request failed: HTTP %s", response.status_code)
        logger.error(RESPONSE_LOG_FORMAT, response.text[:500])
        raise RequestException(f"VMDR API request failed with status {response.status_code}")

    return response.text


def _extract_host_info(host: ET.Element) -> Dict:
    """
    Extract host information from XML element

    :param ET.Element host: Host XML element
    :return: Dictionary of host information
    :rtype: Dict
    """
    host_id = host.find("ID")
    host_ip = host.find("IP")
    host_os = host.find("OS")
    host_dns = host.find("DNS")
    host_netbios = host.find("NETBIOS")
    host_fqdn_elem = host.find(".//FQDN")

    return {
        "host_id": host_id.text if host_id is not None else "",
        "host_ip": host_ip.text if host_ip is not None else "",
        "host_os": host_os.text if host_os is not None else "",
        "host_dns": host_dns.text if host_dns is not None else "",
        "host_netbios": host_netbios.text if host_netbios is not None else "",
        "host_fqdn": host_fqdn_elem.text if host_fqdn_elem is not None else "",
    }


def _extract_text_or_empty(element: ET.Element, tag: str) -> str:
    """
    Extract text from XML element or return empty string

    :param ET.Element element: Parent XML element
    :param str tag: Tag name to find
    :return: Text content or empty string
    :rtype: str
    """
    found = element.find(tag)
    return found.text if found is not None else ""


def _parse_detection_element(detection: ET.Element, host_info: Dict) -> Dict:
    """
    Parse single detection XML element into dictionary

    :param ET.Element detection: Detection XML element
    :param Dict host_info: Host information dictionary
    :return: Detection record dictionary
    :rtype: Dict
    """
    qid = _extract_text_or_empty(detection, "QID")

    return {
        **host_info,
        "qid": qid,
        "type": _extract_text_or_empty(detection, "TYPE"),
        "severity": _extract_text_or_empty(detection, "SEVERITY"),
        "port": _extract_text_or_empty(detection, "PORT"),
        "protocol": _extract_text_or_empty(detection, "PROTOCOL"),
        "ssl": _extract_text_or_empty(detection, "SSL"),
        "results": _extract_text_or_empty(detection, "RESULTS"),
        "status": _extract_text_or_empty(detection, "STATUS"),
        "first_found": _extract_text_or_empty(detection, "FIRST_FOUND_DATETIME"),
        "last_found": _extract_text_or_empty(detection, "LAST_FOUND_DATETIME"),
        "times_found": _extract_text_or_empty(detection, "TIMES_FOUND"),
    }


def _process_host_detections(host: ET.Element, detections: List[Dict], unique_qids: Set[str]) -> None:
    """
    Process all detections for a single host

    :param ET.Element host: Host XML element
    :param List[Dict] detections: List to append detections to
    :param Set[str] unique_qids: Set to add QIDs to
    """
    host_info = _extract_host_info(host)
    detection_list = host.findall(".//DETECTION")

    for detection in detection_list:
        qid_elem = detection.find("QID")
        if qid_elem is None:
            continue

        qid = qid_elem.text
        unique_qids.add(qid)

        det_record = _parse_detection_element(detection, host_info)
        detections.append(det_record)


def fetch_vm_detections(truncation_limit: int = 1000, status: str = "Active,New") -> tuple[List[Dict], Set[str]]:
    """
    Fetch vulnerability detections from Qualys VMDR API

    :param int truncation_limit: Maximum number of records to fetch, defaults to 1000
    :param str status: Detection status filter (e.g., "Active,New"), defaults to "Active,New"
    :return: Tuple of (detection records, unique QIDs)
    :rtype: tuple[List[Dict], Set[str]]
    """
    base_url, auth, headers = auth_vmdr_api()
    detection_url = urljoin(base_url, "/api/2.0/fo/asset/host/vm/detection/")

    params = {
        "action": "list",
        "truncation_limit": str(truncation_limit),
        "show_results": "1",
        "status": status,
    }

    logger.info("Fetching VM detections from Qualys (limit: %s, status: %s)", truncation_limit, status)

    response_text = _make_vmdr_request(detection_url, auth, headers, params, timeout=180)

    # Parse XML response
    root = ET.fromstring(response_text)
    hosts = root.findall(".//HOST")

    detections = []
    unique_qids = set()

    for host in hosts:
        _process_host_detections(host, detections, unique_qids)

    logger.info(
        "Fetched %s detections from %s hosts with %s unique QIDs", len(detections), len(hosts), len(unique_qids)
    )
    return detections, unique_qids


def _extract_cve_ids(cve_list_elem: Optional[ET.Element]) -> List[str]:
    """
    Extract CVE IDs from CVE_LIST XML element

    :param Optional[ET.Element] cve_list_elem: CVE_LIST XML element
    :return: List of CVE IDs
    :rtype: List[str]
    """
    if cve_list_elem is None:
        return []

    cve_items = cve_list_elem.findall("CVE")
    return [cve.find("ID").text for cve in cve_items if cve.find("ID") is not None]


def _parse_kb_vuln_element(vuln: ET.Element) -> Optional[tuple[str, Dict]]:
    """
    Parse KB vulnerability XML element into dictionary

    :param ET.Element vuln: VULN XML element from Knowledge Base
    :return: Tuple of (QID, KB entry dict) or None if no QID
    :rtype: Optional[tuple[str, Dict]]
    """
    qid_elem = vuln.find("QID")
    if qid_elem is None:
        return None

    qid = qid_elem.text
    cve_list_elem = vuln.find("CVE_LIST")
    cve_ids = _extract_cve_ids(cve_list_elem)

    kb_entry = {
        "qid": qid,
        "title": _extract_text_or_empty(vuln, "TITLE"),
        "severity": _extract_text_or_empty(vuln, "SEVERITY_LEVEL"),
        "solution": _extract_text_or_empty(vuln, "SOLUTION"),
        "threat": _extract_text_or_empty(vuln, "THREAT"),
        "impact": _extract_text_or_empty(vuln, "IMPACT"),
        "exploitability": _extract_text_or_empty(vuln, "EXPLOITABILITY"),
        "cve_ids": cve_ids,
        "cvss_base": _extract_text_or_empty(vuln, ".//CVSS_BASE"),
        "cvss3_base": _extract_text_or_empty(vuln, ".//CVSS3_BASE"),
    }

    return qid, kb_entry


def fetch_kb_data(qids: Set[str]) -> Dict[str, Dict]:
    """
    Fetch vulnerability details from Qualys Knowledge Base for given QIDs

    :param Set[str] qids: Set of Qualys IDs to fetch
    :return: Dictionary mapping QID to vulnerability details
    :rtype: Dict[str, Dict]
    """
    if not qids:
        logger.warning("No QIDs provided for KB lookup")
        return {}

    base_url, auth, headers = auth_vmdr_api()
    kb_url = urljoin(base_url, "/api/2.0/fo/knowledge_base/vuln/")

    # Batch query all QIDs at once (API supports comma-separated list)
    qid_list = ",".join(sorted(qids))

    params = {
        "action": "list",
        "ids": qid_list,
        "details": "All",  # Get all vulnerability details
    }

    logger.info("Querying Knowledge Base for %s QIDs", len(qids))

    response_text = _make_vmdr_request(kb_url, auth, headers, params, timeout=180)

    # Parse KB response
    root = ET.fromstring(response_text)
    vulns = root.findall(".//VULN")

    kb_data = {}
    for vuln in vulns:
        result = _parse_kb_vuln_element(vuln)
        if result:
            qid, kb_entry = result
            kb_data[qid] = kb_entry

    logger.info("Retrieved KB data for %s vulnerabilities", len(kb_data))
    return kb_data


def create_enriched_vm_scan_csv(detections: List[Dict], kb_data: Dict[str, Dict], output_path: str) -> str:
    """
    Create enriched CSV file combining detection and KB data for import_scans

    :param List[Dict] detections: Detection records from fetch_vm_detections
    :param Dict[str, Dict] kb_data: KB data from fetch_kb_data
    :param str output_path: Output file path
    :return: Path to created CSV file
    :rtype: str
    """
    logger.info("Creating enriched VM scan CSV with %s detections", len(detections))

    # Define CSV headers (required by import_scans)
    fieldnames = [
        "Severity",
        "Title",
        "Exploitability",
        "CVE ID",
        "Solution",
        "DNS",
        "IP",
        "QG Host ID",
        "OS",
        "NetBIOS",
        "FQDN",
        "QID",
        "Threat",
        "First Detected",
        "Last Detected",
        "Port",
        "Protocol",
        "Results",
        "CVSS Base",
        "CVSS3.1 Base",
    ]

    enriched_records = []

    for detection in detections:
        qid = detection["qid"]

        # Get KB data for this QID
        kb = kb_data.get(qid, {})

        # Create enriched record with all required fields
        enriched = {
            # Required headers from KB
            "Severity": kb.get("severity", ""),
            "Title": kb.get("title", ""),
            "Exploitability": kb.get("exploitability", ""),
            "CVE ID": ", ".join(kb.get("cve_ids", [])),
            "Solution": kb.get("solution", ""),
            "Threat": kb.get("threat", ""),
            "CVSS Base": kb.get("cvss_base", ""),
            "CVSS3.1 Base": kb.get("cvss3_base", ""),
            # Required headers from detection
            "DNS": detection.get("host_dns", ""),
            "IP": detection.get("host_ip", ""),
            "QG Host ID": detection.get("host_id", ""),
            "OS": detection.get("host_os", ""),
            "NetBIOS": detection.get("host_netbios", ""),
            "FQDN": detection.get("host_fqdn", ""),
            "QID": qid,
            "First Detected": detection.get("first_found", ""),
            "Last Detected": detection.get("last_found", ""),
            "Port": detection.get("port", ""),
            "Protocol": detection.get("protocol", ""),
            "Results": detection.get("results", ""),
        }

        enriched_records.append(enriched)

    # Write CSV file
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_records)

    logger.info("Created enriched CSV: %s (%s records)", output_path, len(enriched_records))
    return output_path


def fetch_latest_vm_scan(output_dir: str = ".", filename_prefix: str = "VM_Scan") -> Optional[str]:
    """
    Fetch the latest VM vulnerability scan data from Qualys VMDR API

    This function combines detection list and Knowledge Base data to create
    a CSV file compatible with the import_scans command.

    :param str output_dir: Directory to save the CSV file, defaults to current directory
    :param str filename_prefix: Prefix for the output filename, defaults to "VM_Scan"
    :return: Path to the created CSV file, or None if failed
    :rtype: Optional[str]
    """
    try:
        logger.info("Fetching latest VM scan data from Qualys VMDR API")

        # Step 1: Fetch detections
        detections, unique_qids = fetch_vm_detections()

        if not detections:
            logger.warning("No vulnerability detections found")
            return None

        # Step 2: Fetch KB data for all unique QIDs
        kb_data = fetch_kb_data(unique_qids)

        if not kb_data:
            logger.warning("No Knowledge Base data retrieved")
            return None

        # Step 3: Create enriched CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{filename_prefix}_{timestamp}.csv"
        output_path = os.path.join(output_dir, output_filename)

        csv_path = create_enriched_vm_scan_csv(detections, kb_data, output_path)

        logger.info("Successfully created VM scan CSV: %s", csv_path)
        return csv_path

    except Exception as e:
        logger.error("Failed to fetch VM scan data: %s", str(e))
        import traceback

        traceback.print_exc()
        return None


# ==================================================================================
# VMDR OT API v1.0 - New REST API for Vulnerability Detection
# ==================================================================================


def auth_vmdr_ot_api() -> tuple[str, str, dict]:
    """
    Authenticate with Qualys VMDR OT API v1.0 using JWT authentication

    :return: Tuple of (base_url, jwt_token, headers)
    :rtype: tuple[str, str, dict]
    """
    from .containers import auth_cs_api  # noqa: C0415

    # VMDR OT API uses JWT authentication (same as Container Security)
    # Use the same auth mechanism
    base_url, headers = auth_cs_api()

    # Extract JWT token from Authorization header
    jwt_token = headers.get("Authorization", "").replace("Bearer ", "")

    if not jwt_token:
        raise ValueError("Failed to obtain JWT token for VMDR OT API authentication")

    logger.info("Authenticated with Qualys VMDR OT API v1.0")
    return base_url, jwt_token, headers


def _handle_ot_api_error(response: requests.Response) -> None:
    """
    Handle VMDR OT API error responses with appropriate logging

    :param requests.Response response: Failed HTTP response
    """
    logger.error("VMDR OT API request failed: HTTP %s", response.status_code)
    logger.error(RESPONSE_LOG_FORMAT, response.text[:500])

    if response.status_code == 401:
        logger.error("VMDR OT API - Authentication FAILED (401 Unauthorized)")
        logger.error("  Verify JWT token is valid and has VMDR OT API permissions")
    elif response.status_code == 404:
        logger.error("VMDR OT API - Endpoint not found (404)")
        logger.error("  Verify VMDR OT module is enabled in your Qualys account")
        logger.error("  Contact Qualys support if VMDR OT is not available")


def _fetch_ot_page(ot_url: str, headers: dict, page: int, limit: int, filters: Optional[Dict]) -> Optional[List[Dict]]:
    """
    Fetch single page of OT vulnerabilities

    :param str ot_url: OT API endpoint URL
    :param dict headers: Request headers
    :param int page: Page number
    :param int limit: Records per page
    :param Optional[Dict] filters: Additional filters
    :return: List of detections or None on error
    :rtype: Optional[List[Dict]]
    """
    try:
        params = {"limit": limit, "page": page}
        if filters:
            params.update(filters)

        response = requests.get(url=ot_url, headers=headers, params=params, timeout=120)

        if not response.ok:
            _handle_ot_api_error(response)
            return None

        response_data = response.json()
        detections = response_data if isinstance(response_data, list) else response_data.get("data", [])

        return detections if detections else None

    except requests.RequestException as e:
        logger.error("Failed to fetch VMDR OT vulnerabilities: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error fetching VMDR OT vulnerabilities: %s", e)
        import traceback

        logger.debug(traceback.format_exc())
        return None


def fetch_ot_vulnerabilities(
    sort_field: str = "vulnerabilities.lastDetected",
    sort_order: str = "asc",
    limit: int = 100,
    filters: Optional[Dict] = None,
) -> List[Dict]:
    """
    Fetch vulnerabilities from Qualys VMDR OT API v1.0 using the /ot/1.0/detection/list endpoint

    This function fetches vulnerabilities detected on OT/IoT assets, matching them to
    assets using the qid field in the response. Follows Sample 1 Vulnerabilities Last Detected format.

    API Reference: https://docs.qualys.com/en/vmdr-ot/api/vmdrot_api/ch03/list_vulnerability.htm#1.0_API

    :param str sort_field: Field to sort by (default: "vulnerabilities.lastDetected")
    :param str sort_order: Sort order - "asc" or "desc" (default: "asc")
    :param int limit: Number of records per page (default: 100)
    :param Optional[Dict] filters: Additional filters to apply to the query
    :return: List of vulnerability detections with asset information
    :rtype: List[Dict]
    """
    base_url, _, headers = auth_vmdr_ot_api()
    sort_param = f'[{{"{sort_field}":"{sort_order}"}}]'
    ot_url = urljoin(base_url, f"/ot/1.0/detection/list?sort={sort_param}")

    logger.info("Fetching OT vulnerabilities from Qualys VMDR OT API v1.0")
    logger.debug("OT API URL: %s", ot_url)

    all_detections = []
    page = 1

    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

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
        task = progress.add_task("[green]Fetching VMDR OT vulnerabilities...", total=None)

        while True:
            detections = _fetch_ot_page(ot_url, headers, page, limit, filters)

            if detections is None:
                break

            all_detections.extend(detections)

            progress.update(
                task,
                description=f"[green]Fetching VMDR OT vulnerabilities... (Page {page}, Total: {len(all_detections)})",
            )

            logger.debug(
                "Fetched page %s: %s detections (Total so far: %s)", page, len(detections), len(all_detections)
            )

            if len(detections) < limit:
                break

            page += 1

        progress.update(task, total=len(all_detections), completed=len(all_detections))

    logger.info("Fetched %s total OT vulnerability detections", len(all_detections))
    return all_detections


def convert_ot_detections_to_issues(ot_detections: List[Dict]) -> List[Dict]:
    """
    Convert VMDR OT API vulnerability detections to RegScale issue format

    This function transforms OT vulnerability detection data into a format
    compatible with RegScale issue creation, matching vulnerabilities to assets
    using the qid field.

    :param List[Dict] ot_detections: OT vulnerability detections from fetch_ot_vulnerabilities
    :return: List of issues in RegScale format
    :rtype: List[Dict]
    """
    issues = []

    for detection in ot_detections:
        # Extract asset information
        asset_info = detection.get("asset", {})
        asset_id = asset_info.get("assetId", "")
        asset_name = asset_info.get("name", "Unknown Asset")
        asset_ip = asset_info.get("ipAddress", "")

        # Extract vulnerability information
        vulnerabilities = detection.get("vulnerabilities", [])

        for vuln in vulnerabilities:
            qid = vuln.get("qid", "")
            title = vuln.get("title", "")
            severity = vuln.get("severity", "")
            cvss_base = vuln.get("cvssBase", "")
            cvss3_base = vuln.get("cvss3Base", "")
            first_detected = vuln.get("firstDetected", "")
            last_detected = vuln.get("lastDetected", "")
            status = vuln.get("status", "Active")
            cve_ids = vuln.get("cveIds", [])
            solution = vuln.get("solution", "")
            threat = vuln.get("threat", "")
            impact = vuln.get("impact", "")

            # Create issue in RegScale format
            issue = {
                "title": f"{title} (QID: {qid})",
                "description": f"Vulnerability detected on {asset_name} ({asset_ip})\n\n"
                f"**Asset ID**: {asset_id}\n"
                f"**QID**: {qid}\n"
                f"**Severity**: {severity}\n"
                f"**Status**: {status}\n"
                f"**First Detected**: {first_detected}\n"
                f"**Last Detected**: {last_detected}\n\n"
                f"**Threat**: {threat}\n\n"
                f"**Impact**: {impact}\n\n"
                f"**Solution**: {solution}",
                "severityLevel": _map_severity_to_regscale(severity),
                "qid": qid,
                "asset_id": asset_id,
                "asset_name": asset_name,
                "asset_ip": asset_ip,
                "cvss_base": cvss_base,
                "cvss3_base": cvss3_base,
                "cve_ids": cve_ids,
                "first_detected": first_detected,
                "last_detected": last_detected,
                "status": status,
                "source": "Qualys VMDR OT",
            }

            issues.append(issue)

    logger.info("Converted %s OT detections to %s RegScale issues", len(ot_detections), len(issues))
    return issues


def _map_severity_to_regscale(severity: str) -> str:
    """
    Map Qualys severity levels to RegScale severity levels

    :param str severity: Qualys severity (1-5 or text)
    :return: RegScale severity level
    :rtype: str
    """
    severity_map = {
        "5": "Critical",
        "4": "High",
        "3": "Medium",
        "2": "Low",
        "1": "Low",
        "CRITICAL": "Critical",
        "HIGH": "High",
        "MEDIUM": "Medium",
        "LOW": "Low",
        "INFO": "Low",
    }

    severity_str = str(severity).upper()
    return severity_map.get(severity_str, "Medium")  # Default to Medium if unknown


# ==================================================================================
# VMDR Scan Listing Functions
# ==================================================================================


def _parse_xml_to_json(xml_text: str) -> dict:
    """
    Parse XML response to dictionary (fallback for non-JSON responses).

    :param str xml_text: XML response text
    :return: Parsed dictionary
    :rtype: dict
    """
    import xmltodict

    return xmltodict.parse(xml_text)


def _vmdr_report_to_summary(report: dict) -> Optional[ScanSummary]:
    """
    Convert VMDR report dict to ScanSummary.

    :param dict report: Raw VMDR report data
    :return: Normalized scan summary or None
    :rtype: Optional[ScanSummary]
    """
    try:
        scan_id = report.get("ID", "")
        title = report.get("TITLE", f"VMDR Scan {scan_id}")
        status_obj = report.get("STATUS", {})
        status = status_obj.get("STATE", "Unknown") if isinstance(status_obj, dict) else str(status_obj)

        # Parse scan date
        launch_date_str = report.get("LAUNCH_DATETIME", "")
        scan_date = None
        if launch_date_str:
            try:
                scan_date = datetime.strptime(launch_date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                logger.debug("Could not parse date: %s", launch_date_str)

        # Extract target count
        asset_group = report.get("ASSET_GROUP_TITLE_LIST", {})
        target_count = int(asset_group.get("count", 0)) if isinstance(asset_group, dict) else 0

        return ScanSummary(
            scan_id=scan_id,
            scan_type="VMDR",
            title=title,
            status=status,
            scan_date=scan_date,
            target_count=target_count,
            vuln_count=None,  # Not in report list API
            duration=None,
            module="vmdr",
        )
    except Exception as e:
        logger.warning("Failed to parse VMDR report: %s", e)
        return None


def list_vmdr_reports(days: int) -> List[ScanSummary]:
    """
    List VMDR scan reports from the last N days.

    Queries the Qualys VMDR API /api/2.0/fo/report/ endpoint to retrieve
    scan report metadata. Only returns reports launched after the specified
    date threshold.

    :param int days: Number of days to look back for reports
    :return: List of scan summaries, sorted by date (newest first)
    :rtype: List[ScanSummary]

    Example:
        >>> reports = list_vmdr_reports(7)
        >>> print(f"Found {len(reports)} reports")
        Found 15 reports
    """
    logger.info("Fetching VMDR reports from last %s days", days)

    try:
        # Use existing auth function
        base_url, auth, headers = auth_vmdr_api()

        # Calculate date filter
        scan_date_since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # API endpoint: /api/2.0/fo/report/?action=list
        url = urljoin(base_url, "/api/2.0/fo/report/")
        params = {"action": "list", "launched_after_datetime": scan_date_since, "output_format": "json"}

        response = requests.get(url=url, auth=auth, headers=headers, params=params, timeout=120)

        if not response.ok:
            logger.error("VMDR API request failed: HTTP %s", response.status_code)
            logger.error(RESPONSE_LOG_FORMAT, response.text[:500])
            return []

        # Parse response - try JSON first, fallback to XML
        try:
            data = response.json()
        except ValueError:
            # Fallback to XML parsing
            data = _parse_xml_to_json(response.text)

        # Extract reports from response
        report_list = data.get("REPORT_LIST_OUTPUT", {}).get("RESPONSE", {}).get("REPORT_LIST", {})
        reports = report_list.get("REPORT", [])

        # Normalize to list
        if not isinstance(reports, list):
            reports = [reports] if reports else []

        # Convert to ScanSummary objects
        scan_summaries = []
        for report in reports:
            summary = _vmdr_report_to_summary(report)
            if summary:
                scan_summaries.append(summary)

        # Sort by date (newest first)
        scan_summaries.sort(key=lambda s: s.scan_date or datetime.min, reverse=True)

        logger.info("Retrieved %s VMDR reports", len(scan_summaries))
        return scan_summaries

    except requests.RequestException as e:
        logger.error("VMDR API request failed: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error fetching VMDR reports: %s", e)
        logger.debug(traceback.format_exc())
        return []
