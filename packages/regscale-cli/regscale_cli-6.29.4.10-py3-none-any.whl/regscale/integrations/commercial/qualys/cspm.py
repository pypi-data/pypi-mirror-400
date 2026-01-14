"""
Qualys CSPM (Cloud Security Posture Management) API integration

This module provides functions to interact with Qualys Total Cloud/CloudView APIs
for fetching CSPM compliance reports (CIS benchmarks for AWS, Azure, GCP).
"""

import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests

from .url_utils import transform_to_gateway_url

logger = logging.getLogger("regscale")


def auth_cspm_api() -> tuple[str, str, dict]:
    """
    Authenticate with Qualys CloudView/Total Cloud API and return JWT token

    Uses proper URL transformation to support all Qualys platforms worldwide.

    :return: Tuple of (gateway_url, jwt_token, headers)
    :rtype: tuple[str, str, dict]
    """
    from . import _get_config  # noqa: C0415

    config = _get_config()

    username = config.get("qualysUserName")
    password = config.get("qualysPassword")
    base_url = config.get("qualysUrl")

    if not all([username, password, base_url]):
        raise ValueError("Qualys credentials not configured. Please check init.yaml or environment variables.")

    # CloudView/Total Cloud uses gateway subdomain - transform using utility
    gateway_url = transform_to_gateway_url(base_url)
    logger.debug("CSPM: Transformed URL to gateway format: %s", gateway_url)

    # Get JWT token
    auth_url = urljoin(gateway_url, "/auth")
    payload = {"username": username, "password": password, "token": "true"}

    try:
        response = requests.post(auth_url, data=payload, timeout=30)

        if response.status_code not in [200, 201]:
            raise RuntimeError(f"JWT authentication failed with status {response.status_code}")

        jwt_token = response.text.strip()

        headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

        logger.info("Authenticated with Qualys CloudView API (JWT)")
        return gateway_url, jwt_token, headers

    except Exception as e:
        logger.error("Failed to get JWT token: %s", str(e))
        raise


def list_cspm_assessment_reports(include_processing: bool = False) -> List[Dict]:
    """
    List available CSPM assessment reports from Qualys CloudView API

    Uses the CloudView API endpoint: /cloudview-api/rest/v1/report/assessment/list

    :param bool include_processing: Include reports that are still processing
    :return: List of CSPM report metadata dictionaries
    :rtype: List[Dict]
    """
    logger.info("Listing CSPM assessment reports...")

    try:
        gateway_url, _, headers = auth_cspm_api()

        list_url = urljoin(gateway_url, "/cloudview-api/rest/v1/report/assessment/list")

        response = requests.get(list_url, headers=headers, timeout=60)

        if response.status_code != 200:
            logger.error("Failed to list reports: HTTP %s", response.status_code)
            return []

        # Parse JSON response
        data = response.json()

        # Extract reports from response
        reports = data.get("data", []) if isinstance(data, dict) else data

        # Filter out processing reports if not requested
        if not include_processing:
            reports = [r for r in reports if r.get("status") == "COMPLETED"]

        logger.info("Found %s CSPM assessment report(s)", len(reports))
        return reports

    except Exception as e:
        logger.error("Failed to list CSPM reports: %s", str(e))
        return []


def download_cspm_assessment_report(report_id: str, report_name: str = "", output_dir: str = ".") -> Optional[str]:
    """
    Download a specific CSPM assessment report by ID

    Uses CloudView API with JWT authentication to download the report.
    Endpoint: /cloudview-api/rest/v1/report/assessment/{reportId}/download

    :param str report_id: The Qualys report ID (UUID)
    :param str report_name: Optional report name for filename
    :param str output_dir: Directory to save the report file
    :return: Path to downloaded file, or None if failed
    :rtype: Optional[str]
    """
    logger.info("Downloading CSPM report ID: %s", report_id)

    try:
        # Get JWT token and gateway URL
        gateway_url, _, headers = auth_cspm_api()

        # Download endpoint
        download_url = urljoin(gateway_url, f"/cloudview-api/rest/v1/report/assessment/{report_id}/download")

        # Parameters - must be lowercase "csv"
        params = {"reportFormat": "csv"}

        response = requests.get(download_url, headers=headers, params=params, timeout=120)

        if response.status_code != 200:
            logger.error("Failed to download report %s: HTTP %s", report_id, response.status_code)
            try:
                error_data = response.json()
                logger.error("Error details: %s", error_data)
            except Exception:
                pass
            return None

        # Create filename
        if report_name:
            # Use report name if provided
            safe_name = report_name.replace(" ", "_").replace("-", "_")
            filename = f"{safe_name}.csv"
        else:
            # Use report ID and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"CSPM_Report_{report_id}_{timestamp}.csv"

        filepath = os.path.join(output_dir, filename)

        # Save file
        with open(filepath, "wb") as f:
            f.write(response.content)

        logger.info("Downloaded CSPM report to: %s (%s bytes)", filepath, len(response.content))
        return filepath

    except Exception as e:
        logger.error("Failed to download report %s: %s", report_id, str(e))
        return None


