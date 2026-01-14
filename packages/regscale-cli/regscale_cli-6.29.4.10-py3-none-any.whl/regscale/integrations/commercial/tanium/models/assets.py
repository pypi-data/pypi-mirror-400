#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium Endpoint (Asset) Model.

Transforms Tanium endpoint data to RegScale Asset format.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("regscale")


@dataclass
class TaniumEndpoint:
    """
    Represents a Tanium endpoint (asset).

    Maps Tanium endpoint data to RegScale Asset model fields.
    """

    tanium_id: int
    computer_name: str
    computer_id: Optional[str] = None
    domain_name: Optional[str] = None
    ip_address: Optional[str] = None
    ip_addresses: List[str] = field(default_factory=list)
    mac_address: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    serial_number: Optional[str] = None
    last_logged_in_user: Optional[str] = None
    last_seen: Optional[str] = None
    first_seen: Optional[str] = None
    is_virtual: bool = False
    chassis_type: Optional[str] = None
    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    ram_mb: Optional[int] = None
    disk_size_gb: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_tanium_data(cls, data: Dict[str, Any]) -> "TaniumEndpoint":
        """
        Create TaniumEndpoint from Tanium API response data.

        Args:
            data: Raw endpoint data from Tanium API

        Returns:
            TaniumEndpoint instance
        """
        # Handle ID that might be string or int
        tanium_id = data.get("id", 0)
        if isinstance(tanium_id, str):
            try:
                tanium_id = int(tanium_id)
            except ValueError:
                tanium_id = hash(tanium_id) % (10**9)

        # Handle computer name that might be int (defensive)
        computer_name = data.get("computerName", "")
        if not isinstance(computer_name, str):
            computer_name = str(computer_name)

        return cls(
            tanium_id=tanium_id,
            computer_name=computer_name,
            computer_id=data.get("computerID"),
            domain_name=data.get("domainName"),
            ip_address=data.get("ipAddress"),
            ip_addresses=data.get("ipAddresses", []),
            mac_address=data.get("macAddress"),
            manufacturer=data.get("manufacturer"),
            model=data.get("model"),
            os_name=data.get("osName"),
            os_version=data.get("osVersion"),
            serial_number=data.get("serialNumber"),
            last_logged_in_user=data.get("lastLoggedInUser"),
            last_seen=data.get("lastSeen"),
            first_seen=data.get("firstSeen"),
            is_virtual=data.get("isVirtual", False),
            chassis_type=data.get("chassisType"),
            cpu_model=data.get("cpuModel"),
            cpu_cores=data.get("cpuCores"),
            ram_mb=data.get("ramMB"),
            disk_size_gb=data.get("diskSizeGB"),
            tags=data.get("tags", []),
            raw_data=data,
        )

    def get_asset_type(self) -> str:
        """
        Determine RegScale asset type based on Tanium data.

        Returns:
            RegScale AssetType string value
        """
        # Virtual machines
        if self.is_virtual:
            return "Virtual Machine (VM)"

        # Check chassis type
        chassis = (self.chassis_type or "").lower()
        if chassis in ["server", "rack mount", "blade"]:
            return "Physical Server"
        if chassis in ["desktop", "tower"]:
            return "Desktop"
        if chassis in ["laptop", "notebook", "portable"]:
            return "Laptop"
        if chassis in ["tablet"]:
            return "Tablet"

        # Check OS name for hints
        os_lower = (self.os_name or "").lower()
        if "server" in os_lower:
            return "Physical Server"
        if "macos" in os_lower or "mac os" in os_lower:
            return "Desktop"

        # Default based on common scenarios
        return "Desktop"

    def get_operating_system_category(self) -> str:
        """
        Determine RegScale operating system category.

        Returns:
            RegScale AssetOperatingSystem string value
        """
        os_lower = (self.os_name or "").lower()

        # Windows variants
        if "windows" in os_lower:
            if "server" in os_lower:
                return "Windows Server"
            return "Windows Desktop"

        # macOS
        if "macos" in os_lower or "mac os" in os_lower or "osx" in os_lower:
            return "Mac OSX"

        # Linux distributions
        linux_distros = ["ubuntu", "centos", "rhel", "red hat", "debian", "fedora", "suse", "linux"]
        if any(distro in os_lower for distro in linux_distros):
            return "Linux"

        # Unix variants
        unix_variants = ["solaris", "aix", "hp-ux", "unix"]
        if any(variant in os_lower for variant in unix_variants):
            return "Unix"

        # Mobile
        if "ios" in os_lower or "iphone" in os_lower or "ipad" in os_lower:
            return "iOS"
        if "android" in os_lower:
            return "Android"

        # Network devices
        if "palo alto" in os_lower or "pan-os" in os_lower:
            return "Palo Alto"

        return "Other"

    def get_unique_identifier(self) -> str:
        """
        Generate unique identifier for this endpoint.

        Returns:
            Unique identifier string
        """
        return "tanium-%s-%s" % (self.tanium_id, self.computer_name)

    def to_regscale_asset(self, parent_id: int, parent_module: str) -> Dict[str, Any]:
        """
        Convert to RegScale Asset dictionary format.

        Args:
            parent_id: RegScale parent record ID
            parent_module: RegScale parent module name

        Returns:
            Dictionary suitable for creating RegScale Asset
        """
        asset_dict = {
            "name": self.computer_name,
            "assetType": self.get_asset_type(),
            "status": "Active (On Network)",
            "assetCategory": "Hardware",
            "parentId": parent_id,
            "parentModule": parent_module,
            "isPublic": True,
            "otherTrackingNumber": self.get_unique_identifier(),
            "operatingSystem": self.get_operating_system_category(),
            "ipAddress": self.ip_address or "",
            "macAddress": self.mac_address or "",
            "serialNumber": self.serial_number or "",
            "fqdn": self._build_fqdn(),
        }

        # Add optional fields if available
        if self.manufacturer:
            asset_dict["manufacturer"] = self.manufacturer
        if self.model:
            asset_dict["model"] = self.model
        if self.os_version:
            asset_dict["osVersion"] = self.os_version

        # Build description
        asset_dict["description"] = self._build_description()

        return asset_dict

    def _build_fqdn(self) -> str:
        """Build FQDN from computer name and domain."""
        if self.domain_name and self.computer_name:
            return "%s.%s" % (self.computer_name, self.domain_name)
        return self.computer_name or ""

    def _build_description(self) -> str:
        """Build asset description with Tanium details."""
        parts = ["Asset imported from Tanium"]

        if self.manufacturer and self.model:
            parts.append("Hardware: %s %s" % (self.manufacturer, self.model))

        if self.os_name:
            os_info = self.os_name
            if self.os_version:
                os_info = "%s (%s)" % (os_info, self.os_version)
            parts.append("OS: %s" % os_info)

        if self.is_virtual:
            parts.append("Type: Virtual Machine")

        if self.last_logged_in_user:
            parts.append("Last User: %s" % self.last_logged_in_user)

        if self.tags:
            parts.append("Tags: %s" % ", ".join(self.tags))

        return " | ".join(parts)
