#!/usr/bin/env python3
"""
Qualys Diagnostics Script

Comprehensive testing tool for Qualys API integrations including:
- JWT Authentication
- Total Cloud Service (AWS Connectors)
- Web Application Scanning (WAS)
- Container Security
- Vulnerability Management Detection and Response (VMDR)

Usage:
    python qualys_diagnostics.py [--config init.yaml] [--output-dir ./diagnostics_output] [--verbose]
"""

import argparse
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from xml.etree import ElementTree as ET

import requests
import yaml
from requests.auth import HTTPBasicAuth

from .url_utils import transform_to_api_url, transform_to_gateway_url


class Colors:
    """ANSI color codes for console output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# Constants
REGSCALE_CLI_HEADER = "RegScale CLI"
XML_CONTENT_TYPE = "text/xml"


class QualysDiagnostics:
    """Main diagnostics class for testing Qualys API modules"""

    def __init__(self, config_path: str, output_dir: str, verbose: bool = False, modules: Optional[list] = None):
        """Initialize diagnostics with configuration"""
        self.config_path = config_path
        self.output_dir = output_dir
        self.verbose = verbose
        self.modules_filter = modules
        self.config = {}
        self.base_url = ""
        self.username = ""
        self.password = ""
        self.jwt_token = None
        self.results = {}
        self.start_time = None
        self.end_time = None

        # Create sessions for different authentication methods
        # Following the pattern from regscale/integrations/commercial/qualys/__init__.py
        self.basic_auth_session = requests.Session()  # For VMDR, WAS, Total Cloud (Basic Auth)
        self.jwt_session = requests.Session()  # For Container Security (JWT Bearer token)

        # Setup logging
        self.setup_logging()

        # Load configuration
        self.load_config()

    def setup_logging(self):
        """Configure logging with appropriate level and format"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """Load and validate configuration from init.yaml"""
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)

            # Extract required fields
            self.base_url = self.normalize_url(self.config.get("qualysUrl", ""))
            self.username = self.config.get("qualysUserName", "")
            self.password = self.config.get("qualysPassword", "")

            # Validate required fields
            if not self.base_url:
                raise ValueError("qualysUrl not found in configuration")
            if not self.username:
                raise ValueError("qualysUserName not found in configuration")
            if not self.password:
                raise ValueError("qualysPassword not found in configuration")

            self.logger.info(f"Configuration loaded from: {self.config_path}")
            self.logger.info(f"Base URL: {self.sanitize_url(self.base_url)}")
            self.logger.info(f"Username: {self.username}")

        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            sys.exit(1)

    @staticmethod
    def normalize_url(url: str) -> str:
        """Remove trailing slashes from URL"""
        return url.rstrip("/")

    @staticmethod
    def sanitize_url(url: str) -> str:
        """Sanitize URL for logging (basic version for display)"""
        return url

    def transform_to_gateway_url(self, url: str) -> str:
        """Transform API URL to gateway URL for JWT authentication"""
        if "://" not in url:
            return url

        protocol, rest = url.split("://", 1)
        if "." not in rest:
            return url

        # Replace subdomain with 'gateway'
        parts = rest.split(".", 1)
        gateway_url = f"{protocol}://gateway.{parts[1]}"

        self.logger.debug(f"Transformed URL: {url} -> {gateway_url}")
        return gateway_url

    def colorize(self, text: str, color: str) -> str:
        """Add color to text for console output"""
        return f"{color}{text}{Colors.RESET}"

    def make_request(self, method: str, url: str, use_jwt_session: bool = False, **kwargs) -> requests.Response:
        """
        Wrapper for requests with error handling and logging

        :param str method: HTTP method (GET, POST, etc.)
        :param str url: Request URL
        :param bool use_jwt_session: If True, use JWT session; otherwise use basic auth session
        :param kwargs: Additional arguments to pass to requests
        :return: Response object
        :rtype: requests.Response
        """
        try:
            self.logger.debug(f"{method.upper()} {url}")
            if "data" in kwargs:
                self.logger.debug(
                    f"Request body: {kwargs['data'][:200] if isinstance(kwargs['data'], str) else 'binary'}"
                )

            # Select appropriate session based on authentication type
            session = self.jwt_session if use_jwt_session else self.basic_auth_session

            response = session.request(method, url, timeout=30, **kwargs)

            self.logger.debug(f"Response status: {response.status_code}")
            if self.verbose and response.text:
                self.logger.debug(f"Response body (first 500 chars): {response.text[:500]}")

            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def parse_xml_response(self, xml_string: str) -> Optional[ET.Element]:
        """Parse XML response and return root element"""
        try:
            return ET.fromstring(xml_string)
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {e}")
            self.logger.debug(f"Raw XML: {xml_string[:500]}")
            return None

    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"

    def _extract_jwt_token_from_response(self, response: requests.Response, result: Dict[str, Any]) -> Optional[str]:
        """
        Extract JWT token from authentication response

        :param response: HTTP response object
        :param result: Result dictionary to update with token format
        :return: JWT token or None if extraction fails
        :rtype: Optional[str]
        """
        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            try:
                auth_data = response.json()
                token = auth_data.get("access_token")
                result["token_format"] = "json"
                self.logger.debug("JWT token acquired (JSON format)")
                return token
            except Exception as e:
                self.logger.warning(f"Failed to parse JSON token response: {e}")
                return None

        if "text/plain" in content_type or not content_type:
            token = response.text.strip()
            result["token_format"] = "plain_text"
            self.logger.debug("JWT token acquired (plain text format)")
            return token

        self.logger.warning(f"Unexpected Content-Type: {content_type}")
        return None

    def _attempt_jwt_auth_at_url(self, url: str, result: Dict[str, Any], module_name: str) -> bool:
        """
        Attempt JWT authentication at a specific URL

        :param url: Authentication URL to try
        :param result: Result dictionary to update
        :param module_name: Module name for logging
        :return: True if authentication succeeded, False otherwise
        :rtype: bool
        """
        result["attempted_urls"].append(url)
        try:
            self.logger.debug(f"Attempting JWT auth at: {url}")

            response = self.make_request(
                "POST",
                url,
                headers={"X-Requested-With": REGSCALE_CLI_HEADER},
                data={"username": self.username, "password": self.password, "permissions": "true", "token": "true"},
            )

            if response.status_code not in [200, 201]:
                self.logger.warning(f"Failed at {url}: HTTP {response.status_code}")
                self.logger.debug(f"Response body: {response.text[:200]}")
                return False

            token = self._extract_jwt_token_from_response(response, result)

            if token:
                self.jwt_token = token
                result["status"] = "passed"
                result["successful_url"] = url
                result["token_received"] = True
                result["token_preview"] = token[:50] + "..." if len(token) > 50 else token
                result["details"] = f"JWT token obtained successfully from {url} ({result['token_format']} format)"

                self.logger.info(self.colorize(f"[{module_name}] ✓ PASSED - JWT token received", Colors.GREEN))
                self.logger.debug(f"Token preview: {result['token_preview']}")
                return True

            return False

        except Exception as e:
            self.logger.warning(f"Error at {url}: {e}")
            return False

    def test_jwt_auth(self) -> Dict[str, Any]:
        """Test JWT authentication with gateway fallback"""
        module_name = "JWT_AUTH"
        self.logger.info(f"[{module_name}] Testing JWT authentication...")

        result = {
            "status": "failed",
            "attempted_urls": [],
            "successful_url": None,
            "token_received": False,
            "token_preview": None,
            "token_format": None,
            "error": None,
            "details": "",
        }

        # Transform base URL to gateway format (replace 'qualysapi' OR 'qualysguard' with 'gateway')
        gateway_url = self.base_url.replace("qualysapi", "gateway").replace("qualysguard", "gateway")
        urls_to_try = [f"{gateway_url}/auth", f"{self.base_url}/auth"]

        # Try each URL in sequence
        for url in urls_to_try:
            if self._attempt_jwt_auth_at_url(url, result, module_name):
                return result

        # All attempts failed
        result["error"] = "Failed to obtain JWT token from all attempted URLs"
        result["details"] = f"Attempted URLs: {', '.join(result['attempted_urls'])}"
        self.logger.error(self.colorize(f"[{module_name}] ✗ FAILED - {result['error']}", Colors.RED))

        return result

    def _check_connector_details(self, connector_id: str, result: Dict[str, Any], module_name: str) -> None:
        """Fetch and validate connector details"""
        detail_url = f"{self.base_url}/cloudview-api/rest/v1/aws/connectors/{connector_id}"
        detail_response = self.make_request("GET", detail_url, auth=(self.username, self.password))

        if detail_response.status_code == 200:
            result["connector_details_tested"] = True
            self.logger.info(f"[{module_name}] ✓ Connector details retrieved for: {connector_id}")

    def _check_assessment_reports(self, result: Dict[str, Any], module_name: str) -> None:
        """Fetch and process assessment reports"""
        reports_url = f"{self.base_url}/cloudview-api/rest/v1/report/assessment/list?pageNo=1&pageSize=50"
        reports_response = self.make_request("GET", reports_url, auth=(self.username, self.password))

        if reports_response.status_code == 200:
            reports_data = reports_response.json()
            reports = reports_data.get("content", [])
            result["assessment_reports_found"] = len(reports)

            if reports:
                report_id = reports[0].get("id")
                result["sample_report"] = {
                    "id": report_id,
                    "name": reports[0].get("name"),
                    "status": reports[0].get("status"),
                }
                self.logger.info(f"[{module_name}] ✓ Found {result['assessment_reports_found']} assessment reports")
            else:
                self.logger.info(f"[{module_name}] No assessment reports found (empty list)")
        elif reports_response.status_code == 404:
            self.logger.info(f"[{module_name}] Assessment reports endpoint not available (HTTP 404)")
        else:
            self.logger.warning(f"[{module_name}] Assessment reports returned HTTP {reports_response.status_code}")

    def _check_cdr_findings(self, result: Dict[str, Any], module_name: str) -> None:
        """Fetch and process CDR (Cloud Detection and Response) findings"""
        cdr_url = f"{self.base_url}/cdr-api/rest/v1/findings"
        cdr_response = self.make_request(
            "GET", cdr_url, auth=(self.username, self.password), headers={"accept": "application/json"}
        )

        if cdr_response.status_code == 200:
            cdr_data = cdr_response.json()
            findings = cdr_data.get("findings", cdr_data.get("data", cdr_data.get("content", [])))
            result["cdr_findings_found"] = len(findings) if isinstance(findings, list) else 0

            if findings and isinstance(findings, list) and len(findings) > 0:
                first_finding = findings[0]
                result["sample_cdr_finding"] = {
                    "id": first_finding.get("id", first_finding.get("findingId")),
                    "severity": first_finding.get("severity"),
                    "status": first_finding.get("status"),
                }
                self.logger.info(f"[{module_name}] ✓ Found {result['cdr_findings_found']} CDR findings")
            else:
                self.logger.info(f"[{module_name}] No CDR findings found (empty list)")
        elif cdr_response.status_code == 404:
            self.logger.info(f"[{module_name}] CDR findings endpoint not available (HTTP 404)")
        else:
            self.logger.warning(f"[{module_name}] CDR findings returned HTTP {cdr_response.status_code}")

    def test_total_cloud(self) -> Dict[str, Any]:
        """Test Total Cloud Service AWS connector APIs"""
        module_name = "TOTAL_CLOUD"
        self.logger.info(f"[{module_name}] Testing Total Cloud Service...")

        result = {
            "status": "failed",
            "connectors_found": 0,
            "connector_details_tested": False,
            "assessment_reports_found": 0,
            "cdr_findings_found": 0,
            "sample_connector": None,
            "sample_report": None,
            "sample_cdr_finding": None,
            "error": None,
            "details": "",
        }

        try:
            # Test 1: List AWS connectors
            url = f"{self.base_url}/cloudview-api/rest/v1/aws/connectors?pageNo=0&pageSize=50"
            response = self.make_request("GET", url, auth=(self.username, self.password))

            if response.status_code in [401, 403]:
                result["status"] = "skipped"
                result["error"] = "Total Cloud module not enabled or access denied"
                result["details"] = f"HTTP {response.status_code}: {response.text[:200]}"
                self.logger.warning(self.colorize(f"[{module_name}] ⊘ SKIPPED - Module not enabled", Colors.YELLOW))
                return result

            if response.status_code == 200:
                data = response.json()
                connectors = data.get("content", [])
                result["connectors_found"] = len(connectors)

                if connectors:
                    connector_id = connectors[0].get("connectorId")
                    result["sample_connector"] = {"id": connector_id, "name": connectors[0].get("name")}

                    # Test 2: Get connector details
                    if connector_id:
                        self._check_connector_details(connector_id, result, module_name)

                # Test 3: List assessment reports
                self._check_assessment_reports(result, module_name)

                # Test 4: Get CDR findings
                self._check_cdr_findings(result, module_name)

                # Test 5: List Total Cloud compliance reports
                tc_auth = HTTPBasicAuth(self.username, self.password)
                tc_headers = {"X-Requested-With": REGSCALE_CLI_HEADER}
                self._list_total_cloud_reports(self.base_url, tc_headers, tc_auth, result, module_name)

                result["status"] = "passed"
                reports_msg = (
                    f", {result.get('reports_found', 0)} compliance reports" if "reports_found" in result else ""
                )
                result["details"] = (
                    f"Found {result['connectors_found']} AWS connectors, "
                    f"{result['assessment_reports_found']} assessment reports, "
                    f"{result['cdr_findings_found']} CDR findings{reports_msg}"
                )
                self.logger.info(self.colorize(f"[{module_name}] ✓ PASSED - Total Cloud API accessible", Colors.GREEN))
            else:
                result["error"] = f"HTTP {response.status_code}"
                result["details"] = response.text[:200]

        except Exception as e:
            result["error"] = str(e)
            result["details"] = traceback.format_exc()
            self.logger.error(self.colorize(f"[{module_name}] ✗ FAILED - {result['error']}", Colors.RED))

        return result

    def _check_was_findings(self, was_url: str, xml_body: str, result: Dict[str, Any], module_name: str) -> None:
        """Fetch and process WAS findings"""
        findings_url = f"{was_url}/qps/rest/3.0/search/was/finding"
        findings_response = self.make_request(
            "POST",
            findings_url,
            headers={"content-type": XML_CONTENT_TYPE, "X-Requested-With": REGSCALE_CLI_HEADER},
            auth=(self.username, self.password),
            data=xml_body,
        )

        if findings_response.status_code == 200:
            findings_root = self.parse_xml_response(findings_response.text)
            if findings_root is not None:
                findings = findings_root.findall(".//Finding")
                result["findings_found"] = len(findings)
                self.logger.info(f"[{module_name}] ✓ Found {len(findings)} findings")

    def test_was(self) -> Dict[str, Any]:
        """Test Web Application Scanning APIs"""
        module_name = "WAS"
        self.logger.info(f"[{module_name}] Testing Web Application Scanning...")

        result = {
            "status": "failed",
            "webapps_found": 0,
            "findings_found": 0,
            "sample_webapp": None,
            "error": None,
            "details": "",
        }

        try:
            # Transform to qualysapi subdomain for WAS API
            was_url = transform_to_api_url(self.base_url)

            # Test 1: Search for web applications (using XML as originally designed)
            url = f"{was_url}/qps/rest/3.0/search/was/webapp"
            xml_body = "<ServiceRequest></ServiceRequest>"

            response = self.make_request(
                "POST",
                url,
                headers={"content-type": XML_CONTENT_TYPE, "X-Requested-With": REGSCALE_CLI_HEADER},
                auth=(self.username, self.password),
                data=xml_body,
            )

            if response.status_code in [401, 403]:
                result["status"] = "skipped"
                result["error"] = "WAS module not enabled or access denied"
                result["details"] = f"HTTP {response.status_code}"
                self.logger.warning(self.colorize(f"[{module_name}] ⊘ SKIPPED - Module not enabled", Colors.YELLOW))
                return result

            if response.status_code == 200:
                root = self.parse_xml_response(response.text)
                if root is not None:
                    webapps = root.findall(".//WebApp")
                    result["webapps_found"] = len(webapps)

                    if webapps:
                        webapp_id = webapps[0].findtext("id")
                        webapp_name = webapps[0].findtext("name")
                        result["sample_webapp"] = {"id": webapp_id, "name": webapp_name}

                        # Test 2: Search for findings
                        self._check_was_findings(was_url, xml_body, result, module_name)

                        # Test 3: List WAS scans
                        was_headers = {"content-type": XML_CONTENT_TYPE, "X-Requested-With": REGSCALE_CLI_HEADER}
                        self._list_was_scans(was_url, was_headers, result, module_name)

                result["status"] = "passed"
                scans_msg = f", {result.get('scans_found', 0)} scans" if "scans_found" in result else ""
                result["details"] = f"Found {result['webapps_found']} web applications{scans_msg}"
                self.logger.info(
                    self.colorize(
                        f"[{module_name}] ✓ PASSED - Found {result['webapps_found']} web applications", Colors.GREEN
                    )
                )
            else:
                result["error"] = f"HTTP {response.status_code}"
                result["details"] = response.text[:200]

        except Exception as e:
            result["error"] = str(e)
            result["details"] = traceback.format_exc()
            self.logger.error(self.colorize(f"[{module_name}] ✗ FAILED - {result['error']}", Colors.RED))

        return result

    def _check_image_vulnerabilities(
        self, gateway_url: str, headers: dict, image_id: str, result: Dict[str, Any], module_name: str
    ) -> None:
        """Fetch vulnerabilities for a specific image"""
        image_vuln_url = f"{gateway_url}/csapi/v1.3/images/{image_id}/vuln"
        image_vuln_response = self.make_request("GET", image_vuln_url, headers=headers, use_jwt_session=True)

        if image_vuln_response.status_code == 200:
            image_vuln_data = image_vuln_response.json()
            result["image_vulns_found"] = len(image_vuln_data.get("vulnerabilities", []))
            self.logger.info(f"[{module_name}] ✓ Found {result['image_vulns_found']} vulnerabilities in first image")

    def _check_container_vulnerabilities(
        self, gateway_url: str, headers: dict, container_id: str, result: Dict[str, Any], module_name: str
    ) -> None:
        """Fetch vulnerabilities for a specific container"""
        vuln_url = f"{gateway_url}/csapi/v1.3/containers/{container_id}/vuln"
        vuln_response = self.make_request("GET", vuln_url, headers=headers, use_jwt_session=True)

        if vuln_response.status_code == 200:
            vuln_data = vuln_response.json()
            result["container_vulns_found"] = len(vuln_data.get("vulnerabilities", []))
            self.logger.info(
                f"[{module_name}] ✓ Found {result['container_vulns_found']} vulnerabilities in first container"
            )

    def _check_containers(self, gateway_url: str, headers: dict, result: Dict[str, Any], module_name: str) -> None:
        """Fetch and process containers"""
        containers_url = f"{gateway_url}/csapi/v1.3/containers?pageNumber=1&pageSize=50&sort=created:desc"
        containers_response = self.make_request("GET", containers_url, headers=headers, use_jwt_session=True)

        if containers_response.status_code == 200:
            containers_data = containers_response.json()
            containers = containers_data.get("data", [])
            result["containers_found"] = len(containers)

            if containers:
                container_id = containers[0].get("uuid")
                result["sample_container"] = {
                    "id": container_id,
                    "name": containers[0].get("name"),
                    "imageId": containers[0].get("imageId"),
                }
                self.logger.info(f"[{module_name}] ✓ Found {result['containers_found']} containers")

                # Check container vulnerabilities
                if container_id:
                    self._check_container_vulnerabilities(gateway_url, headers, container_id, result, module_name)
        elif containers_response.status_code == 204:
            self.logger.info(f"[{module_name}] No containers found (HTTP 204)")

    def test_container_security(self) -> Dict[str, Any]:
        """Test Container Security APIs with JWT token"""
        module_name = "CONTAINER_SECURITY"
        self.logger.info(f"[{module_name}] Testing Container Security...")

        result = {
            "status": "failed",
            "containers_found": 0,
            "images_found": 0,
            "container_vulns_found": 0,
            "image_vulns_found": 0,
            "sample_container": None,
            "sample_image": None,
            "error": None,
            "details": "",
        }

        if not self.jwt_token:
            result["status"] = "skipped"
            result["error"] = "JWT token not available"
            result["details"] = "Container Security requires JWT authentication which failed earlier"
            self.logger.warning(self.colorize(f"[{module_name}] ⊘ SKIPPED - No JWT token", Colors.YELLOW))
            return result

        try:
            # Transform to gateway URL for Container Security API calls
            gateway_url = transform_to_gateway_url(self.base_url)

            headers = {"Authorization": f"Bearer {self.jwt_token}", "X-Requested-With": REGSCALE_CLI_HEADER}

            # Test 1: List images (primary test)
            images_url = f"{gateway_url}/csapi/v1.3/images?pageNumber=1&pageSize=50"
            images_response = self.make_request("GET", images_url, headers=headers, use_jwt_session=True)

            if images_response.status_code in [401, 403]:
                result["status"] = "skipped"
                result["error"] = "Container Security module not enabled or access denied"
                result["details"] = f"HTTP {images_response.status_code}"
                self.logger.warning(self.colorize(f"[{module_name}] ⊘ SKIPPED - Module not enabled", Colors.YELLOW))
                return result

            if images_response.status_code == 200:
                images_data = images_response.json()
                images = images_data.get("data", [])
                result["images_found"] = len(images)

                if images:
                    image_id = images[0].get("imageId")
                    result["sample_image"] = {"id": image_id, "repository": images[0].get("repository")}
                    self.logger.info(f"[{module_name}] ✓ Found {result['images_found']} images")

                    # Test 2: Get image vulnerabilities
                    if image_id:
                        self._check_image_vulnerabilities(gateway_url, headers, image_id, result, module_name)

                # Test 3: List containers
                self._check_containers(gateway_url, headers, result, module_name)

                # Test 4: List container reports
                self._list_container_reports(gateway_url, headers, result, module_name)

                result["status"] = "passed"
                reports_msg = f", {result.get('reports_found', 0)} reports" if "reports_found" in result else ""
                result["details"] = (
                    f"Found {result['images_found']} images and {result['containers_found']} containers{reports_msg}"
                )
                self.logger.info(
                    self.colorize(f"[{module_name}] ✓ PASSED - Container Security API accessible", Colors.GREEN)
                )
            elif images_response.status_code == 204:
                result["status"] = "passed"
                result["details"] = "Container Security module enabled but no image data available yet"
                self.logger.info(
                    self.colorize(f"[{module_name}] ✓ PASSED - API accessible (no image data yet)", Colors.GREEN)
                )
            else:
                result["error"] = f"HTTP {images_response.status_code}"
                result["details"] = images_response.text[:200]

        except Exception as e:
            result["error"] = str(e)
            result["details"] = traceback.format_exc()
            self.logger.error(self.colorize(f"[{module_name}] ✗ FAILED - {result['error']}", Colors.RED))

        return result

    def _check_vmdr_policies(
        self, vmdr_url: str, headers: dict, auth: HTTPBasicAuth, result: Dict[str, Any], module_name: str
    ) -> None:
        """Fetch and process VMDR compliance policies"""
        policies_url = f"{vmdr_url}/api/2.0/fo/compliance/policy/?action=list&details=All"
        policies_response = self.make_request("GET", policies_url, headers=headers, auth=auth)

        if policies_response.status_code == 200:
            policies_root = self.parse_xml_response(policies_response.text)
            if policies_root is not None:
                policies = policies_root.findall(".//POLICY")
                result["policies_found"] = len(policies)

                if policies:
                    policy_id = policies[0].findtext("ID")
                    policy_title = policies[0].findtext("TITLE")
                    result["sample_policy"] = {"id": policy_id, "title": policy_title}

                self.logger.info(f"[{module_name}] ✓ Found {result['policies_found']} compliance policies")

    def _parse_vmdr_report_response(self, reports_response):
        """Parse VMDR reports from JSON or XML response."""
        try:
            # Try JSON response first
            data = reports_response.json()
            report_list = data.get("REPORT_LIST_OUTPUT", {}).get("RESPONSE", {}).get("REPORT_LIST", {})
            reports = report_list.get("REPORT", [])
        except Exception:
            # Fallback to XML parsing
            root = self.parse_xml_response(reports_response.text)
            reports = root.findall(".//REPORT") if root is not None else []

        # Normalize to list
        return [reports] if (reports and not isinstance(reports, list)) else (reports or [])

    def _extract_vmdr_report_details(self, first_report):
        """Extract ID, title, and status from VMDR report."""
        if isinstance(first_report, dict):
            report_id = first_report.get("ID", "N/A")
            report_title = first_report.get("TITLE", "N/A")
            report_status = first_report.get("STATUS", {})
            report_status = report_status.get("STATE", "N/A") if isinstance(report_status, dict) else "N/A"
        else:
            report_id = first_report.findtext("ID", "N/A")
            report_title = first_report.findtext("TITLE", "N/A")
            status_elem = first_report.find("STATUS")
            report_status = status_elem.findtext("STATE", "N/A") if status_elem is not None else "N/A"

        return {"id": report_id, "title": report_title, "status": report_status}

    def _list_vmdr_reports(
        self, vmdr_url: str, headers: dict, auth: HTTPBasicAuth, result: Dict[str, Any], module_name: str
    ) -> None:
        """List VMDR scan reports from the last 30 days"""
        try:
            from datetime import timedelta

            # Calculate date 30 days ago
            date_since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # List reports using VMDR API
            reports_url = f"{vmdr_url}/api/2.0/fo/report/?action=list&launched_after_datetime={date_since}"
            reports_response = self.make_request("GET", reports_url, headers=headers, auth=auth)

            if reports_response.status_code == 200:
                reports = self._parse_vmdr_report_response(reports_response)
                result["reports_found"] = len(reports)

                if reports:
                    result["sample_report"] = self._extract_vmdr_report_details(reports[0])
                    self.logger.info(f"[{module_name}] ✓ Found {len(reports)} scan reports (last 30 days)")
            else:
                result["reports_found"] = 0
                self.logger.warning(f"[{module_name}] Could not list reports: HTTP {reports_response.status_code}")

        except Exception as e:
            result["reports_found"] = 0
            self.logger.warning(f"[{module_name}] Error listing reports: {e}")

    def _list_was_scans(self, was_url: str, headers: dict, result: Dict[str, Any], module_name: str) -> None:
        """List WAS scans from the last 30 days"""
        try:
            from datetime import timedelta

            # Calculate date 30 days ago
            date_since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # Build XML request body with date filter
            xml_body = f"""<ServiceRequest>
                <filters>
                    <Criteria field="launchedDate" operator="GREATER">{date_since}</Criteria>
                </filters>
                <preferences>
                    <limitResults>10</limitResults>
                </preferences>
            </ServiceRequest>"""

            scans_url = f"{was_url}/qps/rest/3.0/search/was/wasscan"
            scans_response = self.make_request("POST", scans_url, headers=headers, data=xml_body)

            if scans_response.status_code == 200:
                root = self.parse_xml_response(scans_response.text)
                if root is not None:
                    scans = root.findall(".//WasScan")
                    result["scans_found"] = len(scans)

                    if scans:
                        first_scan = scans[0]
                        scan_id = first_scan.findtext("id", "N/A")
                        scan_name = first_scan.findtext("name", "N/A")
                        scan_status = first_scan.findtext("status", "N/A")

                        result["sample_scan"] = {"id": scan_id, "name": scan_name, "status": scan_status}
                        self.logger.info(f"[{module_name}] ✓ Found {len(scans)} WAS scans (last 30 days)")
                else:
                    result["scans_found"] = 0
            else:
                result["scans_found"] = 0
                self.logger.warning(f"[{module_name}] Could not list scans: HTTP {scans_response.status_code}")

        except Exception as e:
            result["scans_found"] = 0
            self.logger.warning(f"[{module_name}] Error listing scans: {e}")

    def _list_container_reports(
        self, gateway_url: str, headers: dict, result: Dict[str, Any], module_name: str
    ) -> None:
        """List Container Security reports (paginated)"""
        try:
            # List first page of reports
            reports_url = f"{gateway_url}/csapi/v1.3/reports?pageNumber=0&pageSize=10"
            reports_response = self.make_request("GET", reports_url, headers=headers)

            if reports_response.status_code == 200:
                try:
                    data = reports_response.json()
                    if isinstance(data, list):
                        result["reports_found"] = len(data)

                        if data:
                            first_report = data[0]
                            report_id = first_report.get("id", "N/A")
                            report_name = first_report.get("name", "N/A")
                            report_status = first_report.get("status", "N/A")

                            result["sample_report"] = {"id": report_id, "name": report_name, "status": report_status}
                            self.logger.info(f"[{module_name}] ✓ Found {len(data)} container reports")
                    else:
                        result["reports_found"] = 0
                except Exception as parse_error:
                    result["reports_found"] = 0
                    self.logger.warning(f"[{module_name}] Error parsing reports: {parse_error}")
            else:
                result["reports_found"] = 0
                self.logger.warning(f"[{module_name}] Could not list reports: HTTP {reports_response.status_code}")

        except Exception as e:
            result["reports_found"] = 0
            self.logger.warning(f"[{module_name}] Error listing reports: {e}")

    def _list_total_cloud_reports(
        self, tc_url: str, headers: dict, auth: HTTPBasicAuth, result: Dict[str, Any], module_name: str
    ) -> None:
        """List Total Cloud assessment reports from the last 30 days"""
        try:
            from datetime import timedelta

            # Calculate date 30 days ago
            date_since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # List assessment reports
            reports_url = f"{tc_url}/api/2.0/fo/compliance/posture/?action=list&evaluated_after={date_since}"
            reports_response = self.make_request("GET", reports_url, headers=headers, auth=auth)

            if reports_response.status_code == 200:
                root = self.parse_xml_response(reports_response.text)
                if root is not None:
                    reports = root.findall(".//ASSESSMENT_REPORT")
                    result["reports_found"] = len(reports)

                    if reports:
                        first_report = reports[0]
                        report_id = first_report.findtext("ID", "N/A")
                        report_title = first_report.findtext("TITLE", "N/A")
                        report_status = first_report.findtext("STATUS", "N/A")

                        result["sample_report"] = {"id": report_id, "title": report_title, "status": report_status}
                        self.logger.info(f"[{module_name}] ✓ Found {len(reports)} assessment reports (last 30 days)")
                else:
                    result["reports_found"] = 0
            else:
                result["reports_found"] = 0
                self.logger.warning(f"[{module_name}] Could not list reports: HTTP {reports_response.status_code}")

        except Exception as e:
            result["reports_found"] = 0
            self.logger.warning(f"[{module_name}] Error listing reports: {e}")

    def test_vmdr(self) -> Dict[str, Any]:
        """
        Test VMDR (Vulnerability Management) APIs

        Note: VMDR uses Basic Authentication (not JWT), following the pattern in
        regscale/integrations/commercial/qualys/vmdr.py
        """
        module_name = "VMDR"
        self.logger.info(f"[{module_name}] Testing Vulnerability Management...")

        result = {
            "status": "failed",
            "host_detections_found": False,
            "policies_found": 0,
            "sample_policy": None,
            "error": None,
            "details": "",
        }

        try:
            # Transform to qualysapi subdomain for VMDR/FO API
            vmdr_url = transform_to_api_url(self.base_url)

            # VMDR uses Basic Auth (username:password), not JWT
            auth = HTTPBasicAuth(self.username, self.password)
            headers = {"X-Requested-With": REGSCALE_CLI_HEADER}

            # Test 1: List host detections (with truncation limit)
            url = f"{vmdr_url}/api/2.0/fo/asset/host/vm/detection/?action=list&truncation_limit=1"
            response = self.make_request("GET", url, headers=headers, auth=auth)

            if response.status_code in [401, 403]:
                result["status"] = "skipped"
                result["error"] = "VMDR module not enabled or access denied"
                result["details"] = f"HTTP {response.status_code}"
                self.logger.warning(self.colorize(f"[{module_name}] ⊘ SKIPPED - Module not enabled", Colors.YELLOW))
                return result

            if response.status_code == 200:
                root = self.parse_xml_response(response.text)
                if root is not None:
                    detections = root.findall(".//DETECTION")
                    result["host_detections_found"] = len(detections) > 0
                    self.logger.info(f"[{module_name}] ✓ Host detections retrieved")

                # Test 2: List compliance policies
                self._check_vmdr_policies(vmdr_url, headers, auth, result, module_name)

                # Test 3: List scan reports
                self._list_vmdr_reports(vmdr_url, headers, auth, result, module_name)

                result["status"] = "passed"
                reports_msg = f", {result.get('reports_found', 0)} scan reports" if "reports_found" in result else ""
                result["details"] = f"Host detections available, {result['policies_found']} policies found{reports_msg}"
                self.logger.info(
                    self.colorize(
                        f"[{module_name}] ✓ PASSED - VMDR APIs accessible",
                        Colors.GREEN,
                    )
                )
            else:
                result["error"] = f"HTTP {response.status_code}"
                result["details"] = response.text[:200]

        except Exception as e:
            result["error"] = str(e)
            result["details"] = traceback.format_exc()
            self.logger.error(self.colorize(f"[{module_name}] ✗ FAILED - {result['error']}", Colors.RED))

        return result

    def run_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic tests"""
        self.start_time = datetime.now()
        self.logger.info(self.colorize("=" * 60, Colors.BOLD))
        self.logger.info(self.colorize("Starting Qualys Diagnostics...", Colors.BOLD))
        self.logger.info(self.colorize("=" * 60, Colors.BOLD))

        # Define all available modules
        all_modules = {
            "jwt": self.test_jwt_auth,
            "total_cloud": self.test_total_cloud,
            "was": self.test_was,
            "container_security": self.test_container_security,
            "vmdr": self.test_vmdr,
        }

        # Filter modules if specified
        if self.modules_filter:
            modules_to_run = {k: v for k, v in all_modules.items() if k in self.modules_filter}
            if not modules_to_run:
                self.logger.error(f"No valid modules specified. Available: {', '.join(all_modules.keys())}")
                sys.exit(1)
        else:
            modules_to_run = all_modules

        # Run JWT auth first (required for other modules)
        if "jwt" in modules_to_run:
            self.results["jwt_auth"] = modules_to_run["jwt"]()

            # Stop if JWT auth failed and user wants to stop on auth failure
            if self.results["jwt_auth"]["status"] == "failed":
                self.logger.error(self.colorize("\nAuthentication failed. Stopping diagnostics.", Colors.RED))
                self.end_time = datetime.now()
                return self.results

        # Run other modules
        for module_key, test_func in modules_to_run.items():
            if module_key == "jwt":
                continue  # Already ran

            self.results[module_key] = test_func()

        self.end_time = datetime.now()

        # Print summary
        self.print_summary()

        return self.results

    def print_summary(self):
        """Print diagnostics summary"""
        duration = (self.end_time - self.start_time).total_seconds()

        passed = sum(1 for r in self.results.values() if r["status"] == "passed")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")
        skipped = sum(1 for r in self.results.values() if r["status"] == "skipped")

        self.logger.info(self.colorize("\n" + "=" * 60, Colors.BOLD))
        self.logger.info(self.colorize("=== DIAGNOSTICS SUMMARY ===", Colors.BOLD))
        self.logger.info(self.colorize("=" * 60, Colors.BOLD))
        self.logger.info(f"Total Tests: {len(self.results)}")
        self.logger.info(self.colorize(f"Passed: {passed}", Colors.GREEN))
        self.logger.info(self.colorize(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN))
        self.logger.info(self.colorize(f"Skipped: {skipped}", Colors.YELLOW))
        self.logger.info(f"Duration: {self.format_duration(duration)}")

    def generate_json_report(self) -> str:
        """Generate JSON report"""
        report = {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "config": {"base_url": self.base_url, "username": self.username},
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results.values() if r["status"] == "passed"),
                "failed": sum(1 for r in self.results.values() if r["status"] == "failed"),
                "skipped": sum(1 for r in self.results.values() if r["status"] == "skipped"),
            },
            "results": self.results,
        }

        return json.dumps(report, indent=2)

    def generate_text_report(self) -> str:
        """Generate human-readable text report"""
        lines = []
        lines.append("=" * 80)
        lines.append("QUALYS DIAGNOSTICS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Base URL: {self.base_url}")
        lines.append(f"Username: {self.username}")
        lines.append(f"Duration: {self.format_duration((self.end_time - self.start_time).total_seconds())}")
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Tests: {len(self.results)}")
        lines.append(f"Passed: {sum(1 for r in self.results.values() if r['status'] == 'passed')}")
        lines.append(f"Failed: {sum(1 for r in self.results.values() if r['status'] == 'failed')}")
        lines.append(f"Skipped: {sum(1 for r in self.results.values() if r['status'] == 'skipped')}")
        lines.append("")

        # Detailed results
        lines.append("DETAILED RESULTS")
        lines.append("-" * 80)

        for module_name, result in self.results.items():
            lines.append(f"\n[{module_name.upper()}]")
            lines.append(f"Status: {result['status'].upper()}")
            lines.append(f"Details: {result.get('details', 'N/A')}")

            if result.get("error"):
                lines.append(f"Error: {result['error']}")

            # Add module-specific details
            for key, value in result.items():
                if key not in ["status", "details", "error"]:
                    lines.append(f"  {key}: {value}")

            lines.append("")

        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)

        failed_modules = [k for k, v in self.results.items() if v["status"] == "failed"]
        if failed_modules:
            lines.append("Failed modules detected:")
            for module in failed_modules:
                lines.append(f"  - {module}: Check credentials and API permissions")
        else:
            lines.append("All tested modules are working correctly!")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def save_reports(self, save_json: bool = True, save_text: bool = True):
        """Save diagnostic reports to files"""
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        timestamp_str = self.start_time.strftime("%Y%m%d_%H%M%S")
        saved_files = []

        # Save JSON report
        if save_json:
            json_path = os.path.join(self.output_dir, f"qualys_diagnostics_{timestamp_str}.json")
            with open(json_path, "w") as f:
                f.write(self.generate_json_report())
            saved_files.append(json_path)
            self.logger.info(f"JSON report saved: {json_path}")

        # Save text report
        if save_text:
            text_path = os.path.join(self.output_dir, f"qualys_diagnostics_{timestamp_str}.txt")
            with open(text_path, "w") as f:
                f.write(self.generate_text_report())
            saved_files.append(text_path)
            self.logger.info(f"Text report saved: {text_path}")

        if saved_files:
            self.logger.info(self.colorize("\nReports saved to:", Colors.BOLD))
            for file_path in saved_files:
                self.logger.info(f"  - {file_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Qualys Diagnostics - Comprehensive API testing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--config", default="init.yaml", help="Path to init.yaml configuration file (default: init.yaml)"
    )

    parser.add_argument(
        "--output-dir",
        default="diagnostics_output",
        help="Directory for output files (default: ./diagnostics_output)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--modules",
        help="Comma-separated list of modules to test (e.g., jwt,vmdr,total_cloud). "
        "Available: jwt, total_cloud, was, container_security, vmdr",
    )

    parser.add_argument("--no-json", action="store_true", help="Skip JSON report generation")

    parser.add_argument("--no-text", action="store_true", help="Skip text report generation")

    args = parser.parse_args()

    # Parse modules filter
    modules_filter = None
    if args.modules:
        modules_filter = [m.strip() for m in args.modules.split(",")]

    # Run diagnostics
    diagnostics = QualysDiagnostics(
        config_path=args.config, output_dir=args.output_dir, verbose=args.verbose, modules=modules_filter
    )

    diagnostics.run_diagnostics()

    # Save reports
    diagnostics.save_reports(save_json=not args.no_json, save_text=not args.no_text)


if __name__ == "__main__":
    main()