def _download_completed_reports(reports: List[Dict], output_dir: str) -> List[str]:
    """Download all completed CSPM reports."""
    downloaded_files = []
    for report in reports:
        if report.get("status") == "COMPLETED":
            report_id = report.get("reportId")
            report_name = report.get("reportName", "")
            filepath = download_cspm_assessment_report(report_id, report_name, output_dir)
            if filepath:
                downloaded_files.append(filepath)
    return downloaded_files


def _wait_and_download_processing_reports(
    processing_reports: List[Dict], output_dir: str, max_wait_minutes: int
) -> List[str]:
    """Wait for processing reports to complete and download them."""
    downloaded_files = []
    start_time = time.time()
    check_interval = 60

    while processing_reports and (time.time() - start_time) < (max_wait_minutes * 60):
        time.sleep(check_interval)
        current_reports = list_cspm_assessment_reports(include_processing=True)

        for proc_report in processing_reports[:]:
            report_id = proc_report.get("reportId")
            current = next((r for r in current_reports if r.get("reportId") == report_id), None)

            if current and current.get("status") == "COMPLETED":
                logger.info("Report %s completed, downloading...", report_id)
                filepath = download_cspm_assessment_report(report_id, current.get("reportName", ""), output_dir)
                if filepath:
                    downloaded_files.append(filepath)
                processing_reports.remove(proc_report)

    if processing_reports:
        logger.warning("%s report(s) still processing after timeout", len(processing_reports))

    return downloaded_files


def fetch_latest_cspm_reports(
    output_dir: str = ".", wait_for_processing: bool = False, max_wait_minutes: int = 30
) -> List[str]:
    """
    Fetch all available CSPM assessment reports

    This function will download all completed CSPM reports. If wait_for_processing
    is True, it will poll for reports that are currently processing until they
    complete or the timeout is reached.

    :param str output_dir: Directory to save report files
    :param bool wait_for_processing: Wait for processing reports to complete
    :param int max_wait_minutes: Maximum minutes to wait for processing reports
    :return: List of paths to downloaded files
    :rtype: List[str]
    """
    logger.info("Fetching latest CSPM compliance reports...")
    os.makedirs(output_dir, exist_ok=True)

    reports = list_cspm_assessment_reports(include_processing=wait_for_processing)
    if not reports:
        logger.warning("No CSPM compliance reports found")
        return []

    # Download completed reports immediately
    downloaded_files = _download_completed_reports(reports, output_dir)

    # Wait for and download processing reports if requested
    if wait_for_processing:
        all_reports = list_cspm_assessment_reports(include_processing=True)
        processing_reports = [r for r in all_reports if r.get("status") != "COMPLETED"]

        if processing_reports:
            logger.info(
                "Found %s processing report(s), waiting up to %s minutes...", len(processing_reports), max_wait_minutes
            )
            downloaded_files.extend(
                _wait_and_download_processing_reports(processing_reports, output_dir, max_wait_minutes)
            )

    logger.info("Downloaded %s CSPM report(s)", len(downloaded_files))
    return downloaded_files


def trigger_cspm_scan(report_id: str) -> Optional[str]:
    """
    Trigger a CSPM assessment scan by rerunning an existing report

    Uses the CloudView API endpoint: /cloudview-api/rest/v1/report/assessment/{reportId}/rerun

    :param str report_id: The existing report ID to rerun
    :return: New report ID if successful, None if failed
    :rtype: Optional[str]
    """
    logger.info("Triggering CSPM scan rerun for report ID: %s", report_id)

    try:
        gateway_url, _, headers = auth_cspm_api()

        rerun_url = urljoin(gateway_url, f"/cloudview-api/rest/v1/report/assessment/{report_id}/rerun")

        response = requests.post(rerun_url, headers=headers, timeout=60)

        if response.status_code not in [200, 201]:
            logger.error("Failed to trigger scan: HTTP %s", response.status_code)
            try:
                error_data = response.json()
                logger.error("Error details: %s", error_data)
            except Exception:
                logger.error("Response text: %s", response.text)
            return None

        # Response is the new report ID (plain text UUID)
        new_report_id = response.text.strip()
        logger.info("Successfully triggered CSPM scan. New report ID: %s", new_report_id)
        return new_report_id

    except Exception as e:
        logger.error("Failed to trigger CSPM scan: %s", str(e))
        return None


