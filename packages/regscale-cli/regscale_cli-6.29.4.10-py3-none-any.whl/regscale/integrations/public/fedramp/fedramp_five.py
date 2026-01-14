"""fedramp v5 docx parser"""

import datetime
import logging
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from tempfile import gettempdir
from typing import Any, Dict, List, Optional, Tuple, Union

from dateutil.relativedelta import relativedelta

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import error_and_exit, get_current_datetime
from regscale.core.utils.date import datetime_str
from regscale.integrations.public.fedramp.appendix_parser import AppendixAParser
from regscale.integrations.public.fedramp.docx_parser import SSPDocParser
from regscale.integrations.public.fedramp.markdown_appendix_parser import MarkdownAppendixParser, merge_parser_results
from regscale.integrations.public.fedramp.rosetta import RosettaStone
from regscale.models import (
    ControlImplementation,
    ControlImplementationStatus,
    ControlObjective,
    ControlParameter,
    File,
    ImplementationObjective,
    ImplementationOption,
    LeveragedAuthorization,
    Parameter,
    PortsProtocol,
    Profile,
    ProfileMapping,
    SecurityControl,
    SecurityPlan,
    StakeHolder,
    SystemRole,
    User,
    ImplementationControlOrigin,
)
from regscale.models.regscale_models.leveraged_authorization import (
    NatureOfAgreement,
    ImpactLevel,
    AuthoriztionType,
)
from regscale.utils.version import RegscaleVersion

SERVICE_PROVIDER_CORPORATE = "Service Provider Corporate"
DEFAULT_STATUS = ControlImplementationStatus.NotImplemented
SYSTEM_DESCRIPTION = "System Description"
AUTHORIZATION_BOUNDARY = "Authorization Boundary"
NETWORK_ARCHITECTURE = "System and Network Architecture"
DATA_FLOW = "Data Flows"
ENVIRONMENT = "System Environment and Inventory"
LAWS_AND_REGULATIONS = "Applicable Laws, Regulations, Standards, and Guidance"
CATEGORIZATION_JUSTIFICATION = "Security Categorization"
SYSTEM_FUNCTION = "System Function or Purpose"

# Default fallback values for LeveragedAuthorization fields
NOT_SPECIFIED = "Not Specified"
UNKNOWN_CSP = "Unknown CSP"

# Status mapping for control implementation - used in handle_parts and check_for_existing_objective
# Maps status values to their standardized RegScale equivalents
IMPLEMENTATION_STATUS_MAP = {
    ControlImplementationStatus.FullyImplemented.value: "Implemented",  # "Fully Implemented" -> "Implemented"
    ControlImplementationStatus.PartiallyImplemented.value: ControlImplementationStatus.PartiallyImplemented.value,
    ControlImplementationStatus.Alternative.value: ControlImplementationStatus.Alternative.value,
    ControlImplementationStatus.NA.value: ControlImplementationStatus.NA.value,
    ControlImplementationStatus.NotImplemented.value: ControlImplementationStatus.NotImplemented.value,
    ControlImplementationStatus.Planned.value: ControlImplementationStatus.Planned.value,
    "Planned": "Planned",  # Handle raw string "Planned" directly
}

logger = logging.getLogger("regscale")


IN_MEMORY_ROLES_PROCESSED = []
# precompile part pattern
PART_PATTERN = re.compile(r"(<p>Part\s[a-zA-Z]:</p>.*?)(?=<p>Part\s[a-zA-Z]:</p>|$)", re.DOTALL)

