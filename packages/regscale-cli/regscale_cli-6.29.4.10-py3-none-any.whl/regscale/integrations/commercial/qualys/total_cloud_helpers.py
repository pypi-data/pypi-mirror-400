"""
Total Cloud helper functions for Qualys integration.

This module contains helper functions for processing Total Cloud data
(VM/host detections and container vulnerabilities) and converting it to RegScale format.
"""

import logging
import traceback
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from dateutil.parser import ParserError, parse
from datetime import datetime, timezone

from regscale.integrations.variables import ScannerVariables

logger = logging.getLogger("regscale")

# Import datetime format constant from parent module
QUALYS_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# Qualys API returns dates in this format
QUALYS_API_DATETIME_FORMAT = "%m/%d/%Y %H:%M"
# Log message for VMDR fallback
VMDR_FALLBACK_MESSAGE = "Total Cloud: Triggering automatic fallback to VMDR"


def _normalize_qualys_datetime(datetime_str: str) -> str:
    """
    Convert Qualys API datetime format to ISO format expected by RegScale.

    Args:
        datetime_str: Datetime string from Qualys API (e.g., "12/14/2025 10:09")

    Returns:
        ISO format datetime string (e.g., "2025-12-14T10:09:00Z")

    Example:
        >>> _normalize_qualys_datetime("12/14/2025 10:09")
        "2025-12-14T10:09:00Z"
    """
    if not datetime_str:
        return ""

    try:
        # Parse Qualys format: MM/DD/YYYY HH:MM
        dt = datetime.strptime(datetime_str, QUALYS_API_DATETIME_FORMAT)
        # Convert to ISO format with UTC timezone
        return dt.strftime(QUALYS_DATETIME_FORMAT)
    except ValueError as ex:
        logger.warning("Failed to parse datetime '%s': %s", datetime_str, ex)
        return datetime_str  # Return original if parsing fails


def fetch_total_cloud_data(include_tags: Optional[str] = None, exclude_tags: Optional[str] = None) -> Optional[Dict]:
    """
    Fetch VM detection data from Total Cloud API with automatic fallback trigger.

    This function wraps the existing _fetch_qualys_api_data() with fallback logic.
    Returns None on failure to trigger automatic VMDR fallback.

    :param include_tags: Comma-separated tag names or IDs to include
    :param exclude_tags: Comma-separated tag names or IDs to exclude
    :return: Parsed XML data dictionary or None if request failed
    """
    from regscale.integrations.commercial.qualys import _fetch_qualys_api_data
    from regscale.integrations.commercial.qualys.qualys_error_handler import QualysErrorHandler

    logger.info("Total Cloud: Fetching VM detection data from Total Cloud API...")

    try:
        xml_data = _fetch_qualys_api_data(include_tags, exclude_tags)

        if not xml_data:
            logger.warning("Total Cloud: API returned no data")
            logger.info(VMDR_FALLBACK_MESSAGE)
            return None

        # Log host count for debugging
        if "HOST_LIST_VM_DETECTION_OUTPUT" in xml_data:
            response = xml_data["HOST_LIST_VM_DETECTION_OUTPUT"].get("RESPONSE", {})
            host_list = response.get("HOST_LIST", {})
            hosts = host_list.get("HOST", [])
            if not isinstance(hosts, list):
                hosts = [hosts] if hosts else []
            logger.debug("Total Cloud: Retrieved %d hosts from API", len(hosts))

        # Check for Qualys errors
        error_details = QualysErrorHandler.extract_error_details(xml_data)
        if error_details.get("has_error"):
            logger.error("Total Cloud: API returned error response")
            QualysErrorHandler.log_error_details(error_details)
            logger.info(VMDR_FALLBACK_MESSAGE)
            return None

        logger.info("Total Cloud: VM detection data fetched successfully")
        return xml_data

    except Exception as e:
        logger.error("Total Cloud: API request failed: %s", e)
        logger.debug(traceback.format_exc())
        logger.info(VMDR_FALLBACK_MESSAGE)
        return None