def get_cspm_report_status(report_id: str) -> Optional[Dict]:
    """
    Get the status of a specific CSPM assessment report

    Polls the list endpoint and filters by report ID.

    :param str report_id: The report ID to check
    :return: Report metadata dictionary with status, or None if not found
    :rtype: Optional[Dict]
    """
    try:
        gateway_url, _, headers = auth_cspm_api()

        list_url = urljoin(gateway_url, "/cloudview-api/rest/v1/report/assessment/list")

        response = requests.get(list_url, headers=headers, timeout=60)

        if response.status_code != 200:
            logger.error("Failed to get report status: HTTP %s", response.status_code)
            return None

        data = response.json()
        reports = data.get("data", []) if isinstance(data, dict) else data

        # Find the specific report
        report = next((r for r in reports if r.get("reportId") == report_id), None)

        if report:
            status = report.get("status", "UNKNOWN")
            logger.info("Report %s status: %s", report_id, status)
            return report

        logger.warning("Report %s not found", report_id)
        return None

    except Exception as e:
        logger.error("Failed to get report status: %s", str(e))
        return None


def list_cspm_connectors(cloud_provider: Optional[str] = None) -> List[Dict]:
    """
    List CSPM cloud connectors (AWS, Azure, GCP)

    Uses CloudView API endpoints:
    - /cloudview-api/rest/v1/aws/connectors
    - /cloudview-api/rest/v1/azure/connectors
    - /cloudview-api/rest/v1/gcp/connectors

    :param str cloud_provider: Optional filter for specific provider (aws, azure, gcp). If None, lists all.
    :return: List of connector dictionaries
    :rtype: List[Dict]
    """
    logger.info("Listing CSPM connectors...")

    try:
        gateway_url, _, headers = auth_cspm_api()

        providers = []
        if cloud_provider:
            providers = [cloud_provider.lower()]
        else:
            providers = ["aws", "azure", "gcp"]

        all_connectors = []

        for provider in providers:
            connector_url = urljoin(gateway_url, f"/cloudview-api/rest/v1/{provider}/connectors")

            try:
                response = requests.get(connector_url, headers=headers, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    connectors = data.get("data", []) if isinstance(data, dict) else data

                    # Add provider tag to each connector
                    for connector in connectors:
                        connector["cloud_provider"] = provider.upper()

                    all_connectors.extend(connectors)
                    logger.info("Found %s %s connector(s)", len(connectors), provider.upper())
                else:
                    logger.warning("Failed to list %s connectors: HTTP %s", provider.upper(), response.status_code)

            except Exception as e:
                logger.warning("Failed to list %s connectors: %s", provider.upper(), str(e))
                continue

        logger.info("Total connectors found: %s", len(all_connectors))
        return all_connectors

    except Exception as e:
        logger.error("Failed to list connectors: %s", str(e))
        return []


def trigger_and_wait_for_scan(
    report_id: str, output_dir: str = ".", max_wait_minutes: int = 30, check_interval_seconds: int = 30
) -> Optional[str]:
    """
    Trigger a CSPM scan, wait for completion, and download the results

    This is a convenience function that combines trigger, poll, and download.

    :param str report_id: The existing report ID to rerun
    :param str output_dir: Directory to save the downloaded report
    :param int max_wait_minutes: Maximum minutes to wait for scan completion
    :param int check_interval_seconds: Seconds between status checks
    :return: Path to downloaded report file, or None if failed
    :rtype: Optional[str]
    """
    logger.info("Starting CSPM scan workflow for report ID: %s", report_id)

    # Trigger the scan
    new_report_id = trigger_cspm_scan(report_id)
    if not new_report_id:
        logger.error("Failed to trigger scan")
        return None

    logger.info("Scan triggered successfully. Waiting for completion...")

    # Poll for completion
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60

    while (time.time() - start_time) < max_wait_seconds:
        time.sleep(check_interval_seconds)

        report_status = get_cspm_report_status(new_report_id)

        if not report_status:
            logger.warning("Could not get report status, retrying...")
            continue

        status = report_status.get("status", "UNKNOWN")

        if status == "COMPLETED":
            logger.info("Scan completed! Downloading report...")
            report_name = report_status.get("reportName", "")
            filepath = download_cspm_assessment_report(new_report_id, report_name, output_dir)
            return filepath

        if status == "FAILED":
            logger.error("Scan failed")
            return None

        elapsed_minutes = (time.time() - start_time) / 60
        logger.info("Scan status: %s (elapsed: %.1f minutes)", status, elapsed_minutes)

    logger.error("Scan did not complete within %s minutes", max_wait_minutes)
    return None
