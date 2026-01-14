"""
Container operations module for Qualys CS API integration.
"""

import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from json import JSONDecodeError
from typing import Dict, List, Optional
from urllib.parse import urljoin

from requests import RequestException
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Create logger for this module
logger = logging.getLogger("regscale")


def _extract_jwt_token(response) -> Optional[str]:
    """
    Extract JWT token from authentication response

    :param response: HTTP response object
    :return: JWT token or None if not found
    :rtype: Optional[str]
    """
    content_type = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
        try:
            response_json = response.json()
            access_token = response_json.get("access_token")
            logger.debug("JWT token acquired (JSON format)")
            return access_token
        except (JSONDecodeError, AttributeError) as e:
            logger.warning("Could not parse JSON response for Authorization header: %s", e)
            logger.debug("Response content: %s", response.text)
            return None

    if "text/plain" in content_type or not content_type:
        access_token = response.text.strip()
        logger.debug("JWT token acquired (plain text format)")
        return access_token

    logger.warning("Unexpected Content-Type for JWT response: %s", content_type)
    logger.debug("Response content: %s", response.text[:200])
    return None


def _handle_auth_failure(response, auth_url: str) -> None:
    """
    Handle authentication failure and raise appropriate exception

    :param response: HTTP response object
    :param str auth_url: Authentication URL attempted
    """
    logger.error("Container Security Auth - Authentication FAILED")
    logger.error("Container Security Auth - Status code: %s", response.status_code)
    logger.error("Container Security Auth - Response body: %s", response.text[:500])
    logger.error("Container Security Auth - Request URL was: %s", auth_url)

    if response.status_code == 401:
        logger.error("Container Security Auth - TROUBLESHOOTING:")
        logger.error("  1. Verify Container Security module is enabled in your Qualys account")
        logger.error("  2. Verify credentials have Container Security API permissions")
        logger.error("  3. Contact Qualys support if Container Security is not available")

    raise RequestException(f"Authentication failed with status code: {response.status_code}")


@lru_cache(maxsize=1)
def auth_cs_api() -> tuple[str, dict]:
    """
    Authenticate the Qualys CS API using form-based authentication

    :return: A tuple of the base URL and a dictionary of headers
    :rtype: tuple[str, dict]
    """
    from . import _get_config  # noqa: C0415

    config = _get_config()
    qualys_url = config.get("qualysMockUrl") or config.get("qualysUrl")
    user = config.get("qualysUserName")
    password = config.get("qualysPassword")

    logger.debug("Container Security: Authenticating to %s", qualys_url)

    auth_headers = {"X-Requested-With": "RegScale CLI"}
    auth_data = {"username": user, "password": password, "permissions": "true", "token": "true"}

    try:
        # Transform URL for gateway endpoint
        base_url = (
            qualys_url.replace("qualysguard", "gateway") if qualys_url and "qualysguard" in qualys_url else qualys_url
        )
        if base_url != qualys_url:
            logger.debug("Container Security: Transformed qualysguard -> gateway")

        auth_url = urljoin(base_url, "/csapi/v1.3/auth")
        logger.debug("Container Security: Authenticating to %s", auth_url)

        # Use a separate session for CS API (don't use QUALYS_API with Basic Auth)
        from requests import Session  # noqa: C0415

        cs_session = Session()
        cs_session.verify = True
        response = cs_session.post(url=auth_url, headers=auth_headers, data=auth_data)

        logger.debug("Container Security Auth - Response status: %s", response.status_code)
        logger.debug("Container Security Auth - Response headers: %s", dict(response.headers))

        if response.ok:
            logger.debug("Container Security: Authentication successful")
            access_token = _extract_jwt_token(response)

            if access_token:
                auth_headers["Authorization"] = f"Bearer {access_token}"
                logger.debug("Added Authorization Bearer header to auth_headers")
            else:
                logger.warning("No access_token found in authentication response")
        else:
            _handle_auth_failure(response, auth_url)

    except Exception as e:
        logger.error("Container Security Auth - Exception during authentication: %s", e)
        logger.error("Container Security Auth - Exception type: %s", type(e).__name__)
        import traceback

        logger.debug("Container Security Auth - Full traceback: %s", traceback.format_exc())
        raise

    return base_url, auth_headers