def fetch_total_cloud_containers(include_tags: Optional[str] = None, exclude_tags: Optional[str] = None) -> List[Dict]:
    """
    Fetch container vulnerability data from Qualys Container Security API.

    This function wraps the existing fetch_all_vulnerabilities() from containers module.
    Returns empty list on failure (non-fatal).

    :param include_tags: Comma-separated tag names or IDs to include
    :param exclude_tags: Comma-separated tag names or IDs to exclude
    :return: List of container vulnerability dictionaries
    """
    from regscale.integrations.commercial.qualys import _prepare_qualys_params
    from regscale.integrations.commercial.qualys.containers import fetch_all_vulnerabilities

    logger.info("Total Cloud: Fetching container vulnerability data...")

    try:
        params = _prepare_qualys_params(include_tags, exclude_tags)
        containers = fetch_all_vulnerabilities(filters=params)
        logger.info("Total Cloud: Fetched %s container vulnerabilities", len(containers))
        return containers

    except Exception as e:
        logger.error("Total Cloud: Container fetch failed: %s", e)
        logger.debug(traceback.format_exc())
        logger.warning("Total Cloud: Continuing without container data")
        return []


def validate_total_cloud_data(xml_data: Optional[Dict], containers: List[Dict]) -> bool:
    """
    Validate Total Cloud data structure before processing.

    Checks:
    - XML data exists and is a dictionary
    - Contains HOST_LIST_VM_DETECTION_OUTPUT structure
    - Has at least one host OR container data
    - Containers is a list type

    :param xml_data: Parsed XML data from Total Cloud API
    :param containers: List of container vulnerability dictionaries
    :return: True if data is valid, False otherwise
    """
    logger.debug("Total Cloud: Validating data structure...")

    # Check XML data
    if not xml_data or not isinstance(xml_data, dict):
        logger.error("Total Cloud: XML data is missing or not a dictionary")
        return False

    if "HOST_LIST_VM_DETECTION_OUTPUT" not in xml_data:
        logger.error("Total Cloud: XML data missing HOST_LIST_VM_DETECTION_OUTPUT structure")
        return False

    # Check for at least one data source
    response = xml_data.get("HOST_LIST_VM_DETECTION_OUTPUT", {}).get("RESPONSE", {})
    host_list = response.get("HOST_LIST", {})
    hosts = host_list.get("HOST", [])

    # Normalize to list
    if not isinstance(hosts, list):
        hosts = [hosts] if hosts else []

    has_hosts = len(hosts) > 0
    has_containers = isinstance(containers, list) and len(containers) > 0

    if not has_hosts and not has_containers:
        logger.warning("Total Cloud: No hosts or containers found in data")
        return False

    logger.info("Total Cloud: Data validation passed (Hosts: %s, Containers: %s)", len(hosts), len(containers))
    return True


def extract_total_cloud_assets(xml_data: Dict, containers: List[Dict]) -> List[Dict]:
    """
    Extract and normalize all assets from Total Cloud data (VMs + containers).

    Combines:
    - VM/host assets from XML HOST_LIST
    - Container assets from container vulnerability data

    All assets normalized to VMDR format with TRACKING_METHOD field.

    :param xml_data: Parsed XML data from Total Cloud API
    :param containers: List of container vulnerability dictionaries
    :return: List of asset dictionaries in VMDR format
    """
    logger.info("Total Cloud: Extracting assets from Total Cloud data...")
    all_assets = []

    # Extract VM assets
    vm_assets = _extract_vm_assets_from_tc(xml_data)
    logger.info("Total Cloud: Extracted %s VM/host assets", len(vm_assets))
    all_assets.extend(vm_assets)

    # Extract container assets
    container_assets = _extract_container_assets_from_tc(containers)
    logger.info("Total Cloud: Extracted %s container assets", len(container_assets))
    all_assets.extend(container_assets)

    logger.info("Total Cloud: Total assets extracted: %s", len(all_assets))
    return all_assets

    # Extract container assets
    container_assets = _extract_container_assets_from_tc(containers)
    logger.info("Total Cloud: Extracted %s container assets", len(container_assets))
    all_assets.extend(container_assets)


