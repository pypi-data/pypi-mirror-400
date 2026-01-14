"""
Prisma Scan information
"""

from concurrent.futures import ThreadPoolExecutor
from itertools import groupby
from operator import attrgetter
from threading import Lock
from typing import Any, List, Optional, Union

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import IssueStatus, SoftwareInventory

# Import helper functions from prisma_modules
try:
    from prisma_modules import (
        validate_cve_format,
        validate_cvss_score,
        map_cvss_to_severity,
        split_comma_separated_values,
        build_asset_properties,
        build_finding_properties,
        parse_software_package,
    )
except ImportError:
    # Fallback for development/testing without prisma_modules
    from regscale.integrations.commercial.prisma_modules import (
        validate_cve_format,
        validate_cvss_score,
        map_cvss_to_severity,
        split_comma_separated_values,
        build_asset_properties,
        build_finding_properties,
        parse_software_package,
    )

FIX_STATUS = "Fix Status"
VULNERABILITY_ID = "Vulnerability ID"
CVE_ID = "CVE ID"
RISK_FACTORS = "Risk Factors"
PACKAGE_LICENSE = "Package License"
PACKAGE_VERSION = "Package Version"
VULNERABILITY_TAGS = "Vulnerability Tags"
VULNERABILITY_LINK = "Vulnerability Link"
PACKAGE_PATH = "Package Path"
SOURCE_PACKAGE = "Source Package"
CUSTOM_LABELS = "Custom Labels"
IMAGE_ID = "Image ID"
IMAGE_NAME = "Image Name"