def _make_api_request(current_url: str, headers: dict, params: Optional[Dict] = None) -> dict:
    """
    Make API request to fetch containers from Qualys CS API

    :param str current_url: The URL for the API request
    :param dict headers: Headers to include in the request
    :param Dict params: Optional query parameters for pagination
    :return: Response data containing containers and response object
    :rtype: dict
    """
    from requests import Session  # noqa: C0415

    # Create a separate session for Container Security API (JWT auth)
    # Don't use QUALYS_API global since it has Basic Auth configured
    cs_session = Session()
    cs_session.verify = True  # SSL verification

    # Make API request
    response = cs_session.get(url=current_url, headers=headers, params=params)

    # Validate response
    if not response.ok:
        logger.error("API request failed: %s - %s", response.status_code, response.text)
        return {"data": [], "_response": response}

    try:
        response_data = response.json()
        response_data["_response"] = response  # Include response object for headers
        return response_data
    except JSONDecodeError as e:
        logger.error("Failed to parse JSON response: %s", e)
        return {"data": [], "_response": response}


def _parse_link_header(link_header: str) -> Optional[str]:
    """
    Parse the Link header to find the next page URL.

    :param str link_header: The Link header value
    :return: The next page URL or None if not found
    :rtype: Optional[str]
    """
    if not link_header:
        logger.debug("No Link header found, assuming no more pages")
        return None

    # Parse the Link header to find the next page URL
    # Format: <url>;rel=next
    for link in link_header.split(","):
        link = link.strip()
        if "rel=next" in link:
            # Extract URL from <url>;rel=next format
            url_start = link.find("<") + 1
            url_end = link.find(">")
            if 0 < url_start < url_end:
                return link[url_start:url_end]

    logger.debug("No next page URL found in Link header")
    return None