def _extract_vm_assets_from_tc(xml_data: Dict) -> List[Dict]:
    """
    Extract VM/host assets from Total Cloud XML data.

    Converts HOST elements to VMDR asset format with TRACKING_METHOD='TOTALCLOUD'.

    :param xml_data: Parsed XML data from Total Cloud API
    :return: List of VM asset dictionaries in VMDR format
    """
    vm_assets = []

    try:
        response = xml_data.get("HOST_LIST_VM_DETECTION_OUTPUT", {}).get("RESPONSE", {})
        host_list = response.get("HOST_LIST", {})
        hosts = host_list.get("HOST", [])

        # Normalize to list
        if not isinstance(hosts, list):
            hosts = [hosts] if hosts else []

        logger.info("Total Cloud: Processing %s hosts from XML data", len(hosts))

        for i, host in enumerate(hosts, 1):
            try:
                asset = _normalize_tc_asset_to_vmdr(host, "TOTALCLOUD")
                if asset:
                    vm_assets.append(asset)
            except Exception as e:
                logger.warning("Total Cloud: Failed to parse host %s/%s: %s", i, len(hosts), e)
                continue

        logger.debug("Total Cloud: Successfully parsed %s VM assets", len(vm_assets))

    except Exception as e:
        logger.error("Total Cloud: Error extracting VM assets: %s", e)
        logger.debug(traceback.format_exc())

    return vm_assets


def _convert_container_vulns_to_detections(vulnerabilities: List[Dict]) -> List[Dict]:
    """
    Convert container vulnerabilities to VMDR DETECTION format.

    :param vulnerabilities: List of container vulnerability dictionaries
    :return: List of DETECTION dictionaries in VMDR format
    """
    detections = []
    for vuln in vulnerabilities:
        qid = vuln.get("qid") or vuln.get("vulnerabilityId", "")
        if not qid:
            continue

        # Convert timestamps using container helper
        from regscale.integrations.commercial.qualys import _convert_container_timestamp

        # Map container vulnerability to VMDR DETECTION format
        detection = {
            "QID": str(qid),
            "TYPE": vuln.get("typeDetected", "Confirmed"),
            "SEVERITY": str(vuln.get("severity", 3)),
            "STATUS": "Active",
            "FIRST_FOUND_DATETIME": _convert_container_timestamp(vuln.get("firstFound") or vuln.get("publishedDate")),
            "LAST_FOUND_DATETIME": _convert_container_timestamp(vuln.get("lastFound") or vuln.get("publishedDate")),
            "RESULTS": vuln.get("result", vuln.get("description", "")),
        }
        detections.append(detection)

    return detections