# Precompile patterns for customer responsibility extraction from part content
# These patterns match various FedRAMP document formats for responsibility sections
CUSTOMER_RESPONSIBILITY_PATTERNS = [
    # Pattern with HTML tags
    re.compile(
        r"(?:<[^>]*>)*\s*"
        r"(?:Federal\s+)?Customer(?:\s+(?:Agency|Organization))?\s+Responsibilit(?:y|ies)"
        r"(?:<[^>]*>)*\s*:?\s*"
        r"(.*?)(?=(?:<[^>]*>)*\s*(?:Service\s+Provider|CSP|Cloud|Test\s+Case|Provider)\s+Responsibilit|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
    # Simple pattern without HTML
    re.compile(
        r"(?:Federal\s+)?Customer(?:\s+(?:Agency|Organization))?\s+Responsibilit(?:y|ies)\s*:?\s*"
        r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Test\s+Case|Provider)\s+Responsibilit|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
    # Agency-specific patterns
    re.compile(
        r"Agency\s+(?:Specific\s+)?(?:Responsibilit(?:y|ies)|Implementation)\s*:?\s*"
        r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Provider)\s+|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
    # Tenant responsibility pattern
    re.compile(
        r"Tenant\s+(?:Responsibilit(?:y|ies)|Implementation)\s*:?\s*"
        r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Provider)\s+|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
    # Customer Implementation Statement pattern
    re.compile(
        r"(?:Federal\s+)?Customer\s+Implementation(?:\s+Statement)?\s*:?\s*"
        r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Provider)\s+|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
]

CLOUD_RESPONSIBILITY_PATTERNS = [
    # Pattern with HTML tags
    re.compile(
        r"(?:<[^>]*>)*\s*"
        r"(?:Service\s+Provider|CSP|Cloud(?:\s+Service\s+Provider)?|Test\s+Case)\s+Responsibilit(?:y|ies)"
        r"(?:<[^>]*>)*\s*:?\s*"
        r"(.*?)(?=(?:<[^>]*>)*\s*(?:Federal\s+)?(?:Customer|Agency|Tenant)(?:\s+(?:Agency|Organization))?\s+Responsibilit|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
    # Simple pattern without HTML
    re.compile(
        r"(?:Service\s+Provider|CSP|Cloud(?:\s+Service\s+Provider)?|Test\s+Case)\s+Responsibilit(?:y|ies)\s*:?\s*"
        r"(.*?)(?=(?:Federal\s+)?(?:Customer|Agency|Tenant)(?:\s+(?:Agency|Organization))?\s+Responsibilit|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
    # Provider Implementation Statement pattern
    re.compile(
        r"(?:Service\s+)?Provider\s+Implementation(?:\s+Statement)?\s*:?\s*"
        r"(.*?)(?=(?:Federal\s+)?(?:Customer|Agency|Tenant)\s+|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
    # CSP Implementation pattern
    re.compile(
        r"CSP\s+Implementation(?:\s+Statement)?\s*:?\s*"
        r"(.*?)(?=(?:Federal\s+)?(?:Customer|Agency|Tenant)\s+|Part\s+[a-z]:|$)",
        re.IGNORECASE | re.DOTALL,
    ),
]


def get_fedramp_compliance_setting() -> Optional[Any]:
    """
    Quick lookup for the FedRAMP Compliance Setting

    :return: The FedRAMP Compliance Setting
    :rtype: Optional[Any]
    """
    # We have to be generic here, as ComplianceSetting may not exist in the database
    fedramp_comp = None
    try:
        from regscale.models.regscale_models.compliance_settings import ComplianceSettings

        setting = ComplianceSettings.get_by_current_tenant()
        logger.debug("Using new ComplianceSettings API")
        fedramp_comp = next(
            comp for comp in setting if comp.title == "FedRAMP Compliance Setting"
        )  # if this raises a StopIteration, we have a problem, Houston
    except Exception as e:
        logger.debug(f"Error getting Compliance Setting: {e}")
    return fedramp_comp


@dataclass
class Person:
    """
    Represents a person.
    """

    name: str
    phone: str
    email: str
    title: str
    user_id: Optional[str] = None


@dataclass
class Organization:
    """
    Represents an organization.
    """

    name: str
    address: str
    point_of_contact: Person


@dataclass
class PreparedBy:
    """
    Represents the prepared by information.
    """

    name: str
    street: str
    building: str
    city_state_zip: str


@dataclass
class SSPDoc:
    """
    Represents an SSP document.
    """

    name: str
    fedramp_id: str
    service_model: str
    digital_identity_level: str
    fips_199_level: str
    date_fully_operational: str
    deployment_model: str
    authorization_path: str
    description: str
    expiration_date: Optional[str] = None
    date_submitted: Optional[str] = None
    approval_date: Optional[str] = None
    csp_name: Optional[str] = None
    csp_street: Optional[str] = None
    csp_building: Optional[str] = None
    csp_city_state_zip: Optional[str] = None
    three_pao_name: Optional[str] = None
    three_pao_street: Optional[str] = None
    three_pao_building: Optional[str] = None
    three_pao_city_state_zip: Optional[str] = None
    version: str = "1.0"


@dataclass
class LeveragedService:
    """
    Represents a leveraged service.
    """

    fedramp_csp_name: str  # CSP/CSO Name → title
    cso_service: str  # CSO Service → servicesUsed
    authorization_type: str  # Authorization Type (JAB/Agency) → authorizationType
    fedramp_id: str  # FedRAMP Package ID → fedrampId
    agreement_type: str  # Nature of Agreement → natureOfAgreement
    impact_level: str  # Impact Level → impactLevel
    data_types: str  # Data Types → dataTypes
    authorized_user_authentication: str  # Authorized Users/Authentication → authorizedUserTypes


@dataclass
class LeveragedServices:
    """
    Represents a list of leveraged services.
    """

    leveraged_services: List[LeveragedService]


@dataclass
class PortsAndProtocolData:
    """
    Represents ports and protocol data.
    """

    service: str
    port: int
    start_port: int
    end_port: int
    protocol: str
    ref_number: str
    purpose: str
    used_by: str


@dataclass
class ParamData:
    """
    Represents parameter data.
    """

    control_id: str
    parameter: Optional[str]
    parameter_value: str


def process_company_info(list_of_dicts: List[Dict[str, str]]) -> Organization:
    """
    Processes the company information table.
    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: An Organization object representing the company information.
    :rtype: Organization
    """
    company_info = merge_dicts(list_of_dicts, True)

    person = Person(
        name=company_info.get("Name"),
        phone=company_info.get("Phone Number"),
        email=company_info.get("Email Address"),
        title="System Owner",
    )

    return Organization(
        name=company_info.get("Company / Organization"),
        address=company_info.get("Address"),
        point_of_contact=person,
    )


def process_ssp_info(list_of_dicts: List[Dict[str, str]]) -> SSPDoc:
    """
    Processes the SSP information table.

    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: An SSPDoc object representing the SSP information.
    :rtype: SSPDoc
    """
    ssp_info = merge_dicts(list_of_dicts, True)
    # print(ssp_info)

    today_dt = datetime.date.today()
    expiration_date = datetime.date(today_dt.year + 3, today_dt.month, today_dt.day).strftime("%Y-%m-%d %H:%M:%S")

    return SSPDoc(
        name=ssp_info.get("CSP Name:"),
        fedramp_id=ssp_info.get("FedRAMP Package ID:"),
        service_model=ssp_info.get("Service Model:"),
        digital_identity_level=ssp_info.get("Digital Identity Level (DIL) Determination (SSP Appendix E):"),
        fips_199_level=ssp_info.get("FIPS PUB 199 Level (SSP Appendix K):"),
        date_fully_operational=ssp_info.get("Fully Operational as of:"),
        deployment_model=ssp_info.get("Deployment Model:"),
        authorization_path=ssp_info.get("Authorization Path:"),
        description=ssp_info.get("General System Description:"),
        expiration_date=ssp_info.get("Expiration Date:", expiration_date),
        date_submitted=ssp_info.get("Date Submitted:", get_current_datetime()),
        approval_date=ssp_info.get("Approval Date:", get_current_datetime()),
    )


def _map_nature_of_agreement(value: Optional[str]) -> str:
    """
    Map a string value to NatureOfAgreement enum value.

    :param Optional[str] value: The nature of agreement string from the document.
    :return: The mapped enum value string.
    :rtype: str
    """
    if not value:
        return NatureOfAgreement.Other.value

    value_lower = value.lower().strip()

    if "eula" in value_lower or "end user" in value_lower:
        return NatureOfAgreement.EULA.value
    elif "sla" in value_lower or "service level" in value_lower:
        return NatureOfAgreement.SLA.value
    elif "license" in value_lower:
        return NatureOfAgreement.LicenseAgreement.value
    elif "contract" in value_lower:
        return NatureOfAgreement.Contract.value
    else:
        return NatureOfAgreement.Other.value


def _map_authorization_type(value: Optional[str]) -> str:
    """
    Map a string value to AuthoriztionType enum value.

    :param Optional[str] value: The authorization type string from the document.
    :return: The mapped enum value string.
    :rtype: str
    """
    if not value:
        return AuthoriztionType.Other.value

    value_lower = value.lower().strip()

    if "jab" in value_lower or "joint authorization" in value_lower:
        return AuthoriztionType.JAB.value
    elif "agency" in value_lower:
        return AuthoriztionType.Agency.value
    elif "ready" in value_lower:
        return AuthoriztionType.FedRAMPReady.value
    else:
        return AuthoriztionType.Other.value


def _map_impact_level(value: Optional[str]) -> str:
    """
    Map a string value to ImpactLevel enum value.

    :param Optional[str] value: The impact level string from the document.
    :return: The mapped enum value string.
    :rtype: str
    """
    if not value:
        return ImpactLevel.Low.value

    value_lower = value.lower().strip()

    if "high" in value_lower:
        return ImpactLevel.High.value
    elif "moderate" in value_lower:
        return ImpactLevel.Moderate.value
    elif "li-saas" in value_lower or "low impact saas" in value_lower:
        return ImpactLevel.LowSaaS.value
    elif "low" in value_lower:
        return ImpactLevel.Low.value
    elif "non-authorized" in value_lower or "non authorized" in value_lower:
        return ImpactLevel.NonAuthorized.value
    else:
        return ImpactLevel.Low.value


def _parse_auth_type_and_fedramp_id(combined_value: Optional[str]) -> Tuple[str, str]:
    """
    Parse the combined authorization type and FedRAMP ID field.

    The field format is typically: "JAB / FR-12345" or "Agency / FR-67890"

    :param Optional[str] combined_value: The combined auth type and FedRAMP ID string.
    :return: A tuple of (authorization_type, fedramp_id).
    :rtype: Tuple[str, str]
    """
    if not combined_value:
        return ("", "")

    # Try to split by common separators
    parts = re.split(r"[/\-–—]", combined_value, maxsplit=1)

    if len(parts) >= 2:
        auth_type = parts[0].strip()
        fedramp_id = parts[1].strip()
        # If the second part looks like a FedRAMP ID (starts with FR or has digits)
        if fedramp_id.upper().startswith("FR") or re.search(r"\d", fedramp_id):
            return (auth_type, fedramp_id)

    # If we can't parse a proper FedRAMP ID, try to identify just the auth type
    # and return empty string for fedramp_id (not the whole combined_value)
    if "jab" in combined_value.lower():
        return ("JAB", "")
    elif "agency" in combined_value.lower():
        return ("Agency", "")

    # Last resort: treat the whole value as auth type, no fedramp_id
    return (combined_value, "")


def build_leveraged_services(leveraged_data: List[Dict[str, str]]) -> List[LeveragedService]:
    """
    Processes the leveraged services table.

    :param List[Dict[str, str]] leveraged_data: The table to process.
    :return: A list of LeveragedService objects representing the leveraged services.
    :rtype: List[LeveragedService]
    """
    services = []
    for row in leveraged_data:
        # Parse the combined authorization type and FedRAMP ID field
        combined_auth = row.get("Authorization Type (JAB or Agency) and FedRAMP Package ID #", "")
        auth_type, fedramp_id = _parse_auth_type_and_fedramp_id(combined_auth)

        service = LeveragedService(
            fedramp_csp_name=row.get("CSP/CSO Name (Name on FedRAMP Marketplace)", ""),
            cso_service=row.get(
                "CSO Service (Names of services and features - services from a single CSO can be all listed in one cell)",
                "",
            ),
            authorization_type=auth_type,
            fedramp_id=fedramp_id,
            agreement_type=row.get("Nature of Agreement", ""),
            impact_level=row.get("Impact Level (High, Moderate, Low, LI-SaaS)", ""),
            data_types=row.get("Data Types", ""),
            authorized_user_authentication=row.get("Authorized Users/Authentication", ""),
        )
        services.append(service)

    return services


def process_person_info(list_of_dicts: List[Dict[str, str]]) -> Person:
    """
    Processes the person information table.
    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: A Person object representing the person information.
    :rtype: Person
    """
    person_data = merge_dicts(list_of_dicts, True)
    person = Person(
        name=person_data.get("Name"),
        phone=person_data.get("Phone Number"),
        email=person_data.get("Email Address"),
        title=person_data.get("Title"),
    )
    return person


def _extract_port_number(value: str) -> int:
    """
    Extract just the numeric port from a value that may contain protocol text.

    Handles formats like: "443", "443/TCP", "80 TCP", "TCP 22", "UDP 514", "22/ssh", "443 / HTTPS"

    :param str value: The port value string.
    :return: The numeric port value, or 0 if not parseable.
    :rtype: int
    """
    value = value.strip()
    if not value:
        return 0

    # Find any sequence of digits in the string (handles both "443/TCP" and "TCP 443")
    match = re.search(r"\d+", value)
    if match:
        return int(match.group())

    return 0


def _get_port_values(row: Dict[str, str], port_col: str) -> tuple:
    """
    Extract port values from a row, handling single ports and ranges.

    :param Dict[str, str] row: The row data.
    :param str port_col: The column name for port data.
    :return: Tuple of (port, start_port, end_port).
    :rtype: tuple
    """
    port_value = row.get(port_col, "") or ""
    port_value = str(port_value).strip()

    if not port_value:
        return (0, 0, 0)

    # Check for port range (e.g., "1024-65535" or "1024-65535/TCP")
    if "-" in port_value:
        parts = port_value.split("-")
        start_port = _extract_port_number(parts[0])
        end_port = _extract_port_number(parts[1])
        if start_port > 0 and end_port > 0:
            return (0, start_port, end_port)

    # Single port - extract just the number, ignoring any protocol text
    port = _extract_port_number(port_value)
    if port > 0:
        return (port, port, port)

    return (0, 0, 0)


def _find_row_column(row: Dict[str, str], patterns: List[str]) -> Optional[str]:
    """
    Find a column name in a row that matches any of the given patterns.

    :param Dict[str, str] row: The row data.
    :param List[str] patterns: List of lowercase patterns to match.
    :return: The actual column name if found, None otherwise.
    :rtype: Optional[str]
    """
    for col_name in row.keys():
        col_lower = col_name.lower()
        if any(pattern in col_lower for pattern in patterns):
            return col_name
    return None


# Column pattern constants for ports/protocols table parsing
_PORT_PATTERNS = ("port #", "port number", "port", "ports", "port range", "start port", "port(s)", "network port")
_SERVICE_PATTERNS = ("service name", "service", "application", "app name", "component", "service/application")
_PROTOCOL_PATTERNS = ("transport protocol", "protocol", "transport", "tcp/udp", "ip protocol", "layer 4 protocol")
_REF_PATTERNS = ("reference #", "reference", "ref", "id", "item #", "item")
_PURPOSE_PATTERNS = ("purpose", "description", "use", "function", "reason", "justification")
_USED_BY_PATTERNS = ("used by", "usedby", "used_by", "component", "system", "consumer", "user")
_EMPTY_PORT_VALUES = ("n/a", "na", "-", "any", "")


def _should_skip_port_row(port: int, start_port: int, end_port: int, port_value: str) -> bool:
    """Check if a port row should be skipped due to missing/empty data."""
    if port != 0 or start_port != 0 or end_port != 0:
        return False
    return not port_value or port_value.strip().lower() in _EMPTY_PORT_VALUES


def _create_port_protocol_data(row: Dict[str, str], columns: Dict[str, str]) -> PortsAndProtocolData:
    """Create a PortsAndProtocolData object from a row using detected columns."""
    port, start_port, end_port = _get_port_values(row, columns["port"])
    return PortsAndProtocolData(
        service=row.get(columns["service"]) or "",
        port=port,
        start_port=start_port,
        end_port=end_port,
        protocol=row.get(columns["protocol"]) or "",
        ref_number=row.get(columns["ref"]) or "",
        purpose=row.get(columns["purpose"]) or "",
        used_by=row.get(columns["used_by"]) or "",
    )


def process_ports_and_protocols(list_of_dicts: List[Dict[str, str]]) -> List[PortsAndProtocolData]:
    """
    Processes the ports and protocols table.
    :param List[Dict[str, str]] list_of_dicts: The table to process.
    :return: A list of PortsAndProtocolData objects representing the ports and protocols information.
    :rtype: List[PortsAndProtocolData]
    """
    ports_and_protocols = []

    for row in list_of_dicts:
        try:
            columns = _detect_port_columns(row)
            port, start_port, end_port = _get_port_values(row, columns["port"])

            if _should_skip_port_row(port, start_port, end_port, row.get(columns["port"], "")):
                logger.debug("Skipping row with no port data: %s", row)
                continue

            ports_and_protocols.append(_create_port_protocol_data(row, columns))
        except (ValueError, AttributeError) as e:
            logger.warning("Skipping bad data unable to process row: %s - %s", row, e)

    logger.debug("Processed %d ports and protocols entries", len(ports_and_protocols))
    return ports_and_protocols


def _detect_port_columns(row: Dict[str, str]) -> Dict[str, str]:
    """Detect column names for port/protocol data using flexible pattern matching."""
    return {
        "port": _find_row_column(row, _PORT_PATTERNS) or "Port #",
        "service": _find_row_column(row, _SERVICE_PATTERNS) or "Service Name",
        "protocol": _find_row_column(row, _PROTOCOL_PATTERNS) or "Transport Protocol",
        "ref": _find_row_column(row, _REF_PATTERNS) or "Reference #",
        "purpose": _find_row_column(row, _PURPOSE_PATTERNS) or "Purpose",
        "used_by": _find_row_column(row, _USED_BY_PATTERNS) or "Used By",
    }


def merge_dicts(list_of_dicts: List[Dict], prioritize_first: bool = False) -> dict:
    """
    Merges a list of dictionaries into a single dictionary.
    :param List[Dict] list_of_dicts: The list of dictionaries to merge.
    :param bool prioritize_first: Whether to prioritize the first dictionary in the list.
    :return: A single dictionary containing the merged data.
    :rtype: dict
    """

    merged_dict = {}
    for d in list_of_dicts:
        if prioritize_first:
            merged_dict.update(d, **merged_dict)  # Merge with priority to earlier values
        else:
            merged_dict.update(d)  # Simple merge

    return merged_dict


def identify_and_process_tables(tables: List[Dict[str, Any]]):
    """
    Identifies and processes tables based on their content keywords and processes them accordingly.
    :param List[Dict[str, Any]] tables: The tables to process.
    :return: A dictionary containing the processed data.
    :rtype: Dict[str, Any]
    """
    processed_data = {
        "ssp_doc": None,
        "org": None,
        "prepared_by": None,
        "stakeholders": [],
        "services": [],
        "ports_and_protocols": [],
    }
    # logger.info(tables)
    for item in tables:
        process_table_based_on_keys(item, processed_data)
        logger.debug(item.get("preceding_text"))
        logger.debug(item.get("table_data"))

    # Identify all SSP stakeholders and find/create RegScale users
    ssp_stakeholders = identify_ssp_stakeholders(processed_data.get("stakeholders", []))

    # Store stakeholder users in processed_data
    owner = ssp_stakeholders.get("owner")
    isso = ssp_stakeholders.get("isso")
    authorizing_official = ssp_stakeholders.get("authorizing_official")
    security_manager = ssp_stakeholders.get("security_manager")

    logger.debug("Owner: %s", owner)
    logger.debug("ISSO: %s", isso)
    logger.debug("Authorizing Official: %s", authorizing_official)
    logger.debug("Security Manager: %s", security_manager)

    if owner:
        processed_data["owner"] = owner
    if isso:
        processed_data["isso"] = isso
    if authorizing_official:
        processed_data["authorizing_official"] = authorizing_official
    if security_manager:
        processed_data["security_manager"] = security_manager

    return processed_data


def identify_ssp_stakeholders(people: List[Person]) -> Dict[str, Optional[User]]:
    """
    Identifies SSP stakeholders from a list of people and finds or creates RegScale users.

    Matches people by title to SSP roles:
    - "System Owner" -> owner
    - "Information System Security Officer" / "ISSO" -> isso
    - "Authorizing Official" / "AO" -> authorizing_official
    - "System Security Manager" / "Security Manager" -> security_manager

    :param List[Person] people: A list of Person objects representing the stakeholders.
    :returns: A dictionary with user objects for each role (owner, isso, authorizing_official, security_manager).
    :rtype: Dict[str, Optional[User]]
    """
    logger.info("Identifying SSP stakeholders from %d people in document", len(people))
    for person in people:
        if person:
            logger.info("  - Found stakeholder: %s (Title: %s, Email: %s)", person.name, person.title, person.email)

    # Pre-fetch existing users once for efficiency
    existing_users = []
    try:
        existing_users = User.get_list()
        logger.info("Found %d existing users in RegScale for matching", len(existing_users))
    except Exception as e:
        logger.warning("Error getting Users: %s", e)

    # Find people matching each role
    role_matches = find_stakeholders_by_role(people)
    logger.info("Role matches found: %s", {k: v.name if v else None for k, v in role_matches.items()})

    # Convert Person objects to User objects using find_or_create
    result = {
        "owner": None,
        "isso": None,
        "authorizing_official": None,
        "security_manager": None,
    }

    for role, person in role_matches.items():
        if person:
            user = _find_or_create_user_for_person(person, existing_users)
            if user:
                result[role] = user
                logger.info("Mapped %s: %s -> User ID: %s", role, person.name, user.id)
            else:
                logger.warning("Could not find or create user for %s: %s", role, person.name)

    return result


def _find_or_create_user_for_person(person: Person, existing_users: List[dict]) -> Optional[User]:
    """
    Find or create a RegScale user for a Person from the FedRAMP document.

    :param Person person: The person from the document.
    :param List[dict] existing_users: Pre-fetched list of existing users.
    :return: The User object if found or created, None otherwise.
    :rtype: Optional[User]
    """
    if not person or not person.name:
        return None

    try:
        user = User.find_or_create_user(
            name=person.name,
            email=person.email if person.email else None,
            job_title=person.title if person.title else None,
            users=existing_users,
        )
        if user:
            # Store user_id in person for reference
            person.user_id = user.id
        return user
    except Exception as e:
        logger.warning("Error finding/creating user for %s: %s", person.name, e)
        return None


# Role patterns for stakeholder identification (case-insensitive)
_ROLE_PATTERNS = {
    "owner": (
        "system owner",
        "information system owner",
        "cto",
        "chief technical officer",
        "chief technology officer",
        "chief executive officer",
        "ceo",
        "program manager",
        "project manager",
    ),
    "isso": ("information system security officer", "isso", "issm", "information security officer"),
    "authorizing_official": (
        "authorizing official",
        "authorization official",
        "designated ao",
        "designated authorizing",
        "agency ao",
        "federal ao",
    ),
    "security_manager": (
        "system security manager",
        "security manager",
        "information security manager",
        "security governance",
        "chief security officer",
        "cso",
        "ciso",
        "chief information security officer",
        "vp security",
        "vp, security",
        "director of security",
        "director, security",
    ),
}


def _match_title_to_role(title_lower: str) -> Optional[str]:
    """Match a lowercase title to a role name using pattern matching."""
    for role, patterns in _ROLE_PATTERNS.items():
        if any(pattern in title_lower for pattern in patterns):
            return role
    return None


def find_stakeholders_by_role(people: List[Person]) -> Dict[str, Optional[Person]]:
    """
    Identifies SSP stakeholders from a list of people by matching titles to roles.

    :param List[Person] people: A list of Person objects representing the stakeholders.
    :returns: A dictionary mapping role names to Person objects.
    :rtype: Dict[str, Optional[Person]]
    """
    result: Dict[str, Optional[Person]] = dict.fromkeys(_ROLE_PATTERNS)

    try:
        for person in people:
            if not person or not person.title:
                continue

            title_lower = person.title.lower()
            role = _match_title_to_role(title_lower)

            if role and result[role] is None:
                result[role] = person
                logger.debug("Matched %s: %s (title: %s)", role, person.name, person.title)
    except Exception as e:
        logger.warning("Error finding stakeholders by role: %s", e)

    return result


def identify_owner_or_isso(people: List[Person]) -> Tuple[Optional[User], Optional[User]]:
    """
    Identifies the ISSO and the Owner from a list of people and returns User objects.

    This is a backwards-compatible wrapper around identify_ssp_stakeholders.

    :param List[Person] people: A list of Person objects representing the stakeholders.
    :returns: A tuple containing the Owner User and ISSO User.
    :rtype: Tuple[Optional[User], Optional[User]]
    """
    stakeholders = identify_ssp_stakeholders(people)
    return stakeholders.get("owner"), stakeholders.get("isso")


def process_table_based_on_keys(table: any, processed_data: Dict[str, Any]):
    """
    Processes a table based on the keys present in the first row of the table.
    :param any table: The table to process.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    """
    try:
        key = table.get("preceding_text")
        merged_dict = merge_dicts(table.get("table_data"), True)
        table_data = table.get("table_data")
        fetch_ports(key, processed_data, table_data, merged_dict)
        fetch_stakeholders(merged_dict, table_data, processed_data, key)
        fetch_services(merged_dict, table_data, processed_data)
        fetch_ssp_info(merged_dict, table_data, processed_data, key)
        fetch_prep_data(table_data, processed_data, key)
        fetch_system_info(key, processed_data, merged_dict)
        fetch_user_info(key, processed_data, merged_dict)
    except Exception as e:
        logger.warning("Error Processing Table - %s: %s", table.get("preceding_text", "") if table else "", e)


def fetch_prep_data(
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
    key: str,
):
    """
    Fetches Prepared By and Prepared For information from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.

    """
    if "Prepared by" in key:
        logger.debug("Processing Prepared By")
        processed_data["prepared_by"] = process_prepared_by(table_data)
    if "Prepared for" in key:
        logger.debug("Processing Prepared By")
        processed_data["prepared_for"] = process_prepared_by(table_data)


def fetch_ssp_info(
    merged_dict: Dict[str, str],
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
    key: str,
):
    """
    Fetches SSP information from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    if "CSP Name:" in merged_dict:
        logger.debug("Processing SSP Doc")
        processed_data["ssp_doc"] = process_ssp_info(table_data)
    if "Document Revision History" in key:
        logger.debug("Processing Version")
        processed_data["version"] = get_max_version(entries=table_data)
        if processed_data["ssp_doc"]:
            processed_data["ssp_doc"].version = processed_data.get("version")
        logger.debug("Processed Version: %s", processed_data["version"])


def fetch_services(
    merged_dict: Dict[str, str],
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
):
    """
    Fetches services data from the table.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    if "CSP/CSO Name (Name on FedRAMP Marketplace)" in merged_dict:
        logger.debug("Processing Leveraged Services")
        processed_data["services"] = build_leveraged_services(table_data)


def fetch_stakeholders(
    merged_dict: Dict[str, str],
    table_data: List[Dict[str, str]],
    processed_data: Dict[str, Any],
    key: str,
):
    """
    Fetches stakeholders data from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    key_lower = (key or "").lower()

    # Check for organization and stakeholders table (original condition)
    if "Name" in merged_dict and "Company / Organization" in table_data[0]:
        logger.debug("Processing Organization and Stakeholders")
        process_organization_and_stakeholders(table_data, processed_data)

    # Expanded stakeholder detection patterns for FedRAMP v5
    stakeholder_patterns = [
        "isso",
        "issm",
        "point of contact",
        "system owner",
        "authorizing official",
        "security manager",
        "table 4.1",
        "table 4-1",
        "table 4.2",
        "table 4-2",
        "table 4.3",
        "table 4-3",
        "table 4.4",
        "table 4-4",
        "key stakeholder",
        "csp poc",
        "cso poc",
        "agency poc",
        "authorization poc",
    ]

    # Check if this looks like a stakeholder table based on key/heading
    is_stakeholder_table = any(pattern in key_lower for pattern in stakeholder_patterns)

    # Also check if table has person-like columns (Name + Email or Title)
    merged_lower = {k.lower(): v for k, v in merged_dict.items()}
    has_person_columns = "name" in merged_lower and (
        "email" in merged_lower
        or "e-mail" in merged_lower
        or "email address" in merged_lower
        or "title" in merged_lower
        or "phone" in merged_lower
    )

    if is_stakeholder_table or has_person_columns:
        try:
            person = process_person_info(table_data)
            if person and person.name:
                logger.info("Found stakeholder from table '%s': %s (Title: %s)", key[:50], person.name, person.title)
                processed_data["stakeholders"].append(person)
        except Exception as e:
            logger.debug("Error processing potential stakeholder table: %s", e)


def _is_ports_table(key: str, merged_dict: Dict[str, str]) -> bool:
    """
    Check if this is a ports and protocols table using flexible matching.

    :param str key: The preceding text key.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.
    :return: True if this appears to be a ports and protocols table.
    :rtype: bool
    """
    # Variations of table headers in FedRAMP templates
    table_header_patterns = [
        "services, ports, and protocols",
        "ports and protocols",
        "network ports",
        "port table",
        "table 9-1",  # FedRAMP v5 standard table number
        "table 9.1",
        "ports & protocols",
        "ports, protocols",
        "system ports",
        "boundary ports",
        "external ports",
        "internal ports",
        "firewall ports",
    ]
    key_lower = (key or "").lower()

    # Check if the table header matches any pattern
    header_match = any(pattern in key_lower for pattern in table_header_patterns)

    # Variations of port column names - more flexible matching
    port_column_patterns = ["port #", "port", "port number", "ports", "port range", "start port", "end port"]
    merged_keys_lower = [k.lower() for k in merged_dict.keys()]

    # Check for exact or partial port column matches
    port_column_match = any(any(pattern in col for pattern in port_column_patterns) for col in merged_keys_lower)

    # Also check for protocol column as secondary indicator (table with protocol likely has ports)
    protocol_patterns = ["protocol", "transport", "tcp/udp", "tcp", "udp"]
    protocol_match = any(any(pattern in col for pattern in protocol_patterns) for col in merged_keys_lower)

    # Service column as additional indicator
    service_patterns = ["service", "service name", "application"]
    service_match = any(any(pattern in col for pattern in service_patterns) for col in merged_keys_lower)

    # If header matches, just need port column
    if header_match and port_column_match:
        return True

    # If no header but table has port + protocol columns, likely a ports table
    if port_column_match and protocol_match:
        return True

    # If table has service + protocol + some numeric-looking column, might be ports table
    if service_match and protocol_match and port_column_match:
        return True

    return False


def _find_column_name(merged_dict: Dict[str, str], patterns: List[str]) -> Optional[str]:
    """
    Find a column name that matches any of the given patterns.

    :param Dict[str, str] merged_dict: The merged dictionary of the table data.
    :param List[str] patterns: List of lowercase patterns to match.
    :return: The actual column name if found, None otherwise.
    :rtype: Optional[str]
    """
    for col_name in merged_dict.keys():
        col_lower = col_name.lower()
        if any(pattern in col_lower for pattern in patterns):
            return col_name
    return None


def fetch_ports(
    key: str,
    processed_data: Dict[str, Any],
    table_data: List[Dict[str, str]],
    merged_dict: Dict[str, str],
):
    """
    Fetches ports and protocols data from the table.
    :param str key: The key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param List[Dict[str, str]] table_data: The table data to process.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.

    """
    if _is_ports_table(key, merged_dict):
        logger.debug("Processing Ports and Protocols")
        # Extend instead of overwrite to accumulate ports from multiple tables
        processed_data["ports_and_protocols"].extend(process_ports_and_protocols(table_data))


# System information key patterns for extraction
_SYSTEM_INFO_PATTERNS = {
    "system_url": ("System URL", "System Website", "Website URL", "URL", "System Website URL"),
    "system_type": ("System Type", "Information System Type", "Type of System"),
    "other_identifier": ("Other Identifier", "DITPR ID", "DoD IT Portfolio Repository ID", "Unique Identifier"),
    "ditpr_id": ("DITPR ID", "DoD IT Portfolio Repository ID", "DITPR"),
    "emass_id": ("eMASS ID", "Enterprise Mission Assurance Support Service ID", "eMASS"),
    "tracking_id": ("Tracking ID", "ATO Tracking ID", "Authorization Tracking ID", "Package ID"),
}


def _extract_value_by_patterns(merged_dict: Dict[str, str], patterns: tuple) -> Optional[str]:
    """Extract a value from merged_dict using the first matching pattern."""
    for key in patterns:
        if key in merged_dict and merged_dict[key]:
            return merged_dict[key].strip()
    return None


def fetch_system_info(key: str, processed_data: Dict[str, Any], merged_dict: Dict[str, str]) -> None:
    """
    Fetches system information from the System Information table.

    Extracts systemUrl, systemType, and other system metadata from vertical
    tables with "System Information" header.

    :param str key: The preceding text key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.
    """
    if "System Information" not in key:
        return

    logger.debug("Processing System Information table")

    for field_name, patterns in _SYSTEM_INFO_PATTERNS.items():
        value = _extract_value_by_patterns(merged_dict, patterns)
        if value:
            processed_data[field_name] = value
            logger.debug("Found %s: %s", field_name, value)


def _extract_user_count(merged_dict: Dict[str, str], key_patterns: List[str], field_name: str) -> Optional[int]:
    """
    Extract a user count from merged_dict using key patterns.

    :param Dict[str, str] merged_dict: The merged dictionary of the table data.
    :param List[str] key_patterns: List of possible key names to match.
    :param str field_name: Name of the field for logging.
    :return: The extracted user count, or None if not found.
    :rtype: Optional[int]
    """
    for key in key_patterns:
        if key in merged_dict and merged_dict[key]:
            try:
                value = int(re.sub(r"[^\d]", "", merged_dict[key]))
                logger.debug("Found %s: %s", field_name, value)
                return value
            except (ValueError, TypeError):
                pass
    return None


# Key patterns for user count extraction
USER_COUNT_PATTERNS = {
    "users": ["Total Users", "Number of Users", "Users", "System Users"],
    "internal_users": ["Internal Users", "Internal", "Employee Users", "Staff Users"],
    "external_users": ["External Users", "External", "Customer Users", "Public Users"],
    "privileged_users": ["Privileged Users", "Privileged", "Admin Users", "Administrator Users"],
    "users_mfa": ["MFA Users", "Multi-Factor Authentication", "Users with MFA"],
}

# Patterns to identify user information tables
USER_TABLE_PATTERNS = [
    "types of users",
    "user access",
    "system users",
    "user information",
    "user roles",
    "table 5",  # Common FedRAMP user table number
]


def fetch_user_info(
    key: str,
    processed_data: Dict[str, Any],
    merged_dict: Dict[str, str],
):
    """
    Fetches user information from User Access or Types of Users tables.

    Extracts user counts (internal, external, privileged) from FedRAMP SSP tables.

    :param str key: The preceding text key to check for.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    :param Dict[str, str] merged_dict: The merged dictionary of the table data.
    """
    key_lower = (key or "").lower()

    if not any(pattern in key_lower for pattern in USER_TABLE_PATTERNS):
        return

    logger.debug("Processing User Information table")

    for field_name, key_patterns in USER_COUNT_PATTERNS.items():
        value = _extract_user_count(merged_dict, key_patterns, field_name)
        if value is not None:
            processed_data[field_name] = value


def process_prepared_by(table: List[Dict[str, str]]) -> PreparedBy:
    """
    Processes the prepared by information from the table.
    :param List[Dict[str, str]] table: The table to process.
    :return: A PreparedBy object representing the prepared by information.
    :rtype: PreparedBy
    """
    prepared_by = merge_dicts(table, True)
    return PreparedBy(
        name=prepared_by.get("Organization Name"),
        street=prepared_by.get("Street Address"),
        building=prepared_by.get("Suite/Room/Building"),
        city_state_zip=prepared_by.get("City, State, Zip"),
    )


def process_version(table: List[Dict[str, str]]) -> str:
    """
    Processes the version information from the table.
    :param List[Dict[str, str]] table: The table to process.
    :return: The version number.
    :rtype: str
    """
    # Assuming the version is stored under a key named "Version" in one of the table rows
    return get_max_version(table)


def process_organization_and_stakeholders(table: List[Dict[str, str]], processed_data: Dict[str, Any]):
    """
    Processes organization and stakeholders information from the table.
    :param List[Dict[str, str]] table: The table to process.
    :param Dict[str, Any] processed_data: The dictionary where processed data is stored.
    """
    processed_data["org"] = process_company_info(table)
    person = process_person_info(table)
    processed_data["stakeholders"].append(person)


def process_fedramp_docx_v5(
    file_name: str,
    base_fedramp_profile_id: int,
    save_data: bool,
    add_missing: bool,
    appendix_a_file_name: str,
) -> int:
    """
    Processes a FedRAMP document and loads it into RegScale.
    :param str file_name: The path to the FedRAMP document.
    :param int base_fedramp_profile_id: The name of the RegScale FedRAMP profile to use.
    :param bool save_data: Whether to save the data as a JSON file.
    :param bool add_missing: Whether to create missing controls from profile in the SSP.
    :param str appendix_a_file_name: The path to the Appendix A document.
    :return: The created SSP ID.
    :rtype: int
    """
    logger.info(f"Processing FedRAMP Document: {file_name}")
    logger.info(f"Appendix A File: {appendix_a_file_name}")
    ssp_parser = SSPDocParser(file_name)

    logger.info(f"Using the following values: save_data: {save_data} and add_missing: {add_missing}")

    tables = ssp_parser.parse()
    doc_text_dict = ssp_parser.text
    app = Application()
    config = app.config
    user_id = config.get("userId")

    processed_data = identify_and_process_tables(tables)
    parent_id = processing_data_from_ssp_doc(processed_data, user_id, doc_text_dict)
    if appendix_a_file_name:
        # Use dual-parser approach (DOCX + Markdown) with merge for better page-spanning content handling
        load_appendix_a(
            appendix_a_file_name=appendix_a_file_name,
            parent_id=parent_id,
            profile_id=base_fedramp_profile_id,
            add_missing=add_missing,
        )
    extract_and_upload_images(file_name, parent_id)
    return parent_id


def log_dictionary_items(dict_items: Dict[str, str]):
    """
    Logs the items in a dictionary.
    :param Dict[str, str] dict_items: The dictionary to log.
    """
    for key, value in dict_items.items():
        if value:
            logger.debug("%s: %s", key, value)


def handle_implemented(row_data: Dict, status: str) -> str:
    """
    Handles the implemented status of a control.
    :param Dict row_data: The data from the row.
    :param str status: The current status of the control.
    :return: The updated status of the control.
    :rtype: str
    """
    log_dictionary_items(row_data)
    for key, value in row_data.items():
        if key == "Implemented" and value:
            status = ControlImplementationStatus.FullyImplemented.value
    return status


def handle_service_provider_corporate(row_data: Dict, responsibility: str) -> str:
    """
    Handles the service provider corporate responsibility of a control.
    :param Dict row_data:
    :param str responsibility:
    :return: fetched responsibility
    :rtype: str
    """
    log_dictionary_items(row_data)
    for key, value in row_data.items():
        if value:
            responsibility = key
    return responsibility


def handle_parameter(row_data: Dict, parameters: Dict, control_id: int):
    """
    Handles the parameters of a control.
    :param Dict row_data: The data from the row.
    :param Dict parameters: The parameters dictionary.
    :param int control_id: The control ID.
    """
    log_dictionary_items(row_data)
    for key, value in row_data.items():
        if value:
            if parameters.get(control_id):
                parameters[control_id].append(value)
            else:
                parameters[control_id] = [value]


def handle_row_data(
    row: Dict,
    control: ControlImplementation,
    status: str,
    responsibility: str,
    parameters: Dict,
    key: str,
    alternative_key: str,
) -> Tuple[str, str, Dict]:
    """
    Handles the data from a row.
    :param Dict row: The row to process.
    :param ControlImplementation control:
    :param str status:
    :param str responsibility:
    :param Dict parameters:
    :param str key:
    :param str alternative_key:
    :return: A tuple containing the updated status, responsibility, and parameters.
    :rtype: Tuple[str, str, Dict]
    """
    row_data = row.get(key, row.get(alternative_key))
    logger.debug("Row Data: %s", row_data)

    if "Implemented" in row_data:
        status = handle_implemented(row_data, status)
    elif SERVICE_PROVIDER_CORPORATE in row_data:
        responsibility = handle_service_provider_corporate(row_data, responsibility)
    elif "Parameter" in row_data:
        handle_parameter(row_data, parameters, control.id)

    return status, responsibility, parameters


def process_fetch_key_value(summary_data: Dict) -> Optional[str]:
    """
    Extracts key information from the summary data.
    :param Dict summary_data: The summary data from the row.
    :return: str: The key from the summary data.
    :rtype: Optional[str]
    """
    for key, value in summary_data.items():
        if value:
            logger.debug("%s: %s", key, value)
            return key
    return None


def process_parameter(summary_data: Dict, control_id: int, current_parameters: List[Dict]):
    """
    Processes the parameters from the summary data.
    :param Dict summary_data: The summary data from the row.
    :param int control_id: The control ID.
    :param List[Dict] current_parameters: The current parameters.
    """
    for key, value in summary_data.items():
        if value:
            parameter_name = key.replace("Parameter ", "").strip()
            param = {
                "control_id": control_id,
                "parameter_name": parameter_name if parameter_name else None,
                "parameter_value": value,
            }
            if param not in current_parameters:
                current_parameters.append(param)


def process_row_data(row: Dict, control: SecurityControl, control_dict: Dict) -> Tuple[str, str, List[Dict]]:
    """
    Processes a single row of data, updating status, responsibility, and parameters based on control summary information.
    :param Dict row: The row to process.
    :param SecurityControl control: The control to process.
    :param Dict control_dict: The dictionary containing the control data.
    :return: A tuple containing the updated status, responsibility, and parameters.
    :rtype: Tuple[str, str, List[Dict]]
    """
    control_id_key = f"{control.controlId} Control Summary Information"
    alternate = format_alternative_control_key(control.controlId) or control.controlId
    alternative_control_id_key = f"{alternate} Control Summary Information"

    summary_data = row.get(control_id_key, row.get(alternative_control_id_key))
    if summary_data:
        logger.debug("Row Data: %s", summary_data)

        if "Implemented" in summary_data:
            status = process_fetch_key_value(summary_data)
            control_dict["status"] = (
                ControlImplementationStatus.FullyImplemented.value if status == "Implemented" else status
            )

        if SERVICE_PROVIDER_CORPORATE in summary_data:
            control_dict["responsibility"] = process_fetch_key_value(summary_data)

        if "Parameter" in summary_data:
            process_parameter(summary_data, control.id, control_dict.get("parameters", []))

    return (
        control_dict.get("status"),
        control_dict.get("responsibility"),
        control_dict.get("parameters"),
    )


def process_fetch_key_if_value(summary_data: Dict) -> str:
    """
    Extracts key information from the summary data.
    :param Dict summary_data: The summary data from the row.
    :return: str: The key from the summary data.
    :rtype: str
    """
    for key, value in summary_data.items():
        if value is True or value == "☒":
            logger.debug("%s: %s", key, value)
            return key


def _find_statement(control: any, alternative_control_id: str, row: Dict, control_dict: Dict) -> str:
    """
    Find the statement for the control.
    :param any control:
    :param str alternative_control_id:
    :param Dict row:
    :param Dict control_dict:
    :return: str: The statement for the control.
    :rtype: str
    """
    key_statment = f"{control.controlId} What is the solution and how is it implemented?"
    key_alt_statment = f"{alternative_control_id} What is the solution and how is it implemented?"
    statement_dict = row.get(key_statment) or row.get(key_alt_statment)

    if isinstance(statement_dict, dict):
        control_dict["statement"] = " ".join(f"{key} {value}" for key, value in statement_dict.items() if value)
    elif isinstance(statement_dict, str):
        control_dict["statement"] = statement_dict
    return ""


def fetch_profile_mappings(profile_id: int) -> List[ProfileMapping]:
    """
    Fetches the profile mappings for a given profile.
    :param int profile_id: The profile ID.
    :return: A list of ProfileMapping objects.
    :rtype: List[ProfileMapping]
    """
    profile_mappings = []
    try:
        profile = Profile.get_object(object_id=profile_id)
        if profile and profile.name:
            logger.debug(f"Profile: {profile.name}")
            profile_mappings = ProfileMapping.get_by_profile(profile_id=profile.id)
    except AttributeError:
        error_and_exit(f"Profile #{profile_id} not found, exiting ..")
    logger.info(f"Found {len(profile_mappings)} controls in profile")
    return profile_mappings


def load_appendix_a(
    appendix_a_file_name: str,
    parent_id: int,
    profile_id: int,
    add_missing: bool,
):
    """
    Loads the Appendix A data.

    This function uses two parsers to extract control implementation data:
    1. AppendixAParser - Parses DOCX directly, better for checkbox/status detection
    2. MarkdownAppendixParser - Converts to markdown first, better for page-spanning content

    The results are merged to get the best of both approaches.

    :param str appendix_a_file_name: The path to the Appendix A file.
    :param int parent_id: The parent ID.
    :param int profile_id: The profile ID.
    :param bool add_missing: Whether to add missing controls.
    """
    logger.info("Processing Appendix A File: %s", appendix_a_file_name)

    # Parse using traditional DOCX parser (good for checkboxes and statuses)
    logger.debug("Running DOCX parser for checkbox and status extraction...")
    docx_parser = AppendixAParser(filename=appendix_a_file_name)
    docx_results = docx_parser.fetch_controls_implementations()
    logger.debug("DOCX parser found %d controls", len(docx_results))

    # Parse using markdown-based parser (good for page-spanning content)
    logger.debug("Running markdown parser for implementation statement extraction...")
    try:
        md_parser = MarkdownAppendixParser(filename=appendix_a_file_name)
        md_results = md_parser.fetch_controls_implementations()
        logger.debug("Markdown parser found %d controls", len(md_results))

        # Merge results - DOCX for status/origination, markdown for parts/statements
        controls_implementation_dict = merge_parser_results(docx_results, md_results)
        logger.info(
            "Merged parser results: %d controls (DOCX: %d, Markdown: %d)",
            len(controls_implementation_dict),
            len(docx_results),
            len(md_results),
        )
    except Exception as e:
        # Fall back to DOCX parser only if markdown parsing fails
        logger.warning("Markdown parser failed, using DOCX parser results only: %s", e)
        controls_implementation_dict = docx_results

    process_appendix_a(
        parent_id=parent_id,
        profile_id=profile_id,
        add_missing=add_missing,
        controls_implementation_dict=controls_implementation_dict,
    )


def process_appendix_a(
    parent_id: int,
    profile_id: int,
    add_missing: bool = False,
    controls_implementation_dict: Dict = None,
    mdparts_dict: Dict = None,
):
    """
    Processes the Appendix A data.
    :param int parent_id: The parent ID.
    :param int profile_id: The profile ID.
    :param bool add_missing: Whether to add missing controls.
    :param Dict controls_implementation_dict: The controls implementation dictionary.
    :param Dict mdparts_dict: The control parts dictionary.
    """
    profile_mappings = fetch_profile_mappings(profile_id=profile_id)
    data_dict = controls_implementation_dict
    existing_controls: list[ControlImplementation] = ControlImplementation.get_all_by_parent(
        parent_id=parent_id, parent_module=SecurityPlan.get_module_slug()
    )
    for control in existing_controls:
        if not control.parentId or control.parentId == 0:
            control.parentId = parent_id

    logger.info(f"Found {len(existing_controls)} existing controls")
    logger.debug(f"{existing_controls=}")
    existing_control_dict = {c.controlID: c for c in existing_controls if c and c.controlID}

    param_mapper = RosettaStone()
    param_mapper.load_fedramp_version_5_mapping()
    param_mapper.lookup_l0_by_l1()
    for mapping in profile_mappings:
        control = SecurityControl.get_object(object_id=mapping.controlID)

        if not control:
            logger.debug(f"Control not found in mappings: {mapping.controlID}")
            continue
        alternate = control.controlId
        try:
            alternate = format_alternative_control_key(control.controlId)
        except ValueError:
            logger.debug(f"Error formatting alternative control key: {control.controlId}")
        alternative_control_id = alternate
        control_dict = data_dict.get(control.controlId)
        if not control_dict:
            control_dict = data_dict.get(alternative_control_id)
        if not control_dict:
            logger.debug(f"Control not found in parsed controls: {control.controlId}")
            continue

        process_control_implementations(
            existing_control_dict,
            control,
            control_dict,
            parent_id,
            add_missing,
            mdparts_dict,
        )


def process_control_implementations(
    existing_control_dict: Dict,
    control: SecurityControl,
    control_dict: Dict,
    parent_id: int,
    add_missing: bool = False,
    mdparts_dict: Dict = None,
):
    """
    Processes the control implementations.
    :param Dict existing_control_dict: The existing control dictionary.
    :param SecurityControl control: The control implementation object.
    :param Dict control_dict: The control dictionary.
    :param int parent_id: The parent ID.
    :param bool add_missing: Whether to add missing controls.
    :param Dict mdparts_dict: The control parts dictionary.
    """
    supporting_roles, primary_role = get_primary_and_supporting_roles(
        control_dict.get("responsibility").split(",") if control_dict.get("responsibility") else [],
        parent_id,
    )

    if existing_control := existing_control_dict.get(control.id):
        _update_existing_control(
            existing_control,
            control,
            control_dict,
            primary_role,
            supporting_roles,
            mdparts_dict,
            parent_id,
        )
    else:
        _create_control_implementation(
            control, control_dict, primary_role, parent_id, add_missing, supporting_roles, mdparts_dict
        )


def _create_control_implementation(
    control: SecurityControl,
    control_dict: Dict,
    primary_role: Dict,
    parent_id: int,
    add_missing: bool,
    supporting_roles: List[Dict],
    mdparts_dict: Dict,
):
    """
    Creates a new control implementation.
    :param SecurityControl control:
    :param Dict control_dict:
    :param Dict primary_role:
    :param int parent_id:
    :param bool add_missing:
    :param List[Dict] supporting_roles:
    :param Dict mdparts_dict:
    :return:
    """
    new_statement = mdparts_dict.get(control.controlId) if mdparts_dict else None
    implementation = create_implementations(
        control,
        parent_id,
        control_dict.get("status"),
        new_statement if new_statement else control_dict.get("statement"),
        control_dict.get("origination"),
        control_dict.get("parameters"),
        add_missing,
        role_id=primary_role.get("id") if primary_role else None,
        planned_implementation_date=control_dict.get("planned_implementation_date"),
        exclusion_justification=control_dict.get("exclusion_justification"),
        alternative_implementation=control_dict.get("alternative_implementation"),
    )
    if implementation:
        if parts := control_dict.get("parts"):
            handle_parts(
                parts=parts,
                status=map_implementation_status(control_dict.get("status")),
                control=control,
                control_implementation=implementation,
                mdparts_dict=mdparts_dict,
                origination=control_dict.get("origination"),
            )
        if params := control_dict.get("parameters"):
            handle_params(
                parameters=params,
                control=control,
                control_implementation=implementation,
            )
        add_roles_to_control_implementation(implementation, supporting_roles)


def _update_existing_control(
    existing_control: ControlImplementation,
    control: SecurityControl,
    control_dict: Dict,
    primary_role: Dict,
    supporting_roles: List[Dict],
    mdparts_dict: Dict,
    parent_id: int,
):
    """
    Updates the existing control implementation.
    :param existing_control ControlImplementation : The existing control implementation.
    :param control SecurityControl: The control object.
    :param control_dict Dict:
    :param primary_role Dict:
    :param supporting_roles List[Dict:
    :param mdparts_dict Dict:
    :param parent_id int:
    """
    new_statement = mdparts_dict.get(control.controlId) if mdparts_dict else None
    statement_to_use = new_statement if new_statement else control_dict.get("statement")
    logger.debug(
        "Updating control %s: statement=%s (mdparts_dict=%s, control_dict has statement=%s)",
        control.controlId,
        repr(statement_to_use)[:100] if statement_to_use else None,
        mdparts_dict is not None,
        "statement" in control_dict,
    )
    update_existing_control(
        existing_control,
        control_dict.get("status"),
        statement_to_use,
        control_dict.get("origination"),
        primary_role if primary_role and isinstance(primary_role, dict) and primary_role.get("id") else None,
        parent_id,
    )
    if params := control_dict.get("parameters"):
        handle_params(
            params,
            control=control,
            control_implementation=existing_control,
        )
    if parts := control_dict.get("parts"):
        handle_parts(
            parts=parts,
            status=map_implementation_status(control_dict.get("status")),
            control=control,
            control_implementation=existing_control,
            mdparts_dict=mdparts_dict,
            origination=control_dict.get("origination"),
        )
    add_roles_to_control_implementation(existing_control, supporting_roles)


def add_roles_to_control_implementation(implementation: ControlImplementation, roles: List[Dict]):
    """
    Updates roles for a control implementation by checking existing roles and adding/removing as appropriate.
    This prevents duplicate roles on successive imports.
    :param ControlImplementation implementation: The control implementation.
    :param List[Dict] roles: The list of roles to set.
    """
    if not implementation or not implementation.id:
        logger.warning("Control implementation is missing or has no ID, cannot update roles")
        return

    try:
        # Get existing roles for this control implementation
        from regscale.models.regscale_models.implementation_role import ImplementationRole

        # Get existing roles
        existing_roles = ImplementationRole.get_all_by_parent(
            parent_id=implementation.id, parent_module=implementation._module_string
        )
        existing_role_ids = {role.roleId for role in existing_roles if role and role.roleId}

        # Get target role IDs from the new roles list
        target_role_ids = {role.get("id") for role in roles if isinstance(role, dict) and role.get("id")}

        # Find roles to add (in target but not in existing)
        roles_to_add = target_role_ids - existing_role_ids

        # Find roles to remove (in existing but not in target)
        roles_to_remove = existing_role_ids - target_role_ids

        # Add new roles
        for role_id in roles_to_add:
            try:
                implementation.add_role(role_id)
                logger.debug(f"Added role {role_id} to control implementation {implementation.id}")
            except Exception as e:
                logger.warning(f"Failed to add role {role_id} to control implementation {implementation.id}: {e}")

        # Remove roles that are no longer needed
        _remove_roles_from_control_implementation(implementation, roles_to_remove, existing_roles)

        if roles_to_add or roles_to_remove:
            logger.info(
                f"Updated roles for control implementation {implementation.id}: added {len(roles_to_add)}, removed {len(roles_to_remove)}"
            )
        else:
            logger.debug(f"No role changes needed for control implementation {implementation.id}")

    except Exception as e:
        logger.error(f"Error updating roles for control implementation {implementation.id}: {e}")
        # Fallback to old behavior if there's an error
        _fallback_add_roles_to_control_implementation(implementation, roles)


def _remove_roles_from_control_implementation(
    implementation: ControlImplementation, roles_to_remove: set, existing_roles: List
):
    """
    Removes roles that are no longer needed from a control implementation.
    :param ControlImplementation implementation: The control implementation to remove roles from.
    :param set roles_to_remove: Set of role IDs that should be removed.
    :param List existing_roles: List of existing ImplementationRole objects.
    """
    for role_id in roles_to_remove:
        try:
            # Find the ImplementationRole record to delete
            for existing_role in existing_roles:
                if existing_role.roleId == role_id:
                    existing_role.delete()
                    logger.debug(f"Removed role {role_id} from control implementation {implementation.id}")
                    break
        except Exception as e:
            logger.warning(f"Failed to remove role {role_id} from control implementation {implementation.id}: {e}")


def _fallback_add_roles_to_control_implementation(implementation: ControlImplementation, roles: List[Dict]):
    """
    Fallback method for adding roles to a control implementation when the main method fails.
    This uses the old behavior of simply adding roles without checking for duplicates.
    :param ControlImplementation implementation: The control implementation.
    :param List[Dict] roles: The list of roles to add.
    """
    if roles and len(roles) > 0:
        for role in roles:
            if isinstance(role, dict) and role.get("id"):
                try:
                    implementation.add_role(role.get("id"))
                except Exception as add_error:
                    logger.warning(f"Failed to add role {role.get('id')}: {add_error}")


def get_primary_and_supporting_roles(roles: List, parent_id: int) -> Tuple[List, Dict]:
    """
    Get the primary role.
    :param List roles: The list of roles.
    :param int parent_id: The parent ID.
    :return: The primary role and supporting roles.
    :rtype: Tuple[List, Dict]
    """
    supporting_roles = []
    primary_role = None
    if roles and len(roles) >= 1:
        primary_role = get_or_create_system_role(roles[0], parent_id)
        for role in roles[1:]:
            if role:
                supporting_roles.append(get_or_create_system_role(role, parent_id))
    return supporting_roles, primary_role


def get_or_create_system_role(role: str, ssp_id: int) -> Optional[Dict]:
    """
    Creates a System Role.
    :param str role: The name of the role.
    :param int ssp_id: The user ID.
    :return: The created role.
    :rtype: Optional[Dict]
    """
    app = Application()
    try:
        role_name = role.strip().replace(",", "")
        if role_name == "<Roles>":
            return None
        existing_sys_roles = [
            r
            for r in SystemRole.get_all_by_parent(parent_id=ssp_id, parent_module=SecurityPlan.get_module_slug())
            if r is not None
        ]
        existing_roles_dict = {r.roleName: r for r in existing_sys_roles}
        in_mem_roles_processed_dict = {r.roleName: r for r in IN_MEMORY_ROLES_PROCESSED if r is not None}
        existing_role = existing_roles_dict.get(role_name) or in_mem_roles_processed_dict.get(role_name)
        IN_MEMORY_ROLES_PROCESSED.append(existing_role)

        if existing_role:
            logger.debug("Role: %s already exists in RegScale, skipping insert..", role_name.strip())
            return existing_role.model_dump()
        else:
            user_id = app.config.get("userId")
            if role_name:
                sys_role = SystemRole(
                    roleName=role_name,
                    roleType="Internal",
                    accessLevel="Privileged",
                    sensitivityLevel=ControlImplementationStatus.NA.value,
                    assignedUserId=user_id,
                    privilegeDescription=role_name,
                    securityPlanId=ssp_id,
                    functions=role_name,
                ).create()
                if sys_role:
                    IN_MEMORY_ROLES_PROCESSED.append(sys_role)
                return sys_role.model_dump()
    except Exception as e:
        logger.warning(f"Error creating role: {role} - {e}")
        return {}


def create_implementations(
    control: SecurityControl,
    parent_id: int,
    status: str,
    statement: str,
    responsibility: str,
    parameters: List[Dict],
    add_missing: bool = False,
    role_id: int = None,
    planned_implementation_date: Optional[str] = None,
    exclusion_justification: Optional[str] = None,
    alternative_implementation: Optional[str] = None,
) -> ControlImplementation:
    """
    Creates the control implementations.
    :param SecurityControl control: The control object.
    :param int parent_id: The parent ID.
    :param str status: The status of the implementation.
    :param str statement: The statement of the implementation.
    :param str responsibility: The responsibility of the implementation.
    :param List[Dict] parameters: The parameters of the implementation.
    :param bool add_missing: Whether to add missing controls.
    :param int role_id: The role ID.
    :param Optional[str] planned_implementation_date: The planned implementation date from document.
    :param Optional[str] exclusion_justification: The exclusion justification from document.
    :param Optional[str] alternative_implementation: Alternative implementation description.
    :return: The created control implementation.
    :rtype: ControlImplementation
    """
    if status and status.lower() == "implemented":
        status = ControlImplementationStatus.FullyImplemented.value
    if control and (status == DEFAULT_STATUS and add_missing) or (status != DEFAULT_STATUS):
        logger.debug(
            "Creating Control: %s - %s - %s - %s - %s",
            control.controlId,
            control.id,
            status,
            statement,
            responsibility,
        )
        logger.debug("params: %s", parameters)
        default_justification, default_planned_date, steps_to_implement = create_control_implementation_defaults(status)

        # Use extracted values from document if available, otherwise fall back to defaults
        final_justification = exclusion_justification or default_justification
        final_planned_date = planned_implementation_date or default_planned_date

        # If alternative implementation is provided, append it to the statement
        final_statement = clean_statement(statement)
        if alternative_implementation:
            final_statement = "{}\n\nAlternative Implementation: {}".format(final_statement, alternative_implementation)

        control_implementation = ControlImplementation(
            parentId=parent_id,
            parentModule="securityplans",
            controlID=control.id,
            status=map_implementation_status(status),
            responsibility=map_responsibility(responsibility),
            implementation=final_statement,
            systemRoleId=role_id,
            exclusionJustification=final_justification,
            stepsToImplement=steps_to_implement,
            plannedImplementationDate=final_planned_date,
        )
        return control_implementation.create()
        # handle_params(parameters, control, control_implementation)


def create_control_implementation_defaults(status: str) -> Tuple[str, str, str]:
    """
    Creates a tuple with default values for exclusion_justification and planned_implementation_date.

    :return: A tuple with default values for exclusion_justification and planned_implementation_date.
    :rtype: Tuple[str, str, str]
    """
    exclusion_justification = None
    planned_implementation_date = None
    steps_to_implement = None
    if status == ControlImplementationStatus.NA.value:
        exclusion_justification = "This is an automated justification, please update"

    if status == "Planned":
        current_date = datetime.datetime.now()
        planned_implementation_date = datetime_str(current_date + datetime.timedelta(days=30))
        steps_to_implement = "Automated steps to implement, please update"

    return exclusion_justification, planned_implementation_date, steps_to_implement


def clean_statement(statement: Union[str, List]) -> str:
    """
    Cleans and formats the statement with proper HTML formatting.

    Formats company/product names (HXM Payroll, BTP HANA CLOUD, etc.) with
    bold styling and line breaks between sections.

    :param Union[str, List] statement: The statement to clean.
    :return: The cleaned and formatted statement.
    :rtype: str
    """
    if isinstance(statement, list):
        text = " ".join(statement)
    else:
        text = statement or ""

    if not text:
        return ""

    return _format_implementation_statement(text)


def _format_implementation_statement(text: str) -> str:
    """
    Format implementation statement with proper HTML for company/product sections.

    :param str text: The raw statement text
    :return: Formatted HTML text
    :rtype: str
    """
    # Known product/company name patterns (case-insensitive matching)
    known_products = [
        r"HXM Payroll",
        r"BTP HANA CLOUD",
        r"SAP HANA Cloud",
        r"PCE IBP",
        r"SAC",
        r"Fieldglass",
        r"S/4",
        r"SAP NS2",
    ]

    # Build pattern to match any known product followed by colon
    product_pattern = "|".join(known_products)

    # Replace product names (not at start) with line breaks before them
    formatted = re.sub(
        rf"(?<=[.!?])\s+({product_pattern})\s*:",
        r"<br/><br/><strong>\1:</strong>",
        text,
        flags=re.IGNORECASE,
    )

    # Handle the first product name at the start of text
    formatted = re.sub(
        rf"^({product_pattern})\s*:",
        r"<strong>\1:</strong>",
        formatted,
        flags=re.IGNORECASE,
    )

    return formatted


def _format_part_statement(text: str) -> str:
    """
    Format part statement text with HTML paragraph tags for proper rendering.

    Converts plain text with newlines to HTML paragraphs:
    - Double newlines become paragraph breaks
    - Single newlines become line breaks
    - Empty or whitespace-only text returns empty string

    :param str text: The raw part statement text with newlines.
    :return: HTML-formatted text with proper paragraph structure.
    :rtype: str
    """
    if not text or not text.strip():
        return ""

    # Split on double newlines (paragraph breaks)
    paragraphs = re.split(r"\n\n+", text.strip())

    formatted_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para:
            # Convert single newlines to <br/> within paragraphs
            para = para.replace("\n", "<br/>")
            formatted_paragraphs.append(f"<p>{para}</p>")

    return "".join(formatted_paragraphs)


def find_matching_parts(part: str, other_ids: List[str]) -> List[str]:
    """
    Find and return the otherId values that contain the specified part (e.g., "Part a"),
    by directly checking for the presence of a substring like '_obj.a'.
    :param str part: The part to look for.
    :param List[str] other_ids: The list of otherId values to search.
    :return: A list of otherId values that contain the specified part.
    :rtype: List[str]
    """
    # Extract the letter part (e.g., "a") from the input string.
    part_letter = part[-1].lower()  # Assuming the format "Part X" where X is the part letter.

    # Construct the substring to look for in otherId values.
    part_pattern = f"_obj.{part_letter}"

    # Collect and return all matching otherId values.
    matches = [
        other_id for other_id in other_ids if part_pattern in other_id.lower() or part_letter in other_id.lower()
    ]

    return matches


def get_or_create_option(
    part_name: str,
    part_value: str,
    control: SecurityControl,
    objective: ControlObjective,
    existing_options: List[ImplementationOption],
    status: Optional[str],
    parent_id: int,
) -> Optional[ImplementationOption]:
    """
    Get or create an implementation option.
    :param str part_name: The name of the part.
    :param str part_value: The value of the part.
    :param SecurityControl control: The security control object.
    :param ControlObjective objective: The control objective object.
    :param List[ImplementationOption] existing_options: The existing options.
    :param Optional[str] status: The status of the implementation.
    :param int parent_id: The parent ID.
    :return: The implementation option.
    :rtype: Optional[ImplementationOption]
    """
    option = None
    for o in existing_options:
        if o.name == part_name:
            option = o
            break
    if not option:
        try:
            option = ImplementationOption(
                name=part_name,
                description=part_value,
                objectiveId=objective.id,
                acceptability=status,
                securityControlId=objective.securityControlId,
            )
            options = ImplementationOption.get_all_by_parent(parent_id=objective.securityControlId, plan_id=parent_id)
            for o in options:
                if o.name == part_name:
                    return o
                elif option.name == o.name:
                    return o
                else:
                    option.get_or_create()
                    return option
        except Exception:
            logger.warning(f"Error creating option: {part_name}")
    return option


def extract_parts(content: str) -> dict:
    """
    Splits a string into parts based on markers like "Part a:", "Part b:", etc.
    If no markers are found, the entire content is treated as general content.

    This function handles cases where:
    - Part markers may be split across page breaks
    - HTML tags may appear within or around part markers
    - Part markers may have varying whitespace

    :param str content: The content to split into parts.
    :return: A dictionary where keys are "Part a", "Part b", etc., and values are the corresponding content.
    :rtype: dict
    """
    output = {}
    if not content:
        return output

    # Enhanced regex to handle various part marker formats:
    # - Standard: "Part a:"
    # - With HTML tags: "<p>Part a:</p>" or "Part <strong>a</strong>:"
    # - With whitespace: "Part  a :" or "Part a :"
    # - Split across elements: "Part" + "a:" (captured by flexible whitespace)
    part_pattern = re.compile(
        r"(?:<[^>]*>\s*)*"  # Optional leading HTML tags with whitespace
        r"Part\s*"  # "Part" followed by optional whitespace
        r"(?:<[^>]*>\s*)*"  # Optional HTML tags between "Part" and letter
        r"([a-z])"  # Capture the part letter
        r"(?:<[^>]*>\s*)*"  # Optional HTML tags after letter
        r"\s*:"  # Colon with optional preceding whitespace
        r"(?:\s*<[^>]*>)*",  # Optional trailing HTML tags
        re.IGNORECASE,
    )

    # Find all matches for "Part a:", "Part b:", etc.
    parts = part_pattern.split(content)

    if len(parts) == 1:  # No "Part a:", "Part b:" markers found
        # Try a fallback pattern for edge cases where markers may be malformed
        fallback_pattern = re.compile(r"Part\s+([a-z])\s*:", re.IGNORECASE)
        parts = fallback_pattern.split(content)

        if len(parts) == 1:
            output["default"] = content.strip()
            return output

    # First chunk is general content (if any)
    general_content = parts[0].strip()
    if general_content:
        output["default"] = general_content

    # Iterate through the matched parts and their corresponding content
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            part_letter = parts[i].lower()  # Part letter (e.g., 'a', 'b')
            part_content = parts[i + 1].strip()  # Corresponding HTML/content for the part
            output[f"Part {part_letter}"] = part_content

    return output


def _get_part_statement(part: Dict, part_letter: str, part_dict: Dict, mdparts_dict: Dict) -> str:
    """Get the statement value for a part, preferring markdown over DOCX."""
    docx_part_value = part.get("value", "")
    if not mdparts_dict:
        return docx_part_value
    md_part_value = part_dict.get(f"Part {part_letter}")
    return md_part_value if md_part_value else docx_part_value


def _find_matching_objectives(control_objectives: List[ControlObjective], part_letter: str) -> List[ControlObjective]:
    """Find objectives matching the part letter."""
    if len(control_objectives) <= 1:
        return control_objectives
    return [o for o in control_objectives if o.name.replace("(", "").startswith(part_letter)]


def _update_aggregated_responsibilities(
    control_implementation: ControlImplementation,
    parts_responsibilities: List[Tuple[Optional[str], Optional[str]]],
    control_id: str,
) -> None:
    """Update control implementation with aggregated responsibilities."""
    if not parts_responsibilities:
        return

    aggregated_customer, aggregated_cloud = aggregate_control_responsibilities(parts_responsibilities)
    if not aggregated_customer and not aggregated_cloud:
        return

    logger.debug(
        "Aggregated control-level responsibilities for %s: customer=%d chars, cloud=%d chars",
        control_id,
        len(aggregated_customer) if aggregated_customer else 0,
        len(aggregated_cloud) if aggregated_cloud else 0,
    )

    needs_update = False
    if aggregated_customer and control_implementation.customerImplementation != aggregated_customer:
        control_implementation.customerImplementation = aggregated_customer
        needs_update = True
    if aggregated_cloud and control_implementation.cloudImplementation != aggregated_cloud:
        control_implementation.cloudImplementation = aggregated_cloud
        needs_update = True

    if needs_update:
        try:
            control_implementation.save()
            logger.debug("Updated control implementation %s with aggregated responsibilities", control_id)
        except Exception as e:
            logger.warning("Failed to update control implementation %s: %s", control_id, str(e))


def handle_parts(
    parts: Dict,
    status: str,
    control: SecurityControl,
    control_implementation: ControlImplementation,
    mdparts_dict: Dict,
    origination: str = None,
):
    """
    Handle the parts for the given control and control implementation.
    :param Dict parts: The parts to handle.
    :param str status: The status of the implementation.
    :param SecurityControl control: The security control object.
    :param ControlImplementation control_implementation: The control implementation object.
    :param Dict mdparts_dict: The control parts dictionary.
    :param str origination: The origination of the implementation.
    """
    control_parts_string = mdparts_dict.get(control.controlId) if mdparts_dict else None
    control_objectives = ControlObjective.get_by_control(control_id=control.id)
    imp_objectives: List[ImplementationObjective] = []
    parts_responsibilities: List[Tuple[Optional[str], Optional[str]]] = []

    if RegscaleVersion.meets_minimum_version("6.13.0.0"):
        status = IMPLEMENTATION_STATUS_MAP.get(status, status)

    if status is None:
        error_and_exit("Status should never be None.")

    for part in parts:
        if part.get("value") == "":
            continue

        part_dict = extract_parts(control_parts_string)
        part_letter = get_part_letter(part.get("name", ""))
        part_statement = _get_part_statement(part, part_letter, part_dict, mdparts_dict)

        part_content = part_statement or part.get("value", "")
        customer_resp, cloud_resp = extract_responsibility_from_part(part_content)
        parts_responsibilities.append((customer_resp, cloud_resp))

        matching_objectives = _find_matching_objectives(control_objectives, part_letter)

        handle_matching_objectives(
            matching_objectives=matching_objectives,
            part=part,
            control=control,
            control_implementation=control_implementation,
            status=IMPLEMENTATION_STATUS_MAP.get(status, status),
            imp_objectives=imp_objectives,
            origination=map_responsibility(origination),
            new_statement=part_statement or None,
            customer_responsibility=customer_resp,
            cloud_responsibility=cloud_resp,
        )

    _update_aggregated_responsibilities(control_implementation, parts_responsibilities, control.controlId)

    if imp_objectives:
        ImplementationObjective.batch_create(items=imp_objectives)


def handle_matching_objectives(
    matching_objectives: List[ControlObjective],
    part: Dict,
    control: SecurityControl,
    control_implementation: ControlImplementation,
    status: Optional[str],
    imp_objectives: List[ImplementationObjective],
    origination: Optional[str] = None,
    new_statement: Optional[str] = None,
    customer_responsibility: Optional[str] = None,
    cloud_responsibility: Optional[str] = None,
):
    """
    Handle the matching objectives for the given part.
    :param List[ControlObjective] matching_objectives: The matching objectives.
    :param Dict part: The part to handle.
    :param SecurityControl control: The security control object.
    :param ControlImplementation control_implementation: The control implementation object.
    :param Optional[str] status: The status of the implementation.
    :param List[ImplementationObjective] imp_objectives: The list of implementation objectives.
    :param Optional[str] origination: The origination of the implementation.
    :param Optional[str] new_statement: The new statement for the implementation.
    :param Optional[str] customer_responsibility: Customer responsibility text extracted from part content.
    :param Optional[str] cloud_responsibility: Cloud/service provider responsibility text extracted from part content.
    """
    statements_used = []
    for objective in matching_objectives:
        logger.debug("Objective: %s - %s - %s", objective.id, objective.name, objective.securityControlId)
        part_statement = f"{part.get('value', '')}" if not new_statement else new_statement
        statements_used.append(part_statement)

        has_existing_obj = check_for_existing_objective(
            control_implementation, objective, status, part_statement, origination
        )
        if has_existing_obj:
            continue
        duplicate = True if part_statement in statements_used else False
        handle_implementation_objectives(
            objective,
            part_statement,
            status,
            control_implementation,
            imp_objectives,
            control,
            duplicate,
            origination,
            customer_responsibility,
            cloud_responsibility,
        )


def check_for_existing_objective(
    control_implementation: ControlImplementation,
    objective: ControlObjective,
    status: Optional[str],
    part_statement: str,
    origination: Optional[str] = None,
) -> bool:
    """
    Check for existing implementation objectives.
    :param ControlImplementation control_implementation: The control implementation object.
    :param ControlObjective objective: The control objective object.
    :param Optional[str] status: The status of the implementation.
    :param str part_statement: The part statement.
    :param Optional[str] origination: The origination of the implementation.
    :return: True if an existing implementation objective is found, False otherwise.
    :rtype: bool
    """
    existing_objectives: List[ImplementationObjective] = ImplementationObjective.get_by_control(
        implementation_id=control_implementation.id
    )
    for existing_obj in existing_objectives:
        if existing_obj.objectiveId == objective.id:
            if status:
                if isinstance(status, ControlImplementationStatus):
                    status = status.value
                existing_obj.status = IMPLEMENTATION_STATUS_MAP.get(status, status)
            existing_obj.statement = _format_part_statement(part_statement)
            if origination is not None:
                existing_obj.responsibility = origination
            existing_obj.parentObjectiveId = objective.id
            existing_obj.save()
            return True
    return False


def map_responsibility(responsibility: str) -> str:
    """
    Map the responsibility to the appropriate value.
    :param str responsibility: The responsibility to map.
    :return: The mapped responsibility.
    :rtype: str
    """
    if not responsibility:
        return ""  # Return empty string instead of None

    # Handle comma-separated values
    if "," in responsibility:
        responsibility_values = [r.strip() for r in responsibility.split(",")]
        return ",".join([map_responsibility(r) for r in responsibility_values])

    # This should be server code with proper enums, but this is the best we can do for now
    responsibility_map = {
        "Service Provider Corporate": ImplementationControlOrigin.SERVICE_PROVIDER_CORPORATE.value,
        "Service Provider System Specific": ImplementationControlOrigin.SERVICE_PROVIDER_SYSTEM.value,
        "Service Provider Hybrid (Corporate and System Specific)": ImplementationControlOrigin.SERVICE_PROVIDER_HYBRID.value,  # Map to closest value
        "Configured by Customer (Customer System Specific)": ImplementationControlOrigin.CONFIGURED_BY_CUSTOMER.value,
        "Provided by Customer (Customer System Specific)": ImplementationControlOrigin.PROVIDED_BY_CUSTOMER.value,
        "Shared (Service Provider and Customer Responsibility)": ImplementationControlOrigin.SHARED.value,
        "Inherited from pre-existing FedRAMP Authorization": ImplementationControlOrigin.INHERITED_FROM_PRE_EXISTING_FEDRAMP_AUTHORIZATION.value,
    }

    return responsibility_map.get(responsibility, responsibility or "")


def extract_responsibility_from_part(part_content: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract customer and cloud responsibility statements from part content.

    FedRAMP v5 SSP documents often have responsibility sections within each part,
    such as "Federal Customer Responsibility" and "Service Provider Responsibility".

    :param str part_content: The content of a control implementation part.
    :return: A tuple of (customer_responsibility, cloud_responsibility) text.
    :rtype: Tuple[Optional[str], Optional[str]]
    """
    customer_responsibility = None
    cloud_responsibility = None

    if not part_content:
        return customer_responsibility, cloud_responsibility

    # Extract customer responsibility
    for pattern in CUSTOMER_RESPONSIBILITY_PATTERNS:
        match = pattern.search(part_content)
        if match:
            extracted = match.group(1).strip()
            # Clean up HTML tags for plain text
            cleaned = re.sub(r"<[^>]+>", " ", extracted)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned and len(cleaned) > 10:  # Must have meaningful content
                customer_responsibility = cleaned
                break

    # Extract cloud/service provider responsibility
    for pattern in CLOUD_RESPONSIBILITY_PATTERNS:
        match = pattern.search(part_content)
        if match:
            extracted = match.group(1).strip()
            # Clean up HTML tags for plain text
            cleaned = re.sub(r"<[^>]+>", " ", extracted)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned and len(cleaned) > 10:  # Must have meaningful content
                cloud_responsibility = cleaned
                break

    return customer_responsibility, cloud_responsibility


def aggregate_control_responsibilities(
    parts_responsibilities: List[Tuple[Optional[str], Optional[str]]],
) -> Tuple[str, str]:
    """
    Aggregate all part-level responsibilities into control-level summary.

    :param parts_responsibilities: List of (customer_responsibility, cloud_responsibility) tuples.
    :return: Aggregated (customer_responsibility, cloud_responsibility) strings.
    :rtype: Tuple[str, str]
    """
    customer_parts = []
    cloud_parts = []

    for idx, (cust, cloud) in enumerate(parts_responsibilities, 1):
        if cust:
            customer_parts.append(f"Part {chr(96 + idx)}: {cust}")
        if cloud:
            cloud_parts.append(f"Part {chr(96 + idx)}: {cloud}")

    customer_aggregated = "\n\n".join(customer_parts) if customer_parts else ""
    cloud_aggregated = "\n\n".join(cloud_parts) if cloud_parts else ""

    return customer_aggregated, cloud_aggregated


def handle_implementation_objectives(
    objective: ControlObjective,
    part_statement: str,
    status: Optional[str],
    control_implementation: Union[ControlImplementation, int, None],
    imp_objectives: List[ImplementationObjective],
    control: SecurityControl,
    duplicate: bool,
    origination: Optional[str] = None,
    customer_responsibility: Optional[str] = None,
    cloud_responsibility: Optional[str] = None,
):
    """
    Handle the implementation objectives for the given objective, option, and control implementation.
    :param ControlObjective objective: The control objective.
    :param str part_statement: The statement text for this part.
    :param Optional[str] status: The implementation status.
    :param Union[ControlImplementation, int, None] control_implementation: The control implementation object or ID.
    :param List[ImplementationObjective] imp_objectives: List to collect implementation objectives.
    :param SecurityControl control: The security control.
    :param bool duplicate: Whether the option is a duplicate will add note if True.
    :param Optional[str] origination: The origination of the implementation.
    :param Optional[str] customer_responsibility: Customer responsibility text extracted from part content.
    :param Optional[str] cloud_responsibility: Cloud/service provider responsibility text extracted from part content.
    """
    if isinstance(status, ControlImplementationStatus):
        status = status.value

    # Ensure part_statement is valid and format with HTML for proper rendering
    statement = _format_part_statement(part_statement) if part_statement else ""

    imp_obj = ImplementationObjective(
        securityControlId=control.id,
        implementationId=control_implementation.id if hasattr(control_implementation, "id") else control_implementation,
        objectiveId=objective.id,
        optionId=None,
        status=status,
        statement=statement,
        notes="#replicated-data-part" if duplicate else "",
        responsibility=origination,
        customerResponsibility=customer_responsibility,
        cloudResponsibility=cloud_responsibility,
    )
    if imp_obj not in imp_objectives:
        imp_objectives.append(imp_obj)


def add_implementation_to_list(objective: ImplementationObjective, implementation_list: List[ImplementationObjective]):
    """
    Add the implementation objective to the list.
    :param ImplementationObjective objective: The implementation objective to add.
    :param List[ImplementationObjective] implementation_list: The list of implementation objectives.
    """
    if objective not in implementation_list:
        implementation_list.append(objective)


def get_matching_objectives(control_objectives: List[ControlObjective], part_name: str) -> List[ControlObjective]:
    """
    Find and return the control objectives that match the specified part name.
    :param List[ControlObjective] control_objectives: The list of control objectives to search.
    :param str part_name: The part name to match.
    :return: A list of control objectives that match the specified part name.
    :rtype: List[ControlObjective]
    """
    matching_objectives = []
    try:
        matching_objectives = get_objectives_by_matching_property(
            control_objectives=control_objectives, property_name="name", part_letter=get_part_letter(part_name)
        )
    except Exception as e:
        logger.warning(f"Error finding matching objectives: {e}")
    return matching_objectives


def get_part_letter(part: str) -> str:
    """
    Get the part letter from the part name.
    :param str part: The part name.
    :return: The part letter.
    :rtype: str
    """
    return part.lower().replace("part", "").strip()  # Assuming the format "Part X" where X is the part letter.


def get_objectives_by_matching_property(
    control_objectives: List[ControlObjective], property_name: str, part_letter: str
) -> List[ControlObjective]:
    """
    Find and return the control objectives that match the specified property name.
    :param List[ControlObjective] control_objectives: The list of control objectives to search.
    :param str property_name: The property name to match.
    :param str part_letter: The part letter to match.
    :return: A list of control objectives that match the specified property name.
    :rtype: List[ControlObjective]
    """
    matching_objectives = []
    try:
        matching_objectives = [
            o for o in control_objectives if part_letter.lower() in getattr(o, property_name).lower()
        ]
    except Exception as e:
        logger.warning(f"Error finding matching objectives: {e}")
    return matching_objectives


def handle_params(
    parameters: List[Dict],
    control: SecurityControl,
    control_implementation: ControlImplementation,
):
    """
    Handle the parameters for the given control and control implementation.
    :param List[Dict] parameters: The parameters to handle.
    :param SecurityControl control: The security control object.
    :param ControlImplementation control_implementation: The control implementation object.

    """
    # Log the initial handling of parameters for the given control.
    logger.debug("Handling Parameters for Control: %s - %d", control.id, len(parameters))
    param_mapper = RosettaStone()
    if not param_mapper.map:
        param_mapper.load_fedramp_version_5_mapping()
        param_mapper.lookup_l0_by_l1()
    mappings = param_mapper.map
    base_control_params = ControlParameter.get_by_control(control_id=control.id)
    base_control_params_dict = {param.otherId: param for param in base_control_params}
    for param in parameters:
        gen_param_name = f"Parameter {param.get('name').replace(' ', '')}"
        if gen_param_name not in mappings:
            logger.debug("Parameter: %s not found in mappings", gen_param_name)
        logger.debug("Processing parameter: %s", gen_param_name)
        control_param_name = mappings.get(gen_param_name)
        base_control_param = base_control_params_dict.get(control_param_name)

        if base_control_param:
            existing_params = Parameter.get_by_parent_id(parent_id=control_implementation.id)
            existing_param_names_dict = {param.name: param for param in existing_params}
            existing_parameter = existing_param_names_dict.get(control_param_name)
            existing_param_by_external_name_dict = {param.externalPropertyName: param for param in existing_params}
            if not existing_parameter:
                existing_parameter = existing_param_by_external_name_dict.get(control_param_name)
            try:
                if not existing_params or not existing_parameter:
                    Parameter(
                        controlImplementationId=control_implementation.id,
                        name=param.get("name").strip(),
                        value=param.get("value"),
                        externalPropertyName=base_control_param.otherId,
                        parentParameterId=base_control_param.id,
                    ).create()
                else:
                    existing_param = existing_parameter
                    if existing_param.name == control_param_name:
                        existing_param.value = param.get("value")
                        existing_param.parentParameterId = base_control_param.id
                        existing_param.save()
            except Exception as e:
                logger.warning(f"warning handling parameter: {e}")
        else:
            logger.warning(f"Param: {gen_param_name} not found: {control_param_name}")


def build_params(base_control_params: List[ControlParameter], parameters: List[Dict]) -> List[Dict]:
    """
    Builds the parameters for the control implementation.
    :param List[ControlParameter] base_control_params: The base control parameters.
    :param List[Dict] parameters: The parameters to build.
    :return: List[Dict]: The built parameters.
    :rtype: List[Dict]
    """
    new_params = []
    if len(base_control_params) >= len(parameters):
        for index, base_param in enumerate(base_control_params):
            if len(parameters) >= index + 1:
                new_param_dict = {}
                new_param_dict["name"] = base_param.parameterId
                new_param_dict["value"] = parameters[index].get("value") if parameters[index] else base_param.default
                new_params.append(new_param_dict)
    return new_params


def map_implementation_status(status: str) -> str:
    """
    Maps the implementation status to the appropriate value.
    :param str status: The status to map.
    :return: The mapped status.
    :rtype: str
    """

    if status and status.lower() == "implemented":
        return ControlImplementationStatus.Implemented.value
    elif status and status.lower() == "fully implemented":
        return ControlImplementationStatus.Implemented.value
    elif status and status.lower() == "partially implemented":
        return ControlImplementationStatus.PartiallyImplemented.value
    elif status and status.lower() == "planned":
        return ControlImplementationStatus.Planned.value
    elif status and status.lower() == "not applicable":
        return ControlImplementationStatus.NA.value
    elif status and status.lower() == "alternative implementation":
        return ControlImplementationStatus.FullyImplemented.value
    else:
        return ControlImplementationStatus.NotImplemented.value


def update_existing_control(
    control: ControlImplementation, status: str, statement: str, responsibility: str, primary_role: Dict, parent_id: int
):
    """
    Updates an existing control with new information.
    :param ControlImplementation control: The control implementation object.
    :param str status: The status of the implementation.
    :param str statement: The statement of the implementation.
    :param str responsibility: The responsibility of the implementation.
    :param Dict primary_role: The primary role of the implementation.
    :param int parent_id: The parent ID.
    """
    state_text = clean_statement(statement)
    justify = (
        state_text or "Unknown" if map_implementation_status(status) == ControlImplementationStatus.NA.value else None
    )
    control.parentId = parent_id
    control.status = map_implementation_status(status)
    control.exclusionJustification = justify
    _, planned_date, steps_to_implement = create_control_implementation_defaults(status)
    if not control.plannedImplementationDate and planned_date:
        control.plannedImplementationDate = planned_date
    if not control.stepsToImplement and steps_to_implement:
        control.stepsToImplement = steps_to_implement
    # Only update implementation if we have a valid new value, otherwise preserve existing
    if state_text:
        control.implementation = state_text
    elif not control.implementation:
        # If status requires implementation statement but none exists, provide default
        mapped_status = map_implementation_status(status)
        if mapped_status in (
            ControlImplementationStatus.Implemented.value,
            ControlImplementationStatus.FullyImplemented.value,
            ControlImplementationStatus.PartiallyImplemented.value,
        ):
            control.implementation = "Implementation details pending review."

    # Only update responsibility if we have a valid new value, otherwise preserve existing
    new_responsibility = map_responsibility(responsibility)
    if new_responsibility:
        control.responsibility = new_responsibility
    elif not control.responsibility:
        # If no responsibility specified in document and none exists on control,
        # default to Service Provider Corporate (most common for FedRAMP)
        control.responsibility = ImplementationControlOrigin.SERVICE_PROVIDER_CORPORATE.value
    control.systemRoleId = primary_role.get("id") if primary_role and isinstance(primary_role, dict) else None

    # Convert the model to a dict and back to a model to workaround these odd 400 errors.
    try:
        control.save()
    except Exception as e:
        logger.warning(f"Error updating control: {control.id} - {e}")


def format_alternative_control_key(control_id: str) -> str:
    """
    Formats the key for the alternative control information.
    :param str control_id: The control ID to format.
    :return: The formatted control ID.
    :rtype: str
    """
    # Unpack the control_family and the rest (assumes there's at least one '-')
    control_family, *rest = control_id.split("-")
    rest_joined = "-".join(rest)  # Join the rest back in case there are multiple '-'

    # Check for '(' and split if needed, also handling the case without '(' more cleanly
    if "(" in rest_joined:
        control_num, control_ending = rest_joined.split("(", 1)  # Split once
        control_ending = control_ending.rstrip(")")  # Remove trailing ')' if present
        alternative_control_id = f"{control_family}-{format_int(int(control_num))}({control_ending})"
    else:
        control_num = rest_joined
        alternative_control_id = f"{control_family}-{format_int(int(control_num))}"

    return alternative_control_id


def format_int(n: int) -> str:
    """
    Formats an integer to a string with a leading zero if it's a single digit.
    :param int n: The integer to format.
    :return: The formatted integer as a string.
    :rtype: str
    """
    # Check if the integer is between 0 and 9 (inclusive)
    if 0 <= n <= 9:
        # Prepend a "0" if it's a single digit
        return f"0{n}"
    else:
        # Just convert to string if it's not a single digit
        return str(n)


def build_data_dict(tables: List) -> Dict:
    """
    Builds a dictionary from a list of tables.

    :param List tables: A list of tables.
    :return: A dictionary containing the tables.
    :rtype: Dict
    """
    table_dict = {}
    for table in tables:
        k_parts = list(table.keys())[0].split()
        if k_parts:
            key_control = k_parts[0]
            if key_control in table_dict:
                table_dict[key_control].append(table)
            else:
                table_dict[key_control] = [table]
    return table_dict


def processing_data_from_ssp_doc(processed_data, user_id, doc_text_dict: Dict) -> int:
    """
    Finalizes the processing of data by creating necessary records in the system.
    :param Dict[str, Any] processed_data: The processed data.
    :param str user_id: The ID of the user performing the operation.
    :param Dict[str, str] doc_text_dict: The dictionary containing the text from the document.
    :return: The ID of the parent object.
    :rtype: int
    """
    processed_data["doc_text_dict"] = doc_text_dict
    # Process SSP Document if present
    if not processed_data.get("ssp_doc"):
        logger.warning("No SSP Document found")
        sys.exit(1)
    ssp = process_ssp_doc(
        processed_data.get("ssp_doc"),
        processed_data,
        user_id,
    )
    parent_id = ssp.id
    logger.info(f"Parent ID: {parent_id}")
    parent_module = "securityplans"
    approval_date = ssp.approvalDate

    # Create stakeholders
    if processed_data.get("stakeholders"):
        create_stakeholders(processed_data.get("stakeholders"), parent_id, parent_module)
    # Process services if present
    if processed_data.get("services"):
        create_leveraged_authorizations(
            processed_data["services"], user_id, parent_id, approval_date
        )  # Assuming parent_id is the ssp_id for simplicity

    # Process ports and protocols if present
    if processed_data.get("ports_and_protocols"):
        logger.info(f"Total ports collected from document: {len(processed_data['ports_and_protocols'])}")
        create_ports_and_protocols(
            processed_data["ports_and_protocols"], parent_id
        )  # Assuming parent_id is the ssp_id for simplicity
    return parent_id


def create_stakeholders(stakeholders: List[Person], parent_id: int, parent_module: str) -> None:
    """
    Creates stakeholders in RegScale.
    :param List[Person] stakeholders: A list of Person objects representing the stakeholders.
    :param int parent_id: The ID of the parent object.
    :param str parent_module: The parent module.

    """
    logger.info(f"Creating Stakeholders: {parent_id} - {parent_module}")
    existing_stakeholders: List[StakeHolder] = StakeHolder.get_all_by_parent(
        parent_id=parent_id, parent_module=parent_module
    )
    for person in stakeholders:
        existing_stakeholder = next(
            (s for s in existing_stakeholders if s.name == person.name and s.email == person.email),
            None,
        )
        if existing_stakeholder:
            logger.debug(existing_stakeholder.model_dump())
            existing_stakeholder.name = person.name
            existing_stakeholder.email = person.email
            existing_stakeholder.phone = person.phone
            existing_stakeholder.title = person.title
            existing_stakeholder.save()
        else:
            StakeHolder(
                name=person.name,
                email=person.email,
                phone=person.phone,
                title=person.title,
                parentId=parent_id,
                parentModule=parent_module,
            ).create()


def process_cloud_info(ssp_doc: SSPDoc) -> Dict:
    """
    Processes the cloud information from the SSP document.
    :param SSPDoc ssp_doc: The SSP document object.
    :return: A dictionary containing the cloud deployment model information.
    :rtype: Dict
    """
    return {
        "saas": "SaaS" in ssp_doc.service_model,
        "paas": "PaaS" in ssp_doc.service_model,
        "iaas": "IaaS" in ssp_doc.service_model,
        "other_service_model": not any(service in ssp_doc.service_model for service in ["SaaS", "PaaS", "IaaS"]),
        "deploy_gov": "gov" in ssp_doc.deployment_model.lower() or "government" in ssp_doc.deployment_model.lower(),
        "deploy_hybrid": "hybrid" in ssp_doc.deployment_model.lower(),
        "deploy_private": "private" in ssp_doc.deployment_model.lower(),
        "deploy_public": "public" in ssp_doc.deployment_model.lower(),
        "deploy_other": not any(
            deploy in ssp_doc.deployment_model.lower()
            for deploy in ["gov", "government", "hybrid", "private", "public"]
        ),
    }


def process_ssp_doc(
    ssp_doc: SSPDoc,
    data: Dict,
    user_id: str,
) -> SecurityPlan:
    """
    Processes the SSP document.
    :param SSPDoc ssp_doc: The SSP document object.
    :param Dict[str, Any] data: The processed data.
    :param str user_id: The ID of the user performing the operation.
    :return: The security plan object.
    :rtype: SecurityPlan
    """
    if ssp_doc:
        cloud_info = process_cloud_info(ssp_doc)
        plans = SecurityPlan.get_list()
        plan_count = len(plans)
        logger.info("Found SSP Count of: %d", plan_count)
        ssp = None
        for plan in plans:
            if plan.systemName == ssp_doc.name:
                ssp = plan  # No extra API call needed - plan is already a full SecurityPlan object
                logger.info("Found SSP: %s", plan.systemName)
                break
        if not ssp:
            ssp = create_ssp(ssp_doc, cloud_info, user_id, data)
        else:
            ssp = save_security_plan_info(ssp, cloud_info, ssp_doc, user_id, data)
        return ssp


def get_expiration_date(dt_format: Optional[str] = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Return the expiration date, which is 3 years from today

    :param Optional[str] dt_format: desired format for datetime string, defaults to "%Y-%m-%d %H:%M:%S"
    :return: Expiration date as a string, 3 years from today
    :rtype: str
    """
    expiration_date = datetime.datetime.now() + relativedelta(years=3)
    return expiration_date.strftime(dt_format)


def find_text_by_heading(doc_text_dict: Dict, target_heading: str) -> Optional[str]:
    """
    Find text content by fuzzy matching heading names.

    FedRAMP documents often have numbered headings like "9.1 System Description"
    instead of just "System Description". This function finds headings that contain
    the target text (case-insensitive).

    :param Dict doc_text_dict: Dictionary mapping headings to paragraph lists.
    :param str target_heading: The heading text to search for.
    :return: The joined text from the matching heading, or None if not found.
    :rtype: Optional[str]
    """
    # First try exact match
    if target_heading in doc_text_dict:
        return " ".join(doc_text_dict[target_heading])

    # Try case-insensitive partial match
    target_lower = target_heading.lower()
    for heading, paragraphs in doc_text_dict.items():
        if target_lower in heading.lower():
            logger.debug("Fuzzy matched heading '%s' to '%s'", target_heading, heading)
            return " ".join(paragraphs)

    return None


def _parse_assurance_level(dil_upper: str, prefix: str) -> str:
    """
    Parse a single assurance level (IAL, AAL, or FAL) from the string.

    :param str dil_upper: The uppercase digital identity level string.
    :param str prefix: The prefix to look for (IAL, AAL, or FAL).
    :return: The assurance level ("1", "2", "3") or empty string.
    :rtype: str
    """
    for level in ("3", "2", "1"):
        if f"{prefix}{level}" in dil_upper or f"{prefix} {level}" in dil_upper:
            return level
    return ""


def parse_digital_identity_level(dil_string: Optional[str]) -> Dict[str, str]:
    """
    Parse digital identity level string to extract IAL, AAL, and FAL values.

    :param Optional[str] dil_string: The digital identity level string from the SSP
    :return: Dictionary with identity_assurance_level, authenticator_assurance_level, and federation_assurance_level
    :rtype: Dict[str, str]
    """
    if not dil_string:
        return {
            "identity_assurance_level": "",
            "authenticator_assurance_level": "",
            "federation_assurance_level": "",
        }

    dil_upper = dil_string.upper()
    return {
        "identity_assurance_level": _parse_assurance_level(dil_upper, "IAL"),
        "authenticator_assurance_level": _parse_assurance_level(dil_upper, "AAL"),
        "federation_assurance_level": _parse_assurance_level(dil_upper, "FAL"),
    }


def create_ssp(ssp_doc: SSPDoc, cloud_info: Dict, user_id: str, data: Dict) -> SecurityPlan:
    """
    Creates a security plan in RegScale.
    :param SSPDoc ssp_doc: The SSP document object.
    :param Dict cloud_info: A dictionary containing cloud deployment model information.
    :param str user_id: The ID of the user creating the security plan.
    :param Dict[str, Any] data: The processed data.
    :return: The security plan object.
    :rtype: SecurityPlan
    """
    compliance_setting = get_fedramp_compliance_setting()
    doc_text_dict = data.get("doc_text_dict")

    # Use fuzzy heading matching to handle numbered headings like "9.1 System Description"
    systemdescription = find_text_by_heading(doc_text_dict, SYSTEM_DESCRIPTION)
    authboundarydescription = find_text_by_heading(doc_text_dict, AUTHORIZATION_BOUNDARY)
    networkarchdescription = find_text_by_heading(doc_text_dict, NETWORK_ARCHITECTURE)
    systemenvironment = find_text_by_heading(doc_text_dict, ENVIRONMENT)
    dataflows = find_text_by_heading(doc_text_dict, DATA_FLOW)
    lawsandregs = find_text_by_heading(doc_text_dict, LAWS_AND_REGULATIONS)
    categorization_justification = find_text_by_heading(doc_text_dict, CATEGORIZATION_JUSTIFICATION)
    system_function = find_text_by_heading(doc_text_dict, SYSTEM_FUNCTION)
    # Get stakeholder users from document
    owner = data.get("owner")
    isso = data.get("isso")
    authorizing_official = data.get("authorizing_official")
    security_manager = data.get("security_manager")
    prepared_by: PreparedBy = data.get("prepared_by")
    prepared_for: PreparedBy = data.get("prepared_for")
    compliance_setting_id = compliance_setting.id if compliance_setting else 2

    # Get system info from System Information table
    system_url = data.get("system_url", "")
    system_type = data.get("system_type", "Major Application")

    # Get additional identifiers from System Information table
    other_identifier = data.get("other_identifier", "")
    ditpr_id = data.get("ditpr_id", "")
    emass_id = data.get("emass_id", "")
    tracking_id = data.get("tracking_id", "")

    # Get user information from User tables
    users_count = data.get("users", 0)
    internal_users = data.get("internal_users", 0)
    external_users = data.get("external_users", 0)
    privileged_users = data.get("privileged_users", 0)
    users_mfa = data.get("users_mfa", 0)

    # Parse digital identity level to get IAL, AAL, FAL
    dil_values = parse_digital_identity_level(ssp_doc.digital_identity_level)

    ssp = SecurityPlan(
        systemName=ssp_doc.name,
        fedrampId=ssp_doc.fedramp_id,
        systemOwnerId=owner.id if owner else user_id,
        planInformationSystemSecurityOfficerId=isso.id if isso else user_id,
        planAuthorizingOfficialId=authorizing_official.id if authorizing_official else user_id,
        systemSecurityManagerId=security_manager.id if security_manager else None,
        status="Operational",
        systemType=system_type,
        systemUrl=system_url,
        description=systemdescription,
        authorizationBoundary=authboundarydescription,
        networkArchitecture=networkarchdescription,
        environment=systemenvironment,
        dataFlow=dataflows,
        lawsAndRegulations=lawsandregs,
        categorizationJustification=categorization_justification or "",
        tenantsId=1,
        # Set C/I/A to the overall FIPS 199 level (common in FedRAMP where all three are typically the same)
        confidentiality=ssp_doc.fips_199_level or "",
        integrity=ssp_doc.fips_199_level or "",
        availability=ssp_doc.fips_199_level or "",
        overallCategorization=ssp_doc.fips_199_level,
        bModelSaaS=cloud_info.get("saas", False),
        bModelPaaS=cloud_info.get("paas", False),
        bModelIaaS=cloud_info.get("iaas", False),
        bModelOther=cloud_info.get("other_service_model", False),
        bDeployGov=cloud_info.get("deploy_gov", False),
        bDeployHybrid=cloud_info.get("deploy_hybrid", False),
        bDeployPrivate=cloud_info.get("deploy_private", False),
        bDeployPublic=cloud_info.get("deploy_public", False),
        bDeployOther=cloud_info.get("deploy_other", False),
        deployOtherRemarks=ssp_doc.deployment_model,
        dateSubmitted=ssp_doc.date_submitted,
        approvalDate=ssp_doc.approval_date,
        expirationDate=get_expiration_date(),
        fedrampAuthorizationLevel=ssp_doc.fips_199_level,
        fedrampAuthorizationType=ssp_doc.authorization_path or "",
        fedrampAuthorizationStatus="Authorized" if ssp_doc.approval_date else "In Process",
        fedrampDateAuthorized=ssp_doc.approval_date if ssp_doc.approval_date else "",
        identityAssuranceLevel=dil_values.get("identity_assurance_level", ""),
        authenticatorAssuranceLevel=dil_values.get("authenticator_assurance_level", ""),
        federationAssuranceLevel=dil_values.get("federation_assurance_level", ""),
        defaultAssessmentDays=365,
        version=data.get("version", "1.0"),
        executiveSummary="\n".join(doc_text_dict.get("Introduction", [])),
        purpose=system_function or "\n".join(doc_text_dict.get("Purpose", [])),
        complianceSettingsId=compliance_setting_id,
        # Additional identifiers
        otherIdentifier=other_identifier,
        ditprId=ditpr_id,
        emassId=emass_id,
        trackingId=tracking_id,
        # User counts
        users=users_count,
        internalUsers=internal_users,
        externalUsers=external_users,
        privilegedUsers=privileged_users,
        usersMFA=users_mfa,
    )
    if prepared_by:
        ssp.cspOrgName = prepared_by.name
        ssp.cspAddress = prepared_by.street
        ssp.cspOffice = prepared_by.building
        ssp.cspCityState = prepared_by.city_state_zip
    if prepared_for:
        ssp.prepOrgName = prepared_for.name
        ssp.prepAddress = prepared_for.street
        ssp.prepOffice = prepared_for.building
        ssp.prepCityState = prepared_for.city_state_zip
    return ssp.create()


def _set_ssp_identifiers(ssp: SecurityPlan, data: Dict) -> None:
    """Set additional identifier fields on the SSP if values exist."""
    identifier_mappings = [
        ("other_identifier", "otherIdentifier"),
        ("ditpr_id", "ditprId"),
        ("emass_id", "emassId"),
        ("tracking_id", "trackingId"),
    ]
    for data_key, ssp_attr in identifier_mappings:
        value = data.get(data_key, "")
        if value:
            setattr(ssp, ssp_attr, value)


def _set_ssp_user_counts(ssp: SecurityPlan, data: Dict) -> None:
    """Set user count fields on the SSP if values exist."""
    count_mappings = [
        ("users", "users"),
        ("internal_users", "internalUsers"),
        ("external_users", "externalUsers"),
        ("privileged_users", "privilegedUsers"),
        ("users_mfa", "usersMFA"),
    ]
    for data_key, ssp_attr in count_mappings:
        value = data.get(data_key, 0)
        if value:
            setattr(ssp, ssp_attr, value)


def _set_ssp_prepared_info(
    ssp: SecurityPlan, prepared_by: Optional[PreparedBy], prepared_for: Optional[PreparedBy]
) -> None:
    """Set prepared by and prepared for organization info on the SSP."""
    if prepared_by:
        ssp.cspOrgName = prepared_by.name
        ssp.cspAddress = prepared_by.street
        ssp.cspOffice = prepared_by.building
        ssp.cspCityState = prepared_by.city_state_zip
    if prepared_for:
        ssp.prepOrgName = prepared_for.name
        ssp.prepAddress = prepared_for.street
        ssp.prepOffice = prepared_for.building
        ssp.prepCityState = prepared_for.city_state_zip


def save_security_plan_info(
    ssp: SecurityPlan, cloud_info: Dict, ssp_doc: SSPDoc, user_id: str, data: Dict
) -> SecurityPlan:
    """
    Saves the security plan information to the database.
    :param SecurityPlan ssp: The security plan object.
    :param Dict cloud_info: A dictionary containing cloud deployment model information.
    :param SSPDoc ssp_doc: The SSP document object.
    :param str user_id: The ID of the user performing the operation.
    :param Dict[str, Any] data: The processed data.
    :return: The updated security plan object.
    :rtype: SecurityPlan
    """
    prepared_by: PreparedBy = data.get("prepared_by")
    prepared_for: PreparedBy = data.get("prepared_for")
    doc_text_dict: Dict = data.get("doc_text_dict")
    owner = data.get("owner")
    isso = data.get("isso")
    authorizing_official = data.get("authorizing_official")
    security_manager = data.get("security_manager")

    dil_values = parse_digital_identity_level(ssp_doc.digital_identity_level)

    # Extract text descriptions from document using fuzzy heading matching
    systemdescription = find_text_by_heading(doc_text_dict, SYSTEM_DESCRIPTION)
    authboundarydescription = find_text_by_heading(doc_text_dict, AUTHORIZATION_BOUNDARY)
    networkarchdescription = find_text_by_heading(doc_text_dict, NETWORK_ARCHITECTURE)
    systemenvironment = find_text_by_heading(doc_text_dict, ENVIRONMENT)
    dataflows = find_text_by_heading(doc_text_dict, DATA_FLOW)
    lawsandregs = find_text_by_heading(doc_text_dict, LAWS_AND_REGULATIONS)
    categorization_justification = find_text_by_heading(doc_text_dict, CATEGORIZATION_JUSTIFICATION)
    system_function = find_text_by_heading(doc_text_dict, SYSTEM_FUNCTION)

    logger.info("Updating SSP: %s", ssp.systemName)
    ssp.fedrampId = ssp_doc.fedramp_id
    ssp.systemName = ssp_doc.name
    ssp.status = "Operational"
    ssp.systemType = data.get("system_type", "") or ssp.systemType
    ssp.systemUrl = data.get("system_url", "") or ssp.systemUrl
    ssp.description = systemdescription or ssp_doc.description
    ssp.authorizationBoundary = authboundarydescription
    ssp.networkArchitecture = networkarchdescription
    ssp.environment = systemenvironment
    ssp.dataFlow = dataflows
    ssp.lawsAndRegulations = lawsandregs
    ssp.categorizationJustification = categorization_justification or ssp.categorizationJustification
    ssp.systemOwnerId = owner.id if owner else user_id
    ssp.planInformationSystemSecurityOfficerId = isso.id if isso else user_id
    ssp.planAuthorizingOfficialId = authorizing_official.id if authorizing_official else user_id
    if security_manager:
        ssp.systemSecurityManagerId = security_manager.id
    ssp.confidentiality = ssp_doc.fips_199_level or ""
    ssp.integrity = ssp_doc.fips_199_level or ""
    ssp.availability = ssp_doc.fips_199_level or ""
    ssp.overallCategorization = ssp_doc.fips_199_level
    ssp.bModelSaaS = cloud_info.get("saas", False)
    ssp.bModelPaaS = cloud_info.get("paas", False)
    ssp.bModelIaaS = cloud_info.get("iaas", False)
    ssp.bModelOther = cloud_info.get("other_service_model", False)
    ssp.bDeployGov = cloud_info.get("deploy_gov", False)
    ssp.bDeployHybrid = cloud_info.get("deploy_hybrid", False)
    ssp.bDeployPrivate = cloud_info.get("deploy_private", False)
    ssp.bDeployPublic = cloud_info.get("deploy_public", False)
    ssp.bDeployOther = cloud_info.get("deploy_other", False)
    ssp.deployOtherRemarks = ssp_doc.deployment_model
    ssp.dateSubmitted = ssp_doc.date_submitted
    ssp.approvalDate = ssp_doc.approval_date
    ssp.expirationDate = get_expiration_date()
    ssp.fedrampAuthorizationLevel = ssp_doc.fips_199_level
    ssp.fedrampAuthorizationType = ssp_doc.authorization_path or ""
    ssp.fedrampAuthorizationStatus = "Authorized" if ssp_doc.approval_date else "In Process"
    ssp.fedrampDateAuthorized = ssp_doc.approval_date if ssp_doc.approval_date else ""
    ssp.identityAssuranceLevel = dil_values.get("identity_assurance_level", "")
    ssp.authenticatorAssuranceLevel = dil_values.get("authenticator_assurance_level", "")
    ssp.federationAssuranceLevel = dil_values.get("federation_assurance_level", "")
    ssp.version = data.get("version", "1.0")

    _set_ssp_identifiers(ssp, data)
    _set_ssp_user_counts(ssp, data)
    _set_ssp_prepared_info(ssp, prepared_by, prepared_for)

    ssp.executiveSummary = "\n".join(doc_text_dict.get("Introduction", []))
    ssp.purpose = system_function or "\n".join(doc_text_dict.get("Purpose", []))
    ssp.save()
    return ssp


def _find_existing_leveraged_auth(
    existing_authorizations: List[LeveragedAuthorization],
    service: LeveragedService,
) -> Optional[LeveragedAuthorization]:
    """
    Find an existing leveraged authorization that matches the service.

    Uses multiple criteria for matching to avoid duplicates:
    1. First tries to match by title (CSP name) - most reliable
    2. Falls back to matching by fedrampId if title doesn't match

    :param List[LeveragedAuthorization] existing_authorizations: Existing authorizations to search.
    :param LeveragedService service: The service to find a match for.
    :return: The matching authorization or None.
    :rtype: Optional[LeveragedAuthorization]
    """
    # Normalize the CSP name for comparison
    service_title = (service.fedramp_csp_name or "").strip().lower()

    for auth in existing_authorizations:
        auth_title = (auth.title or "").strip().lower()

        # Match by title (CSP name) - primary match criterion
        if service_title and auth_title and service_title == auth_title:
            return auth

        # Match by fedrampId if title doesn't match but fedrampId is available and matches
        if service.fedramp_id and auth.fedrampId and service.fedramp_id == auth.fedrampId:
            return auth

    return None


def _update_leveraged_auth_fields(existing: LeveragedAuthorization, service: LeveragedService) -> None:
    """Update existing leveraged authorization fields from service data."""
    if service.fedramp_csp_name:
        existing.title = service.fedramp_csp_name
    if service.fedramp_id:
        existing.fedrampId = service.fedramp_id
    if service.cso_service:
        existing.servicesUsed = service.cso_service
    if service.data_types:
        existing.dataTypes = service.data_types
    if service.authorized_user_authentication:
        existing.authorizedUserTypes = service.authorized_user_authentication
    if service.impact_level:
        existing.impactLevel = _map_impact_level(service.impact_level)
    if service.agreement_type:
        existing.natureOfAgreement = _map_nature_of_agreement(service.agreement_type)
    if service.authorization_type:
        existing.authorizationType = _map_authorization_type(service.authorization_type)


def _create_new_leveraged_auth(service: LeveragedService, user_id: str, ssp_id: int, approval_date: str) -> None:
    """Create a new leveraged authorization from service data."""
    LeveragedAuthorization(
        title=service.fedramp_csp_name or UNKNOWN_CSP,
        fedrampId=service.fedramp_id or NOT_SPECIFIED,
        ownerId=user_id,
        securityPlanId=ssp_id,
        dateAuthorized=approval_date if approval_date else None,
        servicesUsed=service.cso_service or NOT_SPECIFIED,
        dataTypes=service.data_types or NOT_SPECIFIED,
        authorizationType=_map_authorization_type(service.authorization_type),
        authenticationType=service.authorized_user_authentication or NOT_SPECIFIED,
        authorizedUserTypes=service.authorized_user_authentication or NOT_SPECIFIED,
        impactLevel=_map_impact_level(service.impact_level),
        natureOfAgreement=_map_nature_of_agreement(service.agreement_type),
        tenantsId=1,
    ).create()
    logger.debug("Created LeveragedAuthorization: %s", service.fedramp_csp_name)


def create_leveraged_authorizations(services: List[LeveragedService], user_id: str, ssp_id: int, approval_date: str):
    """
    Creates leveraged authorization records for each service.

    :param List[LeveragedService] services: A list of services to be created.
    :param str user_id: The ID of the user creating the services.
    :param int ssp_id: The ID of the security plan these services are associated with.
    :param str approval_date: The date of approval.
    """
    existing_authorizations: List[LeveragedAuthorization] = LeveragedAuthorization.get_all_by_parent(parent_id=ssp_id)
    logger.info("Found %d existing LeveragedAuthorizations", len(existing_authorizations))

    processed_titles: set = set()

    for service in services:
        service_title = (service.fedramp_csp_name or "").strip().lower()
        if service_title in processed_titles:
            logger.debug("Skipping duplicate service in import: %s", service.fedramp_csp_name)
            continue
        processed_titles.add(service_title)

        existing_service = _find_existing_leveraged_auth(existing_authorizations, service)

        if existing_service:
            _update_existing_leveraged_auth(existing_service, service, user_id, approval_date)
        else:
            _try_create_leveraged_auth(service, user_id, ssp_id, approval_date)


def _update_existing_leveraged_auth(
    existing: LeveragedAuthorization, service: LeveragedService, user_id: str, approval_date: str
) -> None:
    """Update an existing leveraged authorization."""
    logger.debug("Updating existing LeveragedAuthorization: %s", existing.title)
    _update_leveraged_auth_fields(existing, service)
    existing.ownerId = user_id
    if approval_date:
        existing.dateAuthorized = approval_date
    try:
        existing.save()
    except Exception as e:
        logger.warning("Failed to update LeveragedAuthorization %s: %s", existing.title, str(e))


def _try_create_leveraged_auth(service: LeveragedService, user_id: str, ssp_id: int, approval_date: str) -> None:
    """Try to create a new leveraged authorization with error handling."""
    try:
        _create_new_leveraged_auth(service, user_id, ssp_id, approval_date)
    except Exception as e:
        logger.warning(
            "Failed to create LeveragedAuthorization '%s': %s - continuing with import",
            service.fedramp_csp_name,
            str(e),
        )


def _port_matches_existing(port_to_create: PortsProtocol, existing_ports: List[PortsProtocol]) -> bool:
    """Check if the port to create already exists in the list of existing ports."""
    for existing_port in existing_ports:
        if (
            existing_port.startPort == port_to_create.startPort
            and existing_port.endPort == port_to_create.endPort
            and existing_port.protocol == port_to_create.protocol
            and existing_port.service == port_to_create.service
            and existing_port.purpose == port_to_create.purpose
            and existing_port.usedBy == port_to_create.usedBy
            and existing_port.parentId == port_to_create.parentId
            and existing_port.parentModule == port_to_create.parentModule
        ):
            return True
    return False


def _should_skip_port_entry(port: PortsAndProtocolData) -> bool:
    """Check if a port entry should be skipped due to missing required fields."""
    if not port.protocol or not port.protocol.strip():
        logger.debug("Skipping port entry with missing protocol: %s", port)
        return True
    if port.start_port == 0 and port.end_port == 0 and port.port == 0:
        logger.debug("Skipping port entry with no valid port number: %s", port)
        return True
    return False


def create_ports_and_protocols(ports_and_protocols: List[PortsAndProtocolData], ssp_id: int):
    """
    Creates port and protocol records for each entry.

    :param List[PortsAndProtocolData] ports_and_protocols: A list of ports and protocols to be created.
    :param int ssp_id: The ID of the security plan these ports and protocols are associated with.

    """
    existing_ports: List[PortsProtocol] = PortsProtocol.get_all_by_parent(
        parent_id=ssp_id, parent_module="securityplans"
    )
    logger.info("Found %d existing Ports & Protocols", len(existing_ports))
    created_count = 0
    skipped_count = 0

    for port in ports_and_protocols:
        if _should_skip_port_entry(port):
            skipped_count += 1
            continue

        port_to_create = PortsProtocol(
            service=port.service or "",
            startPort=port.start_port,
            endPort=port.end_port,
            protocol=port.protocol,
            purpose=port.purpose or "N/A",
            usedBy=port.used_by or "",
            parentId=ssp_id,
            parentModule="securityplans",
        )

        if _port_matches_existing(port_to_create, existing_ports):
            continue

        try:
            port_to_create.create()
            created_count += 1
        except Exception as e:
            logger.warning("Failed to create port entry: %s - %s", port, e)
            skipped_count += 1

    logger.info("Created %d Port & Protocols (skipped %d invalid entries)", created_count, skipped_count)


def get_image_caption_mapping(file_name: str) -> Dict[str, str]:
    """
    Extract figure captions and map them to actual image filenames in the DOCX.

    Parses the DOCX relationships file to map relationship IDs to image paths,
    then combines with figure captions to create filename-to-caption mapping.

    :param str file_name: The path to the DOCX file.
    :return: Dictionary mapping image filenames to their captions.
    :rtype: Dict[str, str]
    """
    import xml.etree.ElementTree as ET

    caption_mapping: Dict[str, str] = {}

    try:
        # Parse the DOCX to get figure captions (relationship ID -> caption)
        doc_parser = SSPDocParser(file_name)
        rid_to_caption = doc_parser.get_figure_captions()

        if not rid_to_caption:
            logger.debug("No figure captions found in document")
            return caption_mapping

        # Read relationships file to map relationship IDs to actual file paths
        with zipfile.ZipFile(file_name, mode="r") as archive:
            try:
                rels_content = archive.read("word/_rels/document.xml.rels")
                rels_root = ET.fromstring(rels_content)

                # Namespace for relationships
                ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}

                for rel in rels_root.findall("r:Relationship", ns):
                    rel_id = rel.get("Id")
                    target = rel.get("Target")

                    if rel_id in rid_to_caption and target and target.startswith("media/"):
                        # Extract just the filename from the target path
                        image_filename = os.path.basename(target)
                        caption = rid_to_caption[rel_id]
                        caption_mapping[image_filename] = caption
                        logger.debug("Mapped %s to caption: %s", image_filename, caption[:50])

            except KeyError:
                logger.debug("No relationships file found in DOCX")

    except Exception as e:
        logger.warning("Unable to extract figure captions: %s", e)

    logger.info("Found %d figure captions for images", len(caption_mapping))
    return caption_mapping


def sanitize_filename(caption: str, original_ext: str) -> Optional[str]:
    """
    Convert a figure caption to a safe filename.

    :param str caption: The figure caption text.
    :param str original_ext: The original file extension.
    :return: A sanitized filename, or None if the caption cannot be converted.
    :rtype: Optional[str]
    """
    # Remove "Figure X-X" prefix pattern and clean up
    cleaned = re.sub(r"^Figure\s+[\d\-\.]+[:\s]*", "", caption, flags=re.IGNORECASE)
    # Remove special characters, keep alphanumeric, spaces, and hyphens
    cleaned = re.sub(r"[^\w\s\-]", "", cleaned)
    # Replace multiple spaces/underscores with single underscore
    cleaned = re.sub(r"[\s_]+", "_", cleaned.strip())
    # Truncate to reasonable length
    cleaned = cleaned[:80]
    # Ensure we have a valid filename
    if not cleaned:
        return None
    return f"{cleaned}{original_ext}"


def extract_and_upload_images(file_name: str, parent_id: int) -> None:
    """
    Extracts embedded images from a document and uploads them to RegScale with improved filenames.

    :param str file_name: The path to the document file.
    :param int parent_id: The parent ID in RegScale to associate the images with.

    """
    logger.debug(f"Processing embedded images in {file_name} for parent ID {parent_id}...")
    existing_files = fetch_existing_files(parent_id)

    # Get figure caption mappings for better filenames
    caption_mapping = get_image_caption_mapping(file_name)

    extracted_files_path = extract_embedded_files(file_name)
    upload_files(extracted_files_path, existing_files, parent_id, caption_mapping)


def fetch_existing_files(parent_id: int) -> list:
    """
    Fetches existing files for a given parent ID from RegScale.

    :param int parent_id: The parent ID whose files to fetch.
    :return: A list of existing files.
    :rtype: list
    """
    return File.get_files_for_parent_from_regscale(parent_id=parent_id, parent_module="securityplans")


def extract_embedded_files(file_name: str) -> str:
    """
    Extracts embedded files from a document and returns the path where they are stored.

    :param str file_name: The path to the document file.
    :return: The path where embedded files are extracted to.
    :rtype: str
    """
    # Minimum file size for diagrams (50KB) - lowered from 200KB to capture more diagrams
    min_file_size = 50000
    file_dump_path = os.path.join(gettempdir(), "imagedump")
    logger.info(f"Extracting embedded images from {file_name}")
    extracted_count = 0
    with zipfile.ZipFile(file_name, mode="r") as archive:
        for file in archive.filelist:
            if file.filename.startswith("word/media/") and file.file_size > min_file_size:
                logger.debug(f"Extracting file: {file.filename} ({file.file_size} bytes)")
                archive.extract(file, path=file_dump_path)
                extracted_count += 1
    logger.info(f"Extracted {extracted_count} images from document")
    return file_dump_path


def _get_file_display_name(filename: str, caption_mapping: Dict[str, str]) -> Tuple[str, bool]:
    """
    Get the display name for a file, optionally using caption mapping.

    :param str filename: The original filename.
    :param Dict[str, str] caption_mapping: Mapping of filenames to captions.
    :return: Tuple of (display_name, was_renamed).
    :rtype: Tuple[str, bool]
    """
    if filename not in caption_mapping:
        return filename, False

    original_ext = os.path.splitext(filename)[1]
    new_name = sanitize_filename(caption_mapping[filename], original_ext)
    if new_name:
        logger.debug("Renaming %s to %s based on figure caption", filename, new_name)
        return new_name, True
    return filename, False


def upload_files(
    extracted_files_path: str,
    existing_files: list,
    parent_id: int,
    caption_mapping: Optional[Dict[str, str]] = None,
) -> None:
    """
    Uploads files from a specified path to RegScale, avoiding duplicates.

    :param str extracted_files_path: The path where files are stored.
    :param list existing_files: A list of files already existing in RegScale to avoid duplicates.
    :param int parent_id: The parent ID in RegScale to associate the uploaded files with.
    :param Optional[Dict[str, str]] caption_mapping: Optional mapping of original filenames to captions.

    """
    media_path = os.path.join(extracted_files_path, "word", "media")
    if not os.path.exists(media_path):
        os.makedirs(media_path)

    caption_mapping = caption_mapping or {}
    uploaded_count = 0
    skipped_count = 0
    renamed_count = 0

    for filename in os.listdir(media_path):
        full_file_path = os.path.join(media_path, filename)
        if not os.path.isfile(full_file_path):
            continue

        display_name, was_renamed = _get_file_display_name(filename, caption_mapping)
        if was_renamed:
            renamed_count += 1

        if file_already_exists(display_name, existing_files) or file_already_exists(filename, existing_files):
            skipped_count += 1
            logger.debug("Skipping duplicate image: %s", display_name)
            continue

        logger.info("Uploading embedded image to RegScale: %s", display_name)
        try:
            upload_file_to_regscale(full_file_path, parent_id, display_name)
            uploaded_count += 1
        except Exception as e:
            logger.warning("Unable to upload image %s: %s", display_name, e)

    logger.info(
        "Successfully uploaded %d embedded images to RegScale (%d renamed, %d duplicates skipped)",
        uploaded_count,
        renamed_count,
        skipped_count,
    )


def file_already_exists(filename: str, existing_files: list) -> bool:
    """
    Checks if a file already exists in RegScale.

    :param str filename: The name of the file to check.
    :param list existing_files: A list of files already existing in RegScale.
    :return: True if the file exists, False otherwise.
    :rtype: bool
    """
    return any(f.trustedDisplayName == filename for f in existing_files)


def upload_file_to_regscale(
    file_path: str,
    parent_id: int,
    display_name: Optional[str] = None,
) -> None:
    """
    Uploads a single file to RegScale.

    :param str file_path: The full path to the file to upload.
    :param int parent_id: The parent ID in RegScale to associate the file with.
    :param Optional[str] display_name: Optional display name for the file. If provided,
        the file will be copied with this name before upload.
    """
    import shutil

    api = Api()
    upload_path = file_path

    # If a display name is provided, copy the file with the new name
    if display_name and display_name != os.path.basename(file_path):
        temp_dir = os.path.join(gettempdir(), "regscale_upload")
        os.makedirs(temp_dir, exist_ok=True)
        upload_path = os.path.join(temp_dir, display_name)
        shutil.copy2(file_path, upload_path)

    try:
        File.upload_file_to_regscale(
            file_name=upload_path,
            parent_id=parent_id,
            parent_module=SecurityPlan.get_module_slug(),
            api=api,
        )
    finally:
        # Clean up the temp file if we created one
        if upload_path != file_path and os.path.exists(upload_path):
            os.remove(upload_path)


def safe_get_first_key(dictionary: dict) -> Optional[str]:
    """Safely get the first key of a dictionary.
    :param dict dictionary: The dictionary to get the first key from.
    :return: The first key of the dictionary, or None if the dictionary is empty.
    :rtype: Optional[str]
    """
    try:
        return next(iter(dictionary))
    except StopIteration:
        return None


def parse_version(version_str: str) -> float:
    """Parse version string to a float, safely.
    :param str version_str: The version string to parse.
    :return: The version number as a float, or 0 if the version string is not a valid number.
    :rtype: float
    """
    try:
        if not version_str:
            return 0
        return float(version_str)
    except ValueError:
        return 0


def get_max_version(entries: List[Dict]) -> Optional[str]:
    """Find the maximum version from a list of entries.
    :param List[Dict] entries: The list of entries to find the maximum version from.
    :return: The maximum version from the entries, or None if no valid versions are found.
    :rtype: Optional[str]
    """
    max_version = None
    for entry in entries:
        version_str = entry.get("Version", "")
        version_num = parse_version(version_str)
        if version_num is not None:
            max_version = max(max_version, version_str, key=parse_version)
    logger.debug(f"Version: {max_version}")
    return max_version


def process_objective(
    objective: ControlObjective,
    processed_objective_ids: set,
    existing_objectives_by_objective_id: Dict,
    control: SecurityControl,
    part_statement: Optional[str],
    status: Optional[str],
    origination: Optional[str] = None,
    imp_objectives: List[ImplementationObjective] = None,
):
    """
    Process a single control objective.

    :param ControlObjective objective: The objective to process.
    :param set processed_objective_ids: Set of already processed objective IDs.
    :param Dict existing_objectives_by_objective_id: Dictionary of existing objectives by ID.
    :param SecurityControl control: The security control.
    :param Optional[str] part_statement: The statement for this part, may be None.
    :param Optional[str] status: The implementation status for this objective.
    :param Optional[str] origination: The implementation origination for this objective.
    :param List[ImplementationObjective] imp_objectives: List to collect implementation objectives.
    :return: None
    """
    logger.debug(f"Processing objective: {objective.id} - {objective.name}")

    # Skip if already processed
    if objective.id in processed_objective_ids:
        logger.debug(f"Objective {objective.id} already processed")
        return

    processed_objective_ids.add(objective.id)
    existing_objective = existing_objectives_by_objective_id.get(objective.id)

    statement = _format_part_statement(part_statement) if part_statement is not None else ""

    # Update existing objective if found
    if existing_objective is not None:
        logger.debug(f"Updating existing objective: {existing_objective.id}")
        existing_objective.status = status
        existing_objective.statement = statement
        if origination is not None:
            existing_objective.responsibility = origination
        existing_objective.save()
    # Create new objective if implementation objectives list provided
    elif imp_objectives is not None:
        logger.debug(f"Creating new objective for {objective.id}")
        imp_obj = ImplementationObjective(
            objectiveId=objective.id,
            status=status,
            statement=statement,
            responsibility=origination,
        )
        imp_objectives.append(imp_obj)
