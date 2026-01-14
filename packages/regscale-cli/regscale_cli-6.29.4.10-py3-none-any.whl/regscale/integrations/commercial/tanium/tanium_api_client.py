#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium API Client for RegScale Integration.

This module provides a Python client for interacting with the Tanium platform via REST API.
It supports authentication via session tokens and provides methods for retrieving endpoints,
vulnerabilities, and compliance findings.

Tanium API Documentation: https://developer.tanium.com/
"""

import logging
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("regscale")

# Constants to avoid literal duplication
CONTENT_TYPE_JSON = "application/json"
ERROR_UNEXPECTED_RESPONSE = "Unexpected response type: %s"
API_VULNERABILITIES_ENDPOINT = "/api/v2/comply/vulnerabilities"


class TaniumAPIException(Exception):
    """Exception raised for Tanium API errors."""

    pass


class TaniumAPIClient:
    """
    Python client for Tanium REST API.

    Handles authentication, query execution, and result retrieval from Tanium.
    Uses session token authentication for API access.

    Example usage:
        >>> client = TaniumAPIClient(
        ...     base_url="https://tanium.example.com",
        ...     api_token="token-12345678-1234-1234-1234-123456789012"
        ... )
        >>> endpoints = client.get_endpoints()
    """

    # Default timeout for requests (30 seconds)
    DEFAULT_TIMEOUT = 30

    # Default page size for pagination
    DEFAULT_PAGE_SIZE = 100

    def __init__(
        self,
        base_url: str,
        api_token: str,
        verify_ssl: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        protocols: str = "https",
    ):
        """
        Initialize Tanium API client.

        Args:
            base_url: Tanium instance base URL (e.g., "https://tanium.example.com")
            api_token: Tanium API token for session authentication
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            protocols: Comma-separated list of allowed protocols (e.g., "https" or "https,http")
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.protocols = [p.strip() for p in protocols.split(",")]

        # Create session with retry capability
        self.session = self._create_session(max_retries)

        # Set authentication and content type headers
        self.session.headers.update(
            {
                "session": self.api_token,
                "Content-Type": CONTENT_TYPE_JSON,
                "Accept": CONTENT_TYPE_JSON,
            }
        )

        logger.info("Tanium API client initialized for %s", self.base_url)

    def _create_session(self, max_retries: int) -> requests.Session:
        """
        Create a requests session with retry capability.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()

        # Configure retry strategy for transient errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        # Mount adapters only for configured protocols
        for protocol in self.protocols:
            protocol_lower = protocol.lower()
            if protocol_lower in ["http", "https"]:
                session.mount(f"{protocol_lower}://", adapter)
                logger.debug("Mounted adapter for protocol: %s", protocol_lower)
            else:
                logger.warning("Ignoring unsupported protocol: %s", protocol)

        if not self.verify_ssl:
            # Disable SSL warnings if verification is disabled
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning("SSL verification is disabled - not recommended for production")

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Make an HTTP request to the Tanium API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            headers: Additional headers (overrides session headers)

        Returns:
            Response data (JSON dict or text)

        Raises:
            TaniumAPIException: If the request fails
        """
        url = "%s%s" % (self.base_url, endpoint)

        # Merge additional headers with session headers
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Return JSON if content-type is JSON, otherwise return text
            content_type = response.headers.get("Content-Type", "")
            if CONTENT_TYPE_JSON in content_type:
                return response.json()
            else:
                return response.text

        except requests.exceptions.HTTPError as e:
            error_msg = "HTTP %s: %s" % (e.response.status_code, e.response.text)
            logger.error("Tanium API request failed: %s", error_msg)
            raise TaniumAPIException(error_msg) from e

        except requests.exceptions.RequestException as e:
            logger.error("Tanium API request failed: %s", str(e))
            raise TaniumAPIException("Request failed: %s" % str(e)) from e

    def test_connection(self) -> bool:
        """
        Test the connection to Tanium API.

        Returns:
            True if connection is successful

        Raises:
            TaniumAPIException: If connection test fails
        """
        try:
            response = self._make_request("GET", "/api/v2/session/info")

            if isinstance(response, dict):
                user_name = response.get("data", {}).get("userName", "Unknown")
                logger.info("Successfully connected to Tanium as user: %s", user_name)

            return True
        except TaniumAPIException as exc:
            logger.error("Connection test failed: %s", str(exc))
            raise

    def get_server_info(self) -> Dict[str, Any]:
        """
        Get Tanium server information.

        Returns:
            Server info dictionary

        Raises:
            TaniumAPIException: If request fails
        """
        response = self._make_request("GET", "/api/v2/session/info")

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", {})

    def get_endpoints(
        self,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Fetch endpoints/assets from Tanium.

        Args:
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of endpoint records

        Raises:
            TaniumAPIException: If request fails
        """
        params = {"limit": limit, "offset": offset}
        response = self._make_request("GET", "/api/v2/endpoints", params=params)

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", [])

    def get_endpoint_by_id(self, endpoint_id: int) -> Dict[str, Any]:
        """
        Fetch a single endpoint by ID.

        Args:
            endpoint_id: The endpoint ID

        Returns:
            Endpoint record

        Raises:
            TaniumAPIException: If request fails
        """
        response = self._make_request("GET", "/api/v2/endpoints/%s" % endpoint_id)

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", {})

    def get_all_endpoints(self, page_size: int = DEFAULT_PAGE_SIZE) -> List[Dict[str, Any]]:
        """
        Fetch all endpoints with pagination support.

        Args:
            page_size: Number of results per page

        Returns:
            List of all endpoint records

        Raises:
            TaniumAPIException: If request fails
        """
        all_endpoints: List[Dict[str, Any]] = []
        offset = 0

        while True:
            params = {"limit": page_size, "offset": offset}
            response = self._make_request("GET", "/api/v2/endpoints", params=params)

            if not isinstance(response, dict):
                raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

            data = response.get("data", [])
            all_endpoints.extend(data)

            # Check if there are more results
            pagination = response.get("pagination", {})
            has_more = pagination.get("hasMore", False)

            if not has_more or not data:
                break

            offset += page_size
            logger.debug("Fetched %s endpoints, continuing pagination...", len(all_endpoints))

        logger.info("Retrieved total of %s endpoints", len(all_endpoints))
        return all_endpoints

    def get_vulnerabilities(
        self,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch vulnerabilities from Tanium Comply module.

        Args:
            limit: Maximum number of results to return
            offset: Offset for pagination
            severity: Filter by severity (Critical, High, Medium, Low)

        Returns:
            List of vulnerability records

        Raises:
            TaniumAPIException: If request fails
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if severity:
            params["severity"] = severity

        response = self._make_request("GET", API_VULNERABILITIES_ENDPOINT, params=params)

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", [])

    def get_vulnerabilities_for_endpoint(
        self,
        endpoint_id: int,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Fetch vulnerabilities for a specific endpoint.

        Args:
            endpoint_id: The endpoint ID
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of vulnerability records for the endpoint

        Raises:
            TaniumAPIException: If request fails
        """
        params = {"limit": limit, "offset": offset, "endpointId": endpoint_id}
        response = self._make_request("GET", API_VULNERABILITIES_ENDPOINT, params=params)

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", [])

    def get_all_vulnerabilities(self, page_size: int = DEFAULT_PAGE_SIZE) -> List[Dict[str, Any]]:
        """
        Fetch all vulnerabilities with pagination support.

        Args:
            page_size: Number of results per page

        Returns:
            List of all vulnerability records

        Raises:
            TaniumAPIException: If request fails
        """
        all_vulns: List[Dict[str, Any]] = []
        offset = 0

        while True:
            params = {"limit": page_size, "offset": offset}
            response = self._make_request("GET", API_VULNERABILITIES_ENDPOINT, params=params)

            if not isinstance(response, dict):
                raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

            data = response.get("data", [])
            all_vulns.extend(data)

            # Check if there are more results
            pagination = response.get("pagination", {})
            has_more = pagination.get("hasMore", False)

            if not has_more or not data:
                break

            offset += page_size
            logger.debug("Fetched %s vulnerabilities, continuing pagination...", len(all_vulns))

        logger.info("Retrieved total of %s vulnerabilities", len(all_vulns))
        return all_vulns

    def get_compliance_findings(
        self,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch compliance findings from Tanium Comply module.

        Args:
            limit: Maximum number of results to return
            offset: Offset for pagination
            status: Filter by status (Pass, Fail, Error, NotApplicable)

        Returns:
            List of compliance finding records

        Raises:
            TaniumAPIException: If request fails
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        response = self._make_request("GET", "/api/v2/comply/findings", params=params)

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", [])

    def get_compliance_findings_for_endpoint(
        self,
        endpoint_id: int,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Fetch compliance findings for a specific endpoint.

        Args:
            endpoint_id: The endpoint ID
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of compliance finding records for the endpoint

        Raises:
            TaniumAPIException: If request fails
        """
        params = {"limit": limit, "offset": offset, "endpointId": endpoint_id}
        response = self._make_request("GET", "/api/v2/comply/findings", params=params)

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", [])

    def get_compliance_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Fetch available compliance benchmarks.

        Returns:
            List of compliance benchmark records

        Raises:
            TaniumAPIException: If request fails
        """
        response = self._make_request("GET", "/api/v2/comply/benchmarks")

        if not isinstance(response, dict):
            raise TaniumAPIException(ERROR_UNEXPECTED_RESPONSE % type(response).__name__)

        return response.get("data", [])


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Example: Connect to Tanium and fetch endpoints
    # NOTE: Replace with actual Tanium instance details
    client = TaniumAPIClient(
        base_url="https://tanium.example.com",
        api_token="token-12345678-1234-1234-1234-123456789012",
        verify_ssl=False,  # Set to True in production
        protocols="https",  # Use "https,http" to allow both protocols
    )

    # Test connection
    try:
        client.test_connection()
        print("Connection successful!")
    except TaniumAPIException as e:
        print("Connection failed: %s" % e)

    # Fetch endpoints
    try:
        endpoints = client.get_endpoints(limit=10)
        print("Retrieved %s endpoints" % len(endpoints))
        for endpoint in endpoints[:3]:
            print("  - %s" % endpoint.get("computerName", "Unknown"))
    except TaniumAPIException as e:
        print("Query failed: %s" % e)