def _extract_container_assets_from_tc(containers: List[Dict]) -> List[Dict]:
    """
    Extract container assets from container vulnerability data.

    Converts container data to VMDR asset format with TRACKING_METHOD='CONTAINER'
    and populates DETECTIONS field with vulnerability data.

    Note: Total Cloud uses DETECTIONS (not DETECTION_LIST.DETECTION) for vulnerability data.

    :param containers: List of container vulnerability dictionaries
    :return: List of container asset dictionaries in VMDR format with DETECTIONS populated
    """
    container_assets = []
    seen_container_ids = set()

    logger.debug("Total Cloud: Processing %s containers", len(containers))

    for i, container in enumerate(containers, 1):
        try:
            container_id = container.get("containerId", "")
            if not container_id:
                logger.warning("Total Cloud: Skipping container %s/%s with missing containerId", i, len(containers))
                continue

            if container_id in seen_container_ids:
                logger.debug("Total Cloud: Duplicate containerId '%s', skipping", container_id)
                continue

            seen_container_ids.add(container_id)

            # Extract container metadata
            image_id = container.get("imageId", "")
            image_name = container.get("imageName", "Unknown Container")
            registry = container.get("registry", "")

            # Convert container vulnerabilities to DETECTIONS format
            vulnerabilities = container.get("vulnerabilities", [])
            detections = _convert_container_vulns_to_detections(vulnerabilities)

            # Normalize container to VMDR format with DETECTIONS populated
            asset = {
                "ASSET_ID": container_id,
                "IP": "Container",  # Placeholder for container
                "DNS": image_name,
                "OS": f"Container: {registry}" if registry else "Container",
                "TRACKING_METHOD": "CONTAINER",
                "CONTAINER_ID": container_id,
                "IMAGE_ID": image_id,
                "IMAGE_NAME": image_name,
                "DETECTIONS": detections,  # Total Cloud uses DETECTIONS, not DETECTION_LIST
            }

            container_assets.append(asset)

        except Exception as e:
            logger.warning("Total Cloud: Failed to parse container %s/%s: %s", i, len(containers), e)
            continue

    logger.debug(
        "Total Cloud: Successfully parsed %s container assets with %s total detections",
        len(container_assets),
        sum(len(asset.get("DETECTIONS", [])) for asset in container_assets),
    )
    return container_assets


def _normalize_tc_asset_to_vmdr(host_data: Dict, tracking_method: str) -> Optional[Dict]:
    """
    Normalize a single Total Cloud host to VMDR asset format.

    Adds TRACKING_METHOD field to distinguish data source.

    :param host_data: Host dictionary from Total Cloud XML
    :param tracking_method: Tracking method identifier (e.g., 'TOTALCLOUD')
    :return: Asset dictionary in VMDR format or None if parsing fails
    """
    try:
        asset_id = host_data.get("ID", "")
        if not asset_id:
            logger.warning("Total Cloud: Host missing ID, skipping")
            return None

        # Extract basic host info
        ip = host_data.get("IP", "")
        dns = host_data.get("DNS", "")
        operating_system = host_data.get("OS", "")
        last_vuln_scan = host_data.get("LAST_VULN_SCAN_DATETIME", "")

        # Create VMDR-normalized asset
        asset = {
            "ASSET_ID": asset_id,
            "IP": ip,
            "DNS": dns,
            "OS": operating_system,
            "TRACKING_METHOD": tracking_method,
            "LAST_SCAN": last_vuln_scan,
        }

        # Add optional fields if present
        if "NETBIOS" in host_data:
            asset["NETBIOS"] = host_data["NETBIOS"]

        # Preserve DETECTION_LIST for issue processing
        if "DETECTION_LIST" in host_data:
            detection_list = host_data["DETECTION_LIST"]
            if detection_list and "DETECTION" in detection_list:
                asset["DETECTIONS"] = detection_list["DETECTION"]

        return asset

    except Exception as e:
        logger.warning("Total Cloud: Error normalizing host data: %s", e)
        return None


