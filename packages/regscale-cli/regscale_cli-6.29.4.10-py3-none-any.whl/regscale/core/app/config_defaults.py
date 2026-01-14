#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Default configuration values for the RegScale CLI.

This module contains the default configuration template and placeholder constants
used throughout the application. The template defines all supported configuration
keys and their default values.

Usage:
    from regscale.core.app.config_defaults import get_default_template, DEFAULT_CONFIG_TEMPLATE

    # Get a fresh copy of the template (recommended for modification)
    template = get_default_template()

    # Or access the frozen template directly (read-only)
    from regscale.core.app.config_defaults import DEFAULT_CONFIG_TEMPLATE
"""

import copy
import os
from types import MappingProxyType
from typing import Any, Dict

# =============================================================================
# Placeholder Constants
# =============================================================================
# These placeholders indicate values that need to be configured by the user
# or are populated programmatically at runtime.

DEFAULT_CLIENT = "<myClientIdGoesHere>"
DEFAULT_SECRET = "<mySecretGoesHere>"
DEFAULT_POPULATED = "<createdProgrammatically>"
DEFAULT_TENANT = "<myTenantIdGoesHere>"

# =============================================================================
# Issue Due Date Configurations by Integration
# =============================================================================
# These define the default number of days until an issue is due based on severity.
# Status indicates the default issue status when created.
# minimumSeverity filters which severities to process.
# useKev indicates whether to use CISA KEV dates to override due dates.

ISSUE_DEFAULTS_AQUA = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_AWS = MappingProxyType(
    {
        "high": 30,
        "low": 365,
        "moderate": 90,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_AXONIUS = MappingProxyType(
    {
        "critical": 15,
        "high": 30,
        "moderate": 90,
        "low": 180,
    }
)

ISSUE_DEFAULTS_DEFENDER365 = MappingProxyType(
    {
        "high": 30,
        "low": 365,
        "moderate": 90,
        "status": "Open",
    }
)

ISSUE_DEFAULTS_DEFENDER_CLOUD = MappingProxyType(
    {
        "high": 30,
        "low": 365,
        "moderate": 90,
        "status": "Open",
    }
)

ISSUE_DEFAULTS_DEFENDER_FILE = MappingProxyType(
    {
        "high": 30,
        "low": 365,
        "moderate": 90,
        "status": "Open",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_ECR = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_JIRA = MappingProxyType(
    {
        "highest": 7,
        "high": 30,
        "medium": 90,
        "low": 180,
        "lowest": 365,
        "status": "Open",
    }
)

ISSUE_DEFAULTS_QUALYS = MappingProxyType(
    {
        "high": 30,
        "moderate": 90,
        "low": 365,
        "status": "Open",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_SALESFORCE = MappingProxyType(
    {
        "critical": 7,
        "high": 30,
        "medium": 90,
        "low": 365,
        "status": "Open",
    }
)

ISSUE_DEFAULTS_SNYK = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_SONARCLOUD = MappingProxyType(
    {
        "blocker": 7,
        "critical": 30,
        "major": 90,
        "minor": 365,
        "status": "Open",
    }
)

ISSUE_DEFAULTS_NEXPOSE = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_PRISMA = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_TANIUM_CLOUD = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
    }
)

ISSUE_DEFAULTS_TENABLE = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "useKev": False,
    }
)

ISSUE_DEFAULTS_WIZ = MappingProxyType(
    {
        "critical": 30,
        "high": 90,
        "low": 365,
        "medium": 90,
        "status": "Open",
        "minimumSeverity": "low",
    }
)

ISSUE_DEFAULTS_XRAY = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": True,
    }
)

ISSUE_DEFAULTS_VERACODE = MappingProxyType(
    {
        "critical": 30,
        "high": 30,
        "moderate": 90,
        "low": 180,
        "status": "Open",
        "minimumSeverity": "low",
        "useKev": False,
    }
)

# Combined issue defaults for all integrations
ISSUE_DEFAULTS_ALL = MappingProxyType(
    {
        "aqua": dict(ISSUE_DEFAULTS_AQUA),
        "aws": dict(ISSUE_DEFAULTS_AWS),
        "axonius": dict(ISSUE_DEFAULTS_AXONIUS),
        "defender365": dict(ISSUE_DEFAULTS_DEFENDER365),
        "defenderCloud": dict(ISSUE_DEFAULTS_DEFENDER_CLOUD),
        "defenderFile": dict(ISSUE_DEFAULTS_DEFENDER_FILE),
        "ecr": dict(ISSUE_DEFAULTS_ECR),
        "jira": dict(ISSUE_DEFAULTS_JIRA),
        "qualys": dict(ISSUE_DEFAULTS_QUALYS),
        "salesforce": dict(ISSUE_DEFAULTS_SALESFORCE),
        "snyk": dict(ISSUE_DEFAULTS_SNYK),
        "sonarcloud": dict(ISSUE_DEFAULTS_SONARCLOUD),
        "nexpose": dict(ISSUE_DEFAULTS_NEXPOSE),
        "prisma": dict(ISSUE_DEFAULTS_PRISMA),
        "tanium_cloud": dict(ISSUE_DEFAULTS_TANIUM_CLOUD),
        "tenable": dict(ISSUE_DEFAULTS_TENABLE),
        "wiz": dict(ISSUE_DEFAULTS_WIZ),
        "xray": dict(ISSUE_DEFAULTS_XRAY),
        "veracode": dict(ISSUE_DEFAULTS_VERACODE),
    }
)

# =============================================================================
# Finding Field Mapping Defaults
# =============================================================================
FINDING_FROM_MAPPING_DEFAULTS = MappingProxyType(
    {
        "aqua": MappingProxyType(
            {
                "remediation": "default",
                "title": "default",
                "description": "default",
            }
        ),
        "tenable_sc": MappingProxyType(
            {
                "remediation": "default",
                "title": "default",
                "description": "default",
            }
        ),
    }
)

# =============================================================================
# CSAM Configuration Defaults
# =============================================================================
# These define the default CSAM integration configuration values.
# Users should replace placeholder values with their actual CSAM settings.

CSAM_FILTER_DEFAULTS = MappingProxyType(
    {
        "Id": "<csamSystemIdGoesHere>",
    }
)

CSAM_AGENCY_DEFINED_DEFAULTS = MappingProxyType(
    {
        "AI-ML": "<AI-MLMappingGoesHere>",
    }
)

CSAM_FRAMEWORK_CATALOG_DEFAULTS = MappingProxyType(
    {
        "800-53R5": "<frameworkCatalogIdGoesHere>",
    }
)

# =============================================================================
# Default Configuration Template
# =============================================================================
# This is the master configuration template containing all supported keys
# and their default values. Use get_default_template() to get a mutable copy.


def _build_config_template() -> Dict[str, Any]:
    """
    Build the default configuration template.

    This function constructs the template dynamically to handle
    any runtime-dependent values (like paths).

    :return: Default configuration template dictionary
    :rtype: Dict[str, Any]
    """
    # Handle the wizStigMapperFile path - create artifacts dir if needed
    artifacts_dir = os.path.join(os.getcwd(), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    wiz_stig_mapper_file = os.path.join(artifacts_dir, "stig_mapper_rules.json")

    return {
        # STIG Configuration
        "stigBatchSize": 100,
        # Azure AD Configuration
        "adAccessToken": DEFAULT_POPULATED,
        "adAuthUrl": "https://login.microsoftonline.com/",
        "adClientId": DEFAULT_CLIENT,
        "adClientSecret": DEFAULT_SECRET,
        "adGraphUrl": "https://graph.microsoft.com/.default",
        "adTenantId": DEFAULT_TENANT,
        # Assessment Configuration
        "assessmentDays": 10,
        # Axonius Configuration
        "axoniusAccessToken": DEFAULT_POPULATED,
        "axoniusSecretToken": DEFAULT_SECRET,
        "axoniusUrl": "<myAxoniusURLgoeshere>",
        # Azure 365 Configuration
        "azure365AccessToken": DEFAULT_POPULATED,
        "azure365ClientId": DEFAULT_CLIENT,
        "azure365Secret": DEFAULT_SECRET,
        "azure365TenantId": DEFAULT_TENANT,
        # Azure Cloud Configuration
        "azureCloudAccessToken": DEFAULT_POPULATED,
        "azureCloudClientId": DEFAULT_CLIENT,
        "azureCloudSecret": DEFAULT_SECRET,
        "azureCloudTenantId": DEFAULT_TENANT,
        "azureCloudSubscriptionId": "<mySubscriptionIdGoesHere>",
        # Azure Entra Configuration
        "azureEntraAccessToken": DEFAULT_POPULATED,
        "azureEntraClientId": DEFAULT_CLIENT,
        "azureEntraSecret": DEFAULT_SECRET,
        "azureEntraTenantId": DEFAULT_TENANT,
        # CISA KEV Configuration
        "cisaKev": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        # Compliance Configuration
        "complianceCreation": "Assessment",
        # CrowdStrike Configuration
        "crowdstrikeClientId": DEFAULT_CLIENT,
        "crowdstrikeClientSecret": DEFAULT_SECRET,
        "crowdstrikeBaseUrl": "<crowdstrikeApiUrl>",
        # CSAM Configuration
        "csamToken": DEFAULT_SECRET,
        "csamURL": "<myCSAMURLgoeshere>",
        "csamFilter": dict(CSAM_FILTER_DEFAULTS),
        "csamAgencyDefinedDataItems": dict(CSAM_AGENCY_DEFINED_DEFAULTS),
        "csamFrameworkCatalog": dict(CSAM_FRAMEWORK_CATALOG_DEFAULTS),
        # Dependabot Configuration
        "dependabotId": "<myGithubUserIdGoesHere>",
        "dependabotOwner": "<myGithubRepoOwnerGoesHere>",
        "dependabotRepo": "<myGithubRepoNameGoesHere>",
        "dependabotToken": "<myGithubPersonalAccessTokenGoesHere>",
        # RegScale Domain Configuration
        "domain": "https://regscale.yourcompany.com/",
        "disableCache": False,
        # Evidence Configuration
        "evidenceFolder": "./evidence",
        # Scoring Configuration
        "passScore": 80,
        "failScore": 30,
        # GCP Configuration
        "gcpCredentials": "<path/to/credentials.json>",
        "gcpOrganizationId": "<000000000000>",
        "gcpProjectId": "<000000000000>",
        "gcpScanType": "<organization | project>",
        # GitHub Configuration
        "githubDomain": "api.github.com",
        # Issue Creation Configuration
        "issueCreation": "Consolidated",
        "issues": {
            "aqua": dict(ISSUE_DEFAULTS_AQUA),
            "aws": dict(ISSUE_DEFAULTS_AWS),
            "axonius": dict(ISSUE_DEFAULTS_AXONIUS),
            "defender365": dict(ISSUE_DEFAULTS_DEFENDER365),
            "defenderCloud": dict(ISSUE_DEFAULTS_DEFENDER_CLOUD),
            "defenderFile": dict(ISSUE_DEFAULTS_DEFENDER_FILE),
            "ecr": dict(ISSUE_DEFAULTS_ECR),
            "jira": dict(ISSUE_DEFAULTS_JIRA),
            "qualys": dict(ISSUE_DEFAULTS_QUALYS),
            "salesforce": dict(ISSUE_DEFAULTS_SALESFORCE),
            "snyk": dict(ISSUE_DEFAULTS_SNYK),
            "sonarcloud": dict(ISSUE_DEFAULTS_SONARCLOUD),
            "nexpose": dict(ISSUE_DEFAULTS_NEXPOSE),
            "prisma": dict(ISSUE_DEFAULTS_PRISMA),
            "tanium_cloud": dict(ISSUE_DEFAULTS_TANIUM_CLOUD),
            "tenable": dict(ISSUE_DEFAULTS_TENABLE),
            "wiz": dict(ISSUE_DEFAULTS_WIZ),
            "xray": dict(ISSUE_DEFAULTS_XRAY),
            "veracode": dict(ISSUE_DEFAULTS_VERACODE),
        },
        # AWS Integration Configuration
        "aws": {
            "inventory": {
                "enabled_services": {
                    "compute": {
                        "enabled": True,
                        "services": {
                            "ec2": True,
                            "ecs": True,
                            "lambda": True,
                            "systems_manager": True,
                        },
                    },
                    "config": {
                        "enabled": True,
                        "services": {},
                    },
                    "containers": {
                        "enabled": True,
                        "services": {
                            "ecr": True,
                        },
                    },
                    "database": {
                        "enabled": True,
                        "services": {
                            "dynamodb": True,
                            "rds": True,
                        },
                    },
                    "integration": {
                        "enabled": True,
                        "services": {
                            "api_gateway": True,
                            "eventbridge": True,
                            "sns": True,
                            "sqs": True,
                        },
                    },
                    "networking": {
                        "enabled": True,
                        "services": {
                            "cloudfront": True,
                            "elastic_ips": True,
                            "load_balancers": True,
                            "route53": True,
                            "vpc": True,
                        },
                    },
                    "security": {
                        "enabled": True,
                        "services": {
                            "acm": True,
                            "audit_manager": True,
                            "cloudtrail": True,
                            "config": True,
                            "guardduty": True,
                            "iam": True,
                            "inspector": True,
                            "kms": True,
                            "secrets_manager": True,
                            "securityhub": True,
                            "waf": True,
                        },
                    },
                    "storage": {
                        "enabled": True,
                        "services": {
                            "ebs": True,
                            "s3": True,
                        },
                    },
                },
            },
        },
        # Jira Configuration
        "jiraApiToken": "<jiraAPIToken>",
        "jiraUrl": "<myJiraUrl>",
        "jiraUserName": "<jiraUserName>",
        # Threading Configuration
        "maxThreads": 1000,
        # NIST Configuration
        "nistCpeApiKey": "<myNistCpeApiKey>",
        # Okta Configuration
        "oktaApiToken": "Can be a SSWS token from Okta or created programmatically",
        "oktaClientId": "<oktaClientIdGoesHere>",
        "oktaUrl": "<oktaUrlGoesHere>",
        # OSCAL Configuration
        "oscalLocation": "/opt/OSCAL",
        # POAM Configuration
        "poamTitleType": "Cve",
        # PowerShell Configuration
        "pwshPath": "/opt/microsoft/powershell/7/pwsh",
        # Qualys Configuration
        "qualysUrl": "https://yourcompany.qualys.com/api/2.0/fo/scan/",
        "qualysUserName": "<qualysUserName>",
        "qualysPassword": "<qualysPassword>",
        # Sicura Configuration
        "sicuraUrl": "<mySicuraUrl>",
        "sicuraToken": "<mySicuraToken>",
        # Salesforce Configuration
        "salesforceUserName": "<salesforceUserName>",
        "salesforcePassword": "<salesforcePassword>",
        "salesforceToken": "<salesforceSecurityToken>",
        # ServiceNow Configuration
        "snowPassword": "<snowPassword>",
        "snowUrl": "<mySnowUrl>",
        "snowUserName": "<snowUserName>",
        # SonarCloud Configuration
        "sonarUrl": "https://sonarcloud.io",
        "sonarToken": "<mySonarToken>",
        # Tenable Configuration
        "tenableAccessKey": "<tenableAccessKeyGoesHere>",
        "tenableSecretKey": "<tenableSecretKeyGoesHere>",
        "tenableUrl": "https://sc.tenalab.online",
        "tenableMinimumSeverityFilter": "low",
        "tenableGroupByPlugin": False,
        # RegScale Authentication
        "token": DEFAULT_POPULATED,
        "userId": "enter RegScale user id here",
        # Feature Flags
        "useMilestones": False,
        "preventAutoClose": False,
        # AlienVault OTX Configuration
        "otx": "enter AlienVault API key here",
        # Vulnerability Configuration
        "vulnerabilityCreation": "PoamCreation",
        # Wiz Configuration
        "wizAccessToken": DEFAULT_POPULATED,
        "wizAuthUrl": "https://auth.wiz.io/oauth/token",
        "wizExcludes": "My things to exclude here",
        "wizScope": "<filled out programmatically after authenticating to Wiz>",
        "wizUrl": "<my Wiz URL goes here>",
        "wizReportAge": 15,
        "wizLastInventoryPull": "<wizLastInventoryPull>",
        "wizInventoryFilterBy": "<wizInventoryFilterBy>",
        "wizIssueFilterBy": "<wizIssueFilterBy>",
        "wizFullPullLimitHours": 8,
        "wizStigMapperFile": wiz_stig_mapper_file,
        # Timeout Configuration
        "timeout": 60,
        # Finding Mapping Configuration
        "findingFromMapping": {
            "aqua": {
                "remediation": "default",
                "title": "default",
                "description": "default",
            },
            "tenable_sc": {
                "remediation": "default",
                "title": "default",
                "description": "default",
            },
        },
    }


def get_default_template() -> Dict[str, Any]:
    """
    Get a fresh, mutable copy of the default configuration template.

    This function returns a deep copy of the template, safe for modification.
    Use this when you need to modify the template or merge it with user config.

    :return: A mutable copy of the default configuration template
    :rtype: Dict[str, Any]

    Example:
        >>> template = get_default_template()
        >>> template["maxThreads"] = 500  # Safe to modify
    """
    return copy.deepcopy(_build_config_template())


# Expose a frozen version of the template for read-only access
# Note: This is built once at module import time
DEFAULT_CONFIG_TEMPLATE = _build_config_template()
