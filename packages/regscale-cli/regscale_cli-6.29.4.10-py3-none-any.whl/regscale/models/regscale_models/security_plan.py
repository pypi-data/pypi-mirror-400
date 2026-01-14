#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Security Plan in the application"""

from typing import Optional, Union

from pydantic import ConfigDict, Field, field_validator

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class SecurityPlan(RegScaleModel):
    """
    Security Plan model
    """

    _module_slug = "securityplans"
    _plural_name = "securityPlans"
    _unique_fields = ["systemName", "tenantsId"]

    id: int = 0
    uuid: str = ""
    systemName: str
    systemType: str = "Major Application"
    defaultAssessmentDays: int = 0
    planInformationSystemSecurityOfficerId: Optional[str] = None
    planAuthorizingOfficialId: Optional[str] = None
    systemSecurityManagerId: Optional[str] = None
    systemOwnerId: Optional[str] = None  # this could be userID
    otherIdentifier: Optional[str] = ""
    trackingId: Optional[str] = ""
    networkEnvironment: Optional[str] = ""
    confidentiality: str = ""
    integrity: str = ""
    availability: str = ""
    status: Optional[str] = "Operational"
    description: Optional[str] = ""
    dateSubmitted: Optional[str] = ""
    approvalDate: Optional[str] = ""
    expirationDate: Optional[str] = ""
    purpose: Optional[str] = ""
    systemUrl: Optional[str] = ""
    conditionsOfApproval: Optional[str] = ""
    environment: Optional[str] = ""
    lawsAndRegulations: Optional[str] = ""
    authorizationBoundary: Optional[str] = ""
    authorizationTerminationDate: Optional[str] = ""
    networkArchitecture: Optional[str] = ""
    dataFlow: Optional[str] = ""
    overallCategorization: Optional[str] = ""
    maturityTier: Optional[str] = ""
    wizProjectId: Optional[str] = ""
    serviceNowAssignmentGroup: Optional[str] = ""
    jiraProject: Optional[str] = ""
    tenableGroup: Optional[str] = ""
    facilityId: Optional[int] = None
    orgId: Optional[int] = None
    parentId: int = 0
    parentModule: str = ""
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    users: int = 0
    privilegedUsers: int = 0
    usersMFA: int = 0
    privilegedUsersMFA: int = 0
    hva: bool = False
    practiceLevel: Optional[str] = ""
    processLevel: Optional[str] = ""
    cmmcLevel: Optional[str] = ""
    cmmcStatus: Optional[str] = ""
    isPublic: bool = True
    executiveSummary: Optional[str] = ""
    recommendations: Optional[str] = ""
    bDeployGov: bool = False
    bDeployHybrid: bool = False
    bDeployPrivate: bool = False
    bDeployPublic: bool = False
    bDeployOther: bool = False
    deployOtherRemarks: Optional[str] = ""
    bModelIaaS: bool = False
    bModelOther: bool = False
    bModelPaaS: bool = False
    bModelSaaS: bool = False
    otherModelRemarks: Optional[str] = ""
    explanationForNonOperational: Optional[str] = ""
    version: Optional[str] = ""
    categorizationJustification: Optional[str] = ""
    internalUsers: int = 0
    externalUsers: int = 0
    externalUsersFuture: int = 0
    internalUsersFuture: int = 0
    prepOrgName: Optional[str] = ""
    prepAddress: Optional[str] = ""
    prepOffice: Optional[str] = ""
    prepCityState: Optional[str] = ""
    cspOrgName: Optional[str] = ""
    cspAddress: Optional[str] = ""
    cspOffice: Optional[str] = ""
    cspCityState: Optional[str] = ""
    authenticationLevel: Optional[str] = ""
    identityAssuranceLevel: Optional[str] = ""
    authenticatorAssuranceLevel: Optional[str] = ""
    federationAssuranceLevel: Optional[str] = ""
    fedrampAuthorizationType: Optional[str] = ""
    fedrampAuthorizationLevel: Optional[str] = ""
    fedrampAuthorizationStatus: Optional[str] = ""
    fedrampDateSubmitted: Optional[str] = ""
    fedrampDateAuthorized: Optional[str] = ""
    fedrampId: Optional[str] = ""
    ditprId: Optional[str] = ""
    emassId: Optional[str] = ""
    complianceSettings: Optional[str] = None
    complianceSettingsId: Optional[int] = 1
    tenantsId: int = 1

    @field_validator("complianceSettingsId")
    def validate_regscale_version_and_compliance_settings(cls, v: int) -> Optional[int]:
        """
        Validate the RegScale version and if it is compatible with ComplianceSettings ID, has to be >=6.13

        :param int v: ComplianceSettings ID
        :return: The ComplianceSettings ID if the RegScale version is compatible, None otherwise
        :rtype: Optional[int]
        """
        from regscale.utils.version import RegscaleVersion

        regscale_version = cls._get_api_handler().regscale_version

        if len(regscale_version) >= 10 or RegscaleVersion.compare_versions(regscale_version, "6.13.0.0"):
            return v
        else:
            return None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the SecurityPlan model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_control_implementations="/api/controlImplementation/getAllByPlan/{plan_id}",
            mega_api="/api/{module_slug}/megaAPI/{intId}",
            export_cis_crm="/api/{module_slug}/exportFedrampRev5CisCrm/{intId}",
            list="/api/{module_slug}/getList",
        )

    @classmethod
    def fetch_mega_api_data(cls, ssp_id: int) -> dict:
        """
        Fetch the Mega API data for the given SSP ID

        :param int ssp_id: RegScale SSP ID
        :return: Mega API data
        :rtype: dict
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("mega_api").format(module_slug=cls._module_slug, intId=ssp_id)
        )
        if not response.raise_for_status():
            return response.json()
        return {}

    @classmethod
    def export_cis_crm(cls, ssp_id: int, max_retries: int = 2, retry_delay: float = 2.0) -> dict:
        """
        Export to a new CIS/CRM workbook with an existing SSP ID.

        Handles async 202 responses by polling until the operation completes.
        Uses httpx for cleaner HTTP handling with configurable timeouts.

        :param int ssp_id: RegScale SSP ID
        :param int max_retries: Maximum number of polling attempts for async operations
        :param float retry_delay: Seconds to wait between polling attempts
        :return: A status message with 'status' key, or error details
        :rtype: dict
        """
        import time

        import httpx

        logger = create_logger()
        app_config = cls._get_api_handler().config
        base_url = app_config.get("domain", "")
        token = app_config.get("token", "")
        ssl_verify = app_config.get("sslVerify", True)

        endpoint = cls.get_endpoint("export_cis_crm").format(module_slug=cls._module_slug, intId=ssp_id)
        full_url = f"{base_url}{endpoint}"

        logger.debug("CIS/CRM Export - Calling endpoint: %s", full_url)

        headers = {"Authorization": token}

        with httpx.Client(verify=ssl_verify, timeout=60.0) as client:
            response = client.get(full_url, headers=headers)

            # Handle 202 Accepted (async operation) - poll until complete
            if response.status_code == 202:
                logger.info("CIS/CRM export initiated (async). Polling for completion...")
                for attempt in range(max_retries):
                    time.sleep(retry_delay)
                    response = client.get(full_url, headers=headers)
                    logger.debug("Polling attempt %d/%d - status: %d", attempt + 1, max_retries, response.status_code)

                    if response.status_code != 202:
                        break  # Operation completed or failed
                else:
                    # Exhausted retries, still getting 202
                    logger.warning(
                        "CIS/CRM export still processing after %d attempts (~%ds)",
                        max_retries,
                        int(max_retries * retry_delay),
                    )
                    return {"error": "Export operation timed out - still processing"}

            if response.is_success:
                try:
                    return response.json()
                except (ValueError, httpx.DecodingError):
                    # Response may be empty or not JSON
                    logger.debug("CIS/CRM export returned non-JSON response (status %s)", response.status_code)
                    return {"error": "Empty or non-JSON response from API"}

            # Log the error for debugging
            logger.debug(
                "CIS/CRM export failed: status=%s, response=%s",
                response.status_code,
                response.text[:200] if response.text else "empty",
            )
            return {"error": f"API returned status {response.status_code}"}

    @classmethod
    def get_ssp_list(cls) -> list:
        """
        Get a list of objects.

        :return: A list of objects
        :rtype: list
        """
        response = cls._get_api_handler().get(endpoint=cls.get_endpoint("list").format(module_slug=cls._module_slug))
        if not response.raise_for_status():
            return response.json()
        return []

    # Legacy code
    def create_new_ssp(self, api: Api, return_id: Optional[bool] = False) -> Union[int, None, "SecurityPlan"]:
        """
        Create a new SSP in RegScale

        :param Api api: The API object to use to create the SSP in RegScale
        :param Optional[bool] return_id: Return the SSP ID only
        :return: The SSP or the SSP ID upon success, None otherwise.
        :rtype: Union[int, None, SecurityPlan]
        """
        # create the ssp in RegScale
        data = self.dict()
        ssp_response = api.post(
            f'{api.config["domain"]}/api/securityplans',
            json=data,
        )
        if ssp_response.ok:
            if return_id:
                return ssp_response.json()["id"]
            return SecurityPlan(**ssp_response.json())
        logger = create_logger()
        logger.error(f"Failed to upload SSP: {ssp_response.status_code} - {ssp_response.text}")
        return None

    def update_ssp(self, api: Api, return_id: Optional[bool] = False) -> Union[int, None, "SecurityPlan"]:
        """
        Update an SSP in RegScale

        :param Api api: The API object to use to create the SSP in RegScale
        :param Optional[bool] return_id: Return the SSP ID only
        :return: The SSP or the SSP ID upon success, None otherwise.
        :rtype: Union[int, None, SecurityPlan]
        """
        # create the ssp in RegScale
        data = self.dict()
        assert self.id is not None or self.id != 0
        ssp_response = api.put(
            f'{api.config["domain"]}/api/securityplans/{self.id}',
            json=data,
        )
        if ssp_response.ok:
            if return_id:
                return ssp_response.json()["id"]
            return SecurityPlan(**ssp_response.json())
        logger = create_logger()
        logger.error(f"Failed to update SSP: {ssp_response.status_code} - {ssp_response.text}")
        return None