def convert_total_cloud_to_issues(assets_with_detections: List[Dict]) -> List[Dict]:
    """
    Convert Total Cloud detection data to RegScale issue format.

    Processes all detections from assets and normalizes to VMDR issue format.
    Groups issues by asset (matching qualys_assets_and_issues format).
    Mode-aware: Uses issueCreation setting to determine PLUGIN_ID format.

    Output format (matching WAS pattern):
    [{
        "ASSET_ID": "12345",
        "IP": "192.168.1.100",
        "DNS": "server.example.com",
        "OS": "Linux",
        "TRACKING_METHOD": "TOTALCLOUD",
        "ISSUES": {
            "CVE_2021_1234": {
                "QID": "45839",
                "SEVERITY": 5,
                "ISSUE_DATA": {...}
            }
        }
    }]

    :param assets_with_detections: List of assets with detection data
    :return: List of asset dictionaries with ISSUES grouped by QUALYS_ID
    """
    logger.info("Total Cloud: Converting detections to issues...")
    assets_with_issues = []
    detection_count = 0

    for asset in assets_with_detections:
        asset_id = asset.get("ASSET_ID", "")
        tracking_method = asset.get("TRACKING_METHOD", "TOTALCLOUD")

        # Get detections from asset
        detections = asset.get("DETECTIONS", [])
        if not detections:
            continue

        # Normalize to list
        if not isinstance(detections, list):
            detections = [detections] if detections else []

        detection_count += len(detections)

        # Process all detections for this asset
        issues_dict = {}
        for detection in detections:
            issue = _process_tc_detection(detection, asset_id, tracking_method)
            if issue:
                # Extract QUALYS_ID as the key
                qualys_id = issue.get("QUALYS_ID", f"QID_{issue.get('QID', 'unknown')}")
                issues_dict[qualys_id] = issue

        # Only add asset if it has issues
        if issues_dict:
            # Create asset entry with issues
            asset_with_issues = {
                "ASSET_ID": asset_id,
                "IP": asset.get("IP", ""),
                "DNS": asset.get("DNS", ""),
                "OS": asset.get("OS", ""),
                "TRACKING_METHOD": tracking_method,
                "ISSUES": issues_dict,
            }
            assets_with_issues.append(asset_with_issues)

    logger.info(
        "Total Cloud: Converted %s detections from %s assets to %s assets with issues",
        detection_count,
        len(assets_with_detections),
        len(assets_with_issues),
    )
    return assets_with_issues


def _process_tc_detection(detection: Dict, asset_id: str, tracking_method: str) -> Optional[Dict]:
    """
    Process a single Total Cloud detection and convert to issue format.

    Extracts vulnerability details and constructs PLUGIN_ID based on mode.

    :param detection: Detection dictionary from Total Cloud data
    :param asset_id: Asset ID this detection belongs to
    :param tracking_method: Tracking method identifier
    :return: Issue dictionary in VMDR format or None if parsing fails
    """
    try:
        qid = detection.get("QID", "")
        if not qid:
            logger.debug("Total Cloud: Detection missing QID, skipping")
            return None

        # Extract detection metadata
        severity = detection.get("SEVERITY", "3")
        vuln_type = detection.get("TYPE", "Confirmed")
        # Normalize datetime formats from Qualys API format to ISO format
        first_found = _normalize_qualys_datetime(detection.get("FIRST_FOUND_DATETIME", ""))
        last_found = _normalize_qualys_datetime(detection.get("LAST_FOUND_DATETIME", ""))

        # Extract issue details
        title = detection.get("TITLE", f"Vulnerability QID {qid}")
        consequence = detection.get("CONSEQUENCE", "")
        diagnosis = detection.get("DIAGNOSIS", "")
        solution = detection.get("SOLUTION", "")
        cvss_base = detection.get("CVSS_BASE", "")
        cvss_temporal = detection.get("CVSS_TEMPORAL", "")

        # Construct mode-aware PLUGIN_ID and QUALYS_ID
        plugin_id, issue_qualys_id = _construct_tc_plugin_id(detection, asset_id, tracking_method)

        # Build issue dictionary
        issue = {
            "ASSET_ID": asset_id,
            "QID": qid,
            "QUALYS_ID": issue_qualys_id,
            "PLUGIN_ID": plugin_id,
            "SEVERITY": int(severity) if severity.isdigit() else 3,
            "TYPE": vuln_type,
            "FIRST_FOUND_DATETIME": first_found,
            "LAST_FOUND_DATETIME": last_found,
            "TRACKING_METHOD": tracking_method,
            "ISSUE_DATA": {
                "TITLE": title,
                "CONSEQUENCE": consequence,
                "DIAGNOSIS": diagnosis,
                "SOLUTION": solution,
            },
        }

        # Add optional CVSS fields
        if cvss_base:
            issue["ISSUE_DATA"]["CVSS_BASE"] = cvss_base
        if cvss_temporal:
            issue["ISSUE_DATA"]["CVSS_TEMPORAL"] = cvss_temporal

        # Add CVE if present
        cve_id = detection.get("CVE_ID")
        if cve_id:
            issue["ISSUE_DATA"]["CVE"] = cve_id

        return issue

    except Exception as e:
        logger.warning("Total Cloud: Error processing detection: %s", e)
        logger.debug(traceback.format_exc())
        return None