def _fetch_paginated_data(endpoint: str, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Generic function to fetch paginated data from Qualys CS API

    :param str endpoint: The API endpoint (e.g., 'containers/list', 'images/list')
    :param Optional[Dict] filters: Filters to apply to the request
    :param int limit: Number of items to fetch per page
    :return: A list of items from all pages
    :rtype: List[Dict]
    """
    all_items = []
    page: int = 1
    current_url = None  # Ensure current_url is always defined

    try:
        # Get authentication
        base_url, headers = auth_cs_api()

        # Prepare base parameters
        params = {"limit": limit}

        # Add filters if provided
        if filters:
            params.update(filters)

        # Track the current URL for pagination
        current_url = urljoin(base_url, f"/csapi/v1.3/{endpoint}")

        # Create progress bar for pagination
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
            task = progress.add_task(f"[green]Fetching {endpoint} data...", total=None)  # Unknown total for pagination

            while current_url:
                # Make API request
                response_data = _make_api_request(current_url, headers, params)

                # Extract items from current page
                current_items = response_data.get("data", [])
                all_items.extend(current_items)

                # Update progress description with current status
                progress.update(
                    task, description=f"[green]Fetching {endpoint} data... (Page {page}, Total: {len(all_items)})"
                )

                logger.debug("Fetched page: %s items (Total so far: %s)", page, len(all_items))

                # Check for next page using the Link header
                response = response_data.get("_response")
                if not response or not hasattr(response, "headers"):
                    # If no response object available, assume single page
                    break

                link_header = response.headers.get("link", "")
                next_url = _parse_link_header(link_header)

                if not next_url:
                    break

                # Update current URL for next iteration
                current_url = next_url
                page += 1

                # Clear params for subsequent requests since they're in the URL
                params = {}
            progress.update(task, total=len(all_items))
            progress.update(task, completed=len(all_items))

    except Exception as e:
        logger.error("Error fetching data from %s: %s", current_url if current_url else "N/A", e)
        logger.debug(traceback.format_exc())

    logger.info("Completed: Fetched %s total items from %s", len(all_items), endpoint)
    return all_items


def fetch_all_containers(filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Fetch all containers from Qualys CS API with pagination

    :param Optional[Dict] filters: Filters to apply to the containers
    :param int limit: Number of containers to fetch per page
    :return: A list of containers
    :rtype: List[Dict]
    """
    return _fetch_paginated_data("containers", filters, limit)


def fetch_all_images(filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Fetch all images from Qualys CS API with pagination

    :param Optional[Dict] filters: Filters to apply to the images
    :param int limit: Number of images to fetch per page
    :return: A list of images
    :rtype: List[Dict]
    """
    return _fetch_paginated_data("images", filters, limit)


def fetch_container_vulns(container_sha: str) -> List[Dict]:
    """
    Fetch vulnerabilities for a specific container from Qualys CS API using container SHA

    :param str container_sha: The SHA of the container
    :return: A list of vulnerabilities
    :rtype: List[Dict]
    """
    base_url, headers = auth_cs_api()
    current_url = urljoin(base_url, f"/csapi/v1.3/containers/{container_sha}/vuln")
    response_data = _make_api_request(current_url, headers)
    return response_data.get("details", {}).get("vulns", [])


def fetch_container_report(report_id: str) -> Dict:
    """
    Fetch detailed vulnerability report for a container from Qualys CS API using report ID

    :param str report_id: The report ID of the container
    :return: Dictionary containing report data with vulnerabilities array
    :rtype: Dict
    """
    base_url, headers = auth_cs_api()
    current_url = urljoin(base_url, f"/csapi/v1.3/reports/{report_id}")
    response_data = _make_api_request(current_url, headers)
    return response_data


def fetch_all_vulnerabilities(filters: Optional[Dict] = None, limit: int = 100, max_workers: int = 10) -> List[Dict]:
    """
    Fetch all containers and a list of vulnerabilities for each container from Qualys CS API with pagination

    :param Optional[Dict] filters: Filters to apply to the containers
    :param int limit: Number of containers to fetch per page
    :param int max_workers: Maximum number of worker threads for concurrent vulnerability fetching
    :return: A list of containers with vulnerabilities
    :rtype: List[Dict]
    """
    containers = fetch_all_containers(filters, limit)

    if not containers:
        logger.info("No containers found to fetch vulnerabilities for")
        return containers

    # Create progress bar for fetching vulnerabilities
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=None,
    )

    def fetch_container_vulns_with_progress(container):
        """Helper function to fetch vulnerabilities for a single container with progress tracking."""
        # Try reportId first (Mock API and some production scenarios)
        report_id = container.get("reportId")
        container_id = container.get("containerId", "unknown")

        if report_id:
            try:
                # Fetch full report with vulnerabilities
                report_data = fetch_container_report(report_id)
                vulns = report_data.get("vulnerabilities", [])
                logger.debug(
                    "Fetched %s vulnerabilities for container %s using reportId", len(vulns), container_id[:12]
                )
                return container, vulns
            except Exception as e:
                logger.error("Error fetching report %s for container %s: %s", report_id, container_id, e)
                return container, []

        # Fallback to SHA-based fetch (production scenarios without reportId)
        container_sha = container.get("sha")
        if container_sha:
            try:
                vulns = fetch_container_vulns(container_sha)
                logger.debug("Fetched %s vulnerabilities for container %s using SHA", len(vulns), container_sha[:8])
                return container, vulns
            except Exception as e:
                logger.error("Error fetching vulnerabilities for container SHA %s: %s", container_sha, e)
                return container, []

        # No reportId or SHA available
        logger.warning("Container %s missing both reportId and SHA, skipping vulnerability fetch", container_id)
        return container, []

    with progress:
        task = progress.add_task(
            f"[yellow]Fetching vulnerabilities for {len(containers)} containers...", total=len(containers)
        )

        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_container = {}
            for container in containers:
                future = executor.submit(fetch_container_vulns_with_progress, container)
                future_to_container[future] = container

            # Process completed tasks and update progress
            for future in as_completed(future_to_container):
                container, vulns = future.result()
                container["vulnerabilities"] = vulns
                progress.update(task, advance=1)

    logger.info("Completed fetching vulnerabilities for %s containers using %s workers", len(containers), max_workers)
    return containers


# ==================================================================================
# Container Security Report Listing Functions
# ==================================================================================


def list_container_reports(days: int) -> list:
    """
    List Container Security vulnerability reports from the last N days.

    NOTE: Container Security API does not support date filtering on the /csapi/v1.3/reports
    endpoint. This function returns an empty list with a warning log message when called
    with a days parameter, as per the approved implementation plan.

    To fetch all Container Security reports (without date filtering), use the full
    fetch_all_containers() and fetch_all_container_vulnerabilities() functions instead.

    :param int days: Number of days to look back (not supported by Container Security API)
    :return: Empty list (date filtering not supported)
    :rtype: List[ScanSummary]
    """
    logger.warning(
        "Container Security API does not support date filtering. "
        "Use fetch_all_containers() to retrieve all container data. "
        "Skipping Container Security reports for list_scans command."
    )
    return []