class Prisma(FlatFileImporter):
    """
    Prisma Scan information
    """

    @staticmethod
    def import_prisma_files_with_inventory(**kwargs):
        """
        Import Prisma CSV files including optional software inventory.

        This method handles the complete import lifecycle:
        1. Import assets and findings via FlatFileImporter
        2. Optionally create software inventory after assets have IDs

        :param kwargs: All FlatFileImporter.import_files parameters plus enable_software_inventory
        :return: None
        """
        from pathlib import Path

        from regscale.core.app.application import Application

        enable_inventory = kwargs.pop("enable_software_inventory", False)
        app = Application()

        # First, import assets and findings normally
        app.logger.info("Starting Prisma import (assets and findings)...")
        FlatFileImporter.import_files(
            import_type=Prisma,
            import_name="Prisma",
            file_types=".csv",
            **kwargs,
        )

        # If software inventory enabled, process it now that assets have IDs
        if enable_inventory:
            app.logger.info("Assets synced. Now processing software inventory...")

            # Get the folder path and object_id from kwargs
            folder_path = Path(kwargs.get("folder_path"))
            object_id = kwargs.get("object_id")
            scan_date = kwargs.get("scan_date")
            mappings_path = kwargs.get("mappings_path")
            disable_mapping = kwargs.get("disable_mapping", False)

            # Find CSV files - check both original folder and processed subfolder
            files = list(folder_path.glob("*.csv"))
            processed_folder = folder_path / "processed"
            if processed_folder.exists():
                files.extend(processed_folder.glob("*.csv"))

            if not files:
                app.logger.warning("No CSV files found for software inventory processing.")
                return

            # Fetch existing assets from RegScale for the security plan
            from regscale.models.regscale_models import Asset

            app.logger.info(f"Fetching assets from RegScale for security plan {object_id}...")
            try:
                regscale_assets = Asset.get_all_by_parent(object_id, "securityplans", app)
                app.logger.info(f"Found {len(regscale_assets)} assets in RegScale.")
            except Exception as e:
                app.logger.error(f"Error fetching assets from RegScale: {e}", exc_info=True)
                return

            if not regscale_assets:
                app.logger.warning("No assets found in RegScale. Cannot process software inventory.")
                return

            # Process software inventory for each file
            for file in files:
                try:
                    app.logger.info(f"Processing software inventory from {file.name}...")
                    prisma_instance = Prisma(
                        name="Prisma",
                        file_path=str(file),
                        object_id=object_id,
                        scan_date=scan_date,
                        mappings_path=mappings_path,
                        disable_mapping=disable_mapping,
                        enable_software_inventory=False,  # Don't trigger in __init__
                        upload_file=False,  # Already uploaded in first pass
                        file_type=file.suffix,
                    )

                    # Now call create_software_inventory with the fetched assets
                    prisma_instance.create_software_inventory(
                        enable_software_inventory=True, scanned_assets=regscale_assets
                    )

                except Exception as e:
                    app.logger.error(f"Error processing software inventory for {file.name}: {e}", exc_info=True)

            app.logger.info("Software inventory processing complete.")

    def _deduplicate_csv_rows(self):
        """
        Deduplicate CSV rows based on (Hostname, CVE ID) to prevent duplicate
        integrationFindingId values in the same batch submission.

        This handles cases where Prisma Cloud CSV exports contain duplicate rows for
        the same vulnerability on the same host. We keep the first occurrence of each
        unique (hostname, cve_id) combination.
        """
        if not hasattr(self, "file_data") or not self.file_data:
            return

        seen_combinations = set()
        deduplicated_data = []
        duplicate_count = 0

        for row in self.file_data:
            hostname = self.mapping.get_value(row, "Hostname")
            cve_id = self.mapping.get_value(row, CVE_ID)

            # Create unique key from hostname and CVE
            row_key = (hostname, cve_id)

            if row_key not in seen_combinations:
                seen_combinations.add(row_key)
                deduplicated_data.append(row)
            else:
                duplicate_count += 1

        if duplicate_count > 0:
            self.attributes.logger.info(
                f"Deduplicated {duplicate_count} duplicate CSV rows "
                f"(original: {len(self.file_data)}, deduplicated: {len(deduplicated_data)})"
            )
            self.file_data = deduplicated_data

    @staticmethod
    def _split_hostnames(hostname: Optional[str]) -> List[str]:
        """
        Split comma-separated hostnames and strip whitespace using prisma_modules helper.

        :param Optional[str] hostname: Hostname string that may contain comma-separated values
        :return: List of individual hostnames, or empty list/single hostname if None
        :rtype: List[str]
        """
        if not hostname:
            return []

        # Use helper function from prisma_modules
        hostnames = split_comma_separated_values(hostname)
        return hostnames if hostnames else [hostname]

    def _create_asset_dict(
        self,
        hostname: str,
        ip_address: Optional[str] = None,
        distro: Optional[str] = None,
        image_name: Optional[str] = None,
        image_id: Optional[str] = None,
    ) -> dict:
        """
        Create asset dictionary with common properties using prisma_modules helper.
        Supports both host/VM assets and container image assets.

        :param str hostname: The hostname for the asset or container image name
        :param Optional[str] ip_address: IP address for the asset (hosts only)
        :param Optional[str] distro: Distribution/OS information
        :param Optional[str] image_name: Container image name (containers only)
        :param Optional[str] image_id: Container image ID/digest (containers only)
        :return: Dictionary of asset properties
        :rtype: dict
        """
        # Use helper function from prisma_modules
        properties = build_asset_properties(
            hostname=hostname,
            ip_address=ip_address,
            distro=distro,
            image_name=image_name,
            image_id=image_id,
            scanning_tool=self.name or "Prisma",
            # Additional Prisma-specific properties
            status="Active (On Network)",
        )

        return properties

    def _create_finding_dict(self, dat: dict, hostname: str, seen) -> dict:
        """
        Create vulnerability finding dictionary using prisma_modules helper.

        :param dict dat: Data row from CSV file
        :param str hostname: The hostname for the finding
        :param seen: Timestamp for first seen/scan date
        :return: Dictionary of finding properties
        :rtype: dict
        """
        # Extract data from CSV row
        cve = self.mapping.get_value(dat, CVE_ID)
        description = self.mapping.get_value(dat, "Description")
        cvss3_score = self.mapping.get_value(dat, self.cvss3_score)
        solution = self.mapping.get_value(dat, "Solution")
        fix_status = self.mapping.get_value(dat, FIX_STATUS)
        package_name = self.mapping.get_value(dat, SOURCE_PACKAGE)
        package_version = self.mapping.get_value(dat, PACKAGE_VERSION)

        # Validate and convert CVSS score
        validated_cvss = validate_cvss_score(cvss3_score) if cvss3_score else None

        # Use helper function from prisma_modules
        properties = build_finding_properties(
            cve=cve or "UNKNOWN",
            cvss_score=validated_cvss,
            title=self.mapping.get_value(dat, self.vuln_title) or cve,
            description=description,
            recommendation=solution or fix_status,
            package_name=package_name,
            package_version=package_version,
            asset_identifier=hostname,
        )

        # Add Prisma-specific properties not handled by helper
        properties.update(
            {
                "control_labels": [],
                "status": IssueStatus.Open,
                "first_seen": seen,
                "scan_date": seen,
                "vulnerability_type": "Vulnerability Scan",
                "baseline": f"{self.name} Host" if self.name else "Prisma Host",
                "plugin_text": description[:255] if description else "",
            }
        )

        # Override category if asset is hardware
        properties["category"] = "Hardware"

        return properties

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        regscale_ssp_id = kwargs.get("object_id")
        self.image_name = "Id"
        self.vuln_title = CVE_ID
        self.cvss3_score = "CVSS"
        self.required_headers = ["Hostname", "Distro", "CVSS", "CVE ID", "Description", "Fix Status"]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")

        # Extract enable_software_inventory before passing kwargs to parent
        self.enable_software_inventory = kwargs.pop("enable_software_inventory", False)

        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            extra_headers_allowed=True,
            ignore_validation=True,
            **kwargs,
        )

        # Deduplicate CSV rows to prevent duplicate integrationFindingId values in same batch
        # This handles cases where the CSV export contains duplicate rows
        self._deduplicate_csv_rows()

        # Note: Software inventory creation is disabled in __init__ because it requires
        # assets to be created in RegScale first (to get asset IDs). The FlatFileImporter
        # pattern calls __init__ before assets are synced to the server.
        #
        # Software inventory can be enabled via CLI flag and will run after asset sync.
        # Future work: Add post-sync lifecycle hook to FlatFileImporter base class
        # to support automatic software inventory creation after asset synchronization.

    def create_asset(self, dat: Optional[dict] = None) -> Union[IntegrationAsset, List[IntegrationAsset]]:
        """
        Create an asset or list of assets from a row in the Prisma csv file.
        If hostname contains comma-separated values, creates separate assets for each.

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationAsset object or list of IntegrationAsset objects
        :rtype: Union[IntegrationAsset, List[IntegrationAsset]]
        """
        hostname = self.mapping.get_value(dat, "Hostname")
        distro = self.mapping.get_value(dat, "Distro")
        ip_address = self.mapping.get_value(dat, "IP Address")

        # Split hostnames (handles comma-separated values)
        hostnames = self._split_hostnames(hostname)

        # Create assets for each hostname
        assets = [IntegrationAsset(**self._create_asset_dict(host, ip_address, distro)) for host in hostnames]

        # Return single asset or list based on count
        return assets[0] if len(assets) == 1 else assets

    def create_vuln(
        self, dat: Optional[dict] = None, **kwargs
    ) -> Union[IntegrationFinding, List[IntegrationFinding], None]:
        """
        Create IntegrationFinding(s) from a row in the Prisma csv file.
        If hostname contains comma-separated values, creates separate findings for each host.
        Uses prisma_modules helper functions for CVE validation and severity mapping.

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationFinding object, list of IntegrationFinding objects, or None
        :rtype: Union[IntegrationFinding, List[IntegrationFinding], None]
        """
        if not dat:
            return None

        # Extract CVE and validate format
        cve = self.mapping.get_value(dat, CVE_ID)
        validated_cve = validate_cve_format(cve) if cve else None

        if not validated_cve:
            self.attributes.logger.warning(
                f"Skipping row with invalid or missing CVE: {cve}. "
                f"Hostname: {self.mapping.get_value(dat, 'Hostname')}"
            )
            return None

        # Get hostname
        hostname: str = self.mapping.get_value(dat, "Hostname")
        if not hostname:
            self.attributes.logger.warning(f"Skipping row with missing hostname for CVE: {validated_cve}")
            return None

        # Get timestamp
        seen = epoch_to_datetime(self.create_epoch)

        # Split hostnames (handles comma-separated values)
        # Note: _split_hostnames always returns non-empty list when hostname is truthy
        hostnames = self._split_hostnames(hostname)

        # Create findings for each hostname
        findings = [IntegrationFinding(**self._create_finding_dict(dat, host, seen)) for host in hostnames]

        # Return single finding or list based on count
        return findings[0] if len(findings) == 1 else findings

    def _fetch_existing_inventory(self, scanned_assets: List) -> set:
        """
        Fetch existing software inventory from RegScale for deduplication.

        :param List scanned_assets: List of scanned assets
        :return: Set of (name, version, parent_asset_id) tuples
        :rtype: set
        """
        existing_inventory_set = set()
        for asset in scanned_assets:
            try:
                existing = SoftwareInventory.fetch_by_asset(self.attributes.app, asset.id)
                for inv in existing:
                    existing_inventory_set.add((inv.name, inv.version, inv.parentHardwareAssetId))
            except Exception as e:
                self.attributes.logger.error(f"Error fetching existing inventory for asset {asset.id}: {e}")
        return existing_inventory_set

    def _process_package_row(
        self, row: dict, key: str, parent_asset_id: int, existing_inventory_set: set, packages_to_create: dict
    ) -> bool:
        """
        Process a single CSV row to extract package data.

        :param dict row: CSV row data
        :param str key: Hostname key
        :param int parent_asset_id: Parent asset ID
        :param set existing_inventory_set: Set of existing packages
        :param dict packages_to_create: Dict of packages to create
        :return: True if package was added, False otherwise
        :rtype: bool
        """
        package_data = {
            "name": self.mapping.get_value(row, SOURCE_PACKAGE),
            "version": self.mapping.get_value(row, PACKAGE_VERSION),
            "license": self.mapping.get_value(row, PACKAGE_LICENSE),
        }

        parsed_package = parse_software_package(package_data=package_data, asset_identifier=key)
        if not parsed_package:
            self.attributes.logger.debug(f"Skipping invalid package data for {key}")
            return False

        package_key = (parsed_package["name"], parsed_package["version"], parent_asset_id)

        # Check if already exists
        if package_key in existing_inventory_set or package_key in packages_to_create:
            return False

        # Create SoftwareInventory object
        inv = SoftwareInventory(
            name=parsed_package["name"],
            version=parsed_package["version"],
            license=parsed_package.get("license"),
            createdById=self.config["userId"],
            dateCreated=get_current_datetime(),
            lastUpdatedById=self.config["userId"],
            isPublic=True,
            parentHardwareAssetId=parent_asset_id,
        )

        packages_to_create[package_key] = inv
        return True

    def _batch_create_packages(self, packages_to_create: dict) -> List[SoftwareInventory]:
        """
        Batch create software packages using old batch_create endpoint.

        :param dict packages_to_create: Dict of packages to create
        :return: List of created SoftwareInventory objects
        :rtype: List[SoftwareInventory]
        """
        if not packages_to_create:
            self.attributes.logger.info("No new packages to create.")
            return []

        try:
            from regscale.core.app.api import Api

            api = Api()
            packages_list = list(packages_to_create.values())
            packages_dicts = [pkg.dict() for pkg in packages_list]

            response = api.post(
                url=self.attributes.app.config["domain"] + "/api/softwareinventory/batchCreate", json=packages_dicts
            )

            if response.status_code == 200 and response.ok:
                created_data = response.json()
                created_packages = [SoftwareInventory(**item) for item in created_data]
                self.attributes.logger.info(f"Successfully created {len(created_packages)} software packages.")
                return created_packages
            else:
                self.attributes.logger.error(f"Batch create failed: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            self.attributes.logger.error(f"Error during batch creation: {e}", exc_info=True)
            return []

    def _collect_packages_parallel(self, grouping: dict, existing_inventory_set: set, packages_to_create: dict) -> int:
        """
        Collect packages from CSV in parallel using ThreadPoolExecutor.

        :param dict grouping: Dict of hostname -> asset groups
        :param set existing_inventory_set: Set of existing packages
        :param dict packages_to_create: Dict to store packages to create
        :return: Total count of collected packages
        :rtype: int
        """
        packages_lock = Lock()

        def collect_packages(key: Any, group: list) -> int:
            """Collect packages from CSV rows for this asset group."""
            collected_count = 0
            group_rows = [row for row in self.file_data if self.mapping.get_value(row, "Hostname") == key]

            if not group_rows:
                return 0

            parent_asset_id = group[0].id

            for row in group_rows:
                try:
                    with packages_lock:
                        if self._process_package_row(
                            row, key, parent_asset_id, existing_inventory_set, packages_to_create
                        ):
                            collected_count += 1
                except Exception as e:
                    self.attributes.logger.error(f"Error processing package for {key}: {e}", exc_info=True)

            return collected_count

        # Collect packages in parallel
        total_collected = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(collect_packages, key, group): key for key, group in grouping.items()}
            for future in futures:
                try:
                    total_collected += future.result()
                except Exception as e:
                    self.attributes.logger.error(f"Error collecting packages: {e}", exc_info=True)

        return total_collected

    def create_software_inventory(
        self, enable_software_inventory: bool = False, scanned_assets: Optional[List] = None
    ) -> List[SoftwareInventory]:
        """
        Create and post a list of software inventory for a given asset.
        Uses client-side deduplication with batch submission for performance.

        :param bool enable_software_inventory: Whether to enable software inventory processing
        :param Optional[List] scanned_assets: Pre-fetched list of RegScale assets (with IDs). If None, uses self.data
        :return: List of software inventory
        :rtype: List[SoftwareInventory]
        """
        if not enable_software_inventory:
            self.attributes.logger.info("Software inventory processing is disabled.")
            return []

        # If scanned_assets not provided, try to get from self.data
        if scanned_assets is None:
            if not self.data or "assets" not in self.data or "vulns" not in self.data:
                self.attributes.logger.warning("No asset or vulnerability data available.")
                return []

            scanned_assets = [
                asset for asset in self.data["assets"] if asset.id in {vuln.parentId for vuln in self.data["vulns"]}
            ]

        if not scanned_assets:
            self.attributes.logger.info("No scanned assets found.")
            return []

        self.attributes.logger.info(f"Processing inventory for {len(scanned_assets)} scanned assets.")

        # Fetch existing inventory
        existing_inventory_set = self._fetch_existing_inventory(scanned_assets)
        self.attributes.logger.info(f"Found {len(existing_inventory_set)} existing software packages.")

        # Group hardware assets by hostname
        # Note: Using "Server" category instead of "Hardware" as that's what prisma_modules sets
        hardware = sorted(
            [
                asset
                for asset in scanned_assets
                if hasattr(asset, "assetCategory") and asset.assetCategory in ["Hardware", "Server"]
            ],
            key=attrgetter("name"),
        )
        self.attributes.logger.info(f"Found {len(hardware)} hardware/server assets for software inventory.")
        grouping = {key: list(group) for key, group in groupby(hardware, key=attrgetter("name"))}

        # Collect packages in parallel
        packages_to_create = {}
        self.attributes.logger.info("Collecting packages from CSV in parallel...")
        total_collected = self._collect_packages_parallel(grouping, existing_inventory_set, packages_to_create)
        self.attributes.logger.info(f"Collected {total_collected} unique packages to create.")

        # Batch create packages
        created_packages = self._batch_create_packages(packages_to_create)

        self.attributes.logger.info(
            f"Software inventory complete. Created {len(created_packages)} packages "
            f"across {len(scanned_assets)} assets."
        )

        return created_packages