def _construct_tc_plugin_id(detection: Dict, asset_id: str, tracking_method: str) -> tuple[str, str]:
    """
    Construct mode-aware PLUGIN_ID and QUALYS_ID for Total Cloud detections.

    Modes:
    - Consolidated: One issue per unique CVE/QID across all assets
      - PLUGIN_ID: Qualys_TOTALCLOUD_CVE_2021_1234
      - QUALYS_ID: CVE_2021_1234

    - PerAsset: One issue per CVE/QID per asset
      - PLUGIN_ID: Qualys_TOTALCLOUD_CVE_2021_1234_abc123
      - QUALYS_ID: CVE_2021_1234_abc123

    :param detection: Detection dictionary from Total Cloud
    :param asset_id: Asset ID for PerAsset mode
    :param tracking_method: Tracking method identifier
    :return: Tuple of (PLUGIN_ID, QUALYS_ID)
    """
    try:
        # Get base identifier (prefer CVE, fallback to QID)
        cve_id = detection.get("CVE_ID", "")
        qid = detection.get("QID", "")
        base_id = cve_id if cve_id else f"QID_{qid}"

        # Sanitize for use in IDs (replace special chars with underscores)
        base_id = base_id.replace("-", "_").replace(".", "_")

        # Determine mode
        issue_creation_mode = _get_issue_creation_mode()

        if issue_creation_mode == "PerAsset":
            # PerAsset mode: Include asset_id in both IDs
            qualys_id = f"{base_id}_{asset_id}"
            plugin_id = f"Qualys_{tracking_method}_{qualys_id}"
        else:
            # Consolidated mode: No asset_id suffix
            qualys_id = base_id
            plugin_id = f"Qualys_{tracking_method}_{base_id}"

        return plugin_id, qualys_id

    except Exception as e:
        logger.warning("Total Cloud: Error constructing plugin ID: %s", e)
        # Fallback to basic ID
        qid = detection.get("QID", "unknown")
        return f"Qualys_{tracking_method}_QID_{qid}", f"QID_{qid}"


def _get_issue_creation_mode() -> str:
    """
    Get the issue creation mode from ScannerVariables.

    :return: Issue creation mode ('Consolidated' or 'PerAsset')
    """
    try:
        if hasattr(ScannerVariables, "issueCreation"):
            return ScannerVariables.issueCreation
        return "Consolidated"  # Default
    except Exception:
        return "Consolidated"


def deduplicate_total_cloud_and_vmdr(tc_assets: List[Dict], vmdr_assets: List[Dict]) -> tuple[List[Dict], set[str]]:
    """
    Deduplicate assets between Total Cloud and VMDR sources.

    Priority: Total Cloud takes precedence over VMDR.
    This function is used in fallback scenarios where both TC and VMDR data exist.

    :param tc_assets: List of Total Cloud assets
    :param vmdr_assets: List of VMDR assets
    :return: Tuple of (combined_assets, tc_asset_ids_set)
    """
    logger.info("Total Cloud: Deduplicating TC and VMDR assets...")

    # Track TC asset IDs
    tc_asset_ids = {asset.get("ASSET_ID") for asset in tc_assets if asset.get("ASSET_ID")}
    logger.debug("Total Cloud: Found %s unique TC asset IDs", len(tc_asset_ids))

    # Start with all TC assets
    combined_assets = list(tc_assets)

    # Add VMDR assets that aren't in TC
    vmdr_only_count = 0
    for vmdr_asset in vmdr_assets:
        vmdr_asset_id = vmdr_asset.get("ASSET_ID")
        if vmdr_asset_id not in tc_asset_ids:
            combined_assets.append(vmdr_asset)
            vmdr_only_count += 1

    logger.info(
        "Total Cloud: Deduplication complete - TC: %s, VMDR only: %s, Total: %s",
        len(tc_assets),
        vmdr_only_count,
        len(combined_assets),
    )

    return combined_assets, tc_asset_ids


def deduplicate_service_data(tc_data: List[Dict], was_data: List[Dict], container_data: List[Dict]) -> List[Dict]:
    """
    Deduplicate data across multiple Qualys services.

    Priority order: Total Cloud > WAS > Standalone Containers
    - Total Cloud includes both VM and container data
    - WAS data has unique webapp IDs
    - Standalone containers only added if not in Total Cloud

    Deduplication key: ASSET_ID only (priority determines which TRACKING_METHOD is kept)

    :param tc_data: List of Total Cloud assets/issues
    :param was_data: List of WAS assets/issues
    :param container_data: List of standalone container assets/issues
    :return: Deduplicated list of all data
    """
    logger.info("Total Cloud: Deduplicating across services (TC, WAS, Containers)...")

    seen_asset_ids = set()
    deduplicated_data = []

    # Priority 1: Total Cloud (includes both VMs and containers)
    for item in tc_data:
        asset_id = item.get("ASSET_ID") or item.get("ID")  # Handle both TC (ASSET_ID) and VMDR (ID)
        if asset_id and asset_id not in seen_asset_ids:
            seen_asset_ids.add(asset_id)
            deduplicated_data.append(item)

    tc_count = len(deduplicated_data)
    logger.debug("Total Cloud: Added %s TC items", tc_count)

    # Priority 2: WAS (unique webapp IDs)
    for item in was_data:
        asset_id = item.get("ASSET_ID")
        if asset_id and asset_id not in seen_asset_ids:
            seen_asset_ids.add(asset_id)
            deduplicated_data.append(item)

    was_count = len(deduplicated_data) - tc_count
    logger.debug("Total Cloud: Added %s WAS items", was_count)

    # Priority 3: Standalone Containers (not already in TC)
    for item in container_data:
        asset_id = item.get("ASSET_ID")
        if asset_id and asset_id not in seen_asset_ids:
            seen_asset_ids.add(asset_id)
            deduplicated_data.append(item)

    container_count = len(deduplicated_data) - tc_count - was_count
    logger.debug("Total Cloud: Added %s standalone container items", container_count)

    logger.info(
        "Total Cloud: Deduplication complete - TC: %s, WAS: %s, Containers: %s, Total: %s",
        tc_count,
        was_count,
        container_count,
        len(deduplicated_data),
    )

    return deduplicated_data


# ==================================================================================
# Total Cloud Report Listing Functions
# ==================================================================================


def _parse_assessment_report(report_element) -> Dict:
    """
    Parse a single assessment report element to dictionary.

    :param report_element: XML element containing report data
    :return: Dictionary representation of the assessment report
    :rtype: Dict
    """
    import xml.etree.ElementTree as ET

    report = {}

    # Extract simple text fields
    report["id"] = report_element.findtext("ID", "")
    report["title"] = report_element.findtext("TITLE", "")
    report["type"] = report_element.findtext("TYPE", "")
    report["status"] = report_element.findtext("STATUS", "")
    report["evaluatedDate"] = report_element.findtext("EVALUATED_DATE", "")

    # Parse control statistics if present
    controls = report_element.find("CONTROL_STATS")
    if controls is not None:
        report["passedControls"] = int(controls.findtext("PASSED", "0"))
        report["failedControls"] = int(controls.findtext("FAILED", "0"))
        report["notApplicableControls"] = int(controls.findtext("NOT_APPLICABLE", "0"))

    return report


def _total_cloud_report_to_summary(report: Dict):
    """
    Convert Total Cloud assessment report dict to ScanSummary.

    :param Dict report: Raw Total Cloud assessment report data
    :return: Normalized scan summary or None
    :rtype: Optional[ScanSummary]
    """
    from .vmdr import ScanSummary

    try:
        scan_id = report.get("id", "")
        title = report.get("title", "") or f"Total Cloud Assessment {scan_id}"
        status = report.get("status", "Unknown")

        # Parse evaluation date
        eval_date_str = report.get("evaluatedDate", "")
        scan_date = None
        if eval_date_str:
            try:
                # Try common formats
                for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M"]:
                    try:
                        scan_date = datetime.strptime(eval_date_str, fmt)
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.debug("Could not parse Total Cloud date: %s - %s", eval_date_str, e)

        # Count failed controls as "findings"
        failed_controls = report.get("failedControls", 0)

        return ScanSummary(
            scan_id=scan_id,
            scan_type="Total Cloud",
            title=title,
            status=status,
            scan_date=scan_date,
            target_count=None,
            vuln_count=failed_controls if failed_controls > 0 else None,
            duration=None,
            module="total_cloud",
        )
    except Exception as e:
        logger.warning("Failed to parse Total Cloud assessment report: %s", e)
        return None


def list_total_cloud_reports(days: int) -> list:
    """
    List Total Cloud assessment reports from the last N days.

    Queries the Qualys Total Cloud API /api/2.0/fo/compliance/posture/ endpoint
    to retrieve assessment report metadata. Only returns reports evaluated after
    the specified date threshold.

    :param int days: Number of days to look back for reports
    :return: List of scan summaries, sorted by date (newest first)
    :rtype: List[ScanSummary]
    """
    from .vmdr import ScanSummary
    from . import _get_config
    import xml.etree.ElementTree as ET

    logger.info("Fetching Total Cloud assessment reports from last %s days", days)

    try:
        # Get authentication
        config = _get_config()
        username = config.get("qualysUserName")
        password = config.get("qualysPassword")
        base_url = config.get("qualysUrl")  # Use qualysguard subdomain for Total Cloud

        if not all([username, password, base_url]):
            logger.error("Total Cloud: Missing authentication configuration")
            return []

        # Calculate date filter
        from datetime import timedelta

        eval_date_since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Build API URL
        url = urljoin(base_url, "/api/2.0/fo/compliance/posture/")
        params = {"action": "list", "evaluated_after": eval_date_since}

        logger.debug("Fetching Total Cloud reports evaluated after %s", eval_date_since)

        # Make API request
        response = requests.get(url=url, auth=(username, password), params=params, timeout=120)

        if not response.ok:
            logger.error("Total Cloud API request failed: HTTP %s", response.status_code)
            logger.error("Response: %s", response.text[:500])
            return []

        # Parse XML response
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error("Failed to parse Total Cloud XML response: %s", e)
            return []

        # Extract reports from response
        reports_element = root.find(".//ASSESSMENT_REPORT_LIST")
        if reports_element is None:
            logger.warning("No ASSESSMENT_REPORT_LIST found in Total Cloud response")
            return []

        report_elements = reports_element.findall("ASSESSMENT_REPORT")
        if not report_elements:
            logger.info("No Total Cloud assessment reports found")
            return []

        # Parse reports
        all_reports = []
        for report_elem in report_elements:
            report = _parse_assessment_report(report_elem)
            all_reports.append(report)

        # Convert to ScanSummary objects
        scan_summaries = []
        for report in all_reports:
            summary = _total_cloud_report_to_summary(report)
            if summary:
                scan_summaries.append(summary)

        # Sort by date (newest first)
        scan_summaries.sort(key=lambda s: s.scan_date or datetime.min, reverse=True)

        logger.info("Retrieved %s Total Cloud assessment reports", len(scan_summaries))
        return scan_summaries

    except requests.RequestException as e:
        logger.error("Total Cloud API request failed: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error fetching Total Cloud reports: %s", e)
        logger.debug(traceback.format_exc())
        return []
