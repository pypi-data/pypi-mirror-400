#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for a RegScale User"""

# standard python imports
import random
import string
from typing import List, Optional, Tuple, cast

from pydantic import ConfigDict, Field, field_validator

from regscale.core.app.utils.app_utils import get_current_datetime

from .regscale_model import RegScaleModel, T


def generate_password() -> str:
    """
    Generates a random string that is 12-20 characters long

    :return: random string 12-20 characters long
    :rtype: str
    """
    # select a random password length between 12-20 characters
    length = random.randint(12, 20)

    # get all possible strings to create a password
    all_string_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

    # randomly select characters matching the random length
    temp = random.sample(all_string_chars, length)
    # return a string from the temp list of samples
    return "".join(temp)


class User(RegScaleModel):
    """User Model"""

    model_config = ConfigDict(populate_by_name=True)
    _module_slug = "accounts"
    _unique_fields = [
        ["userName", "email"],
    ]
    _exclude_graphql_fields = ["extra_data", "tenantsId", "password"]

    userName: str = Field(alias="username")
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    tenantId: int = 1
    initials: Optional[str] = None
    id: Optional[str] = None
    password: str = Field(default_factory=generate_password)
    homePageUrl: Optional[str] = "/workbench"
    name: Optional[str] = None
    workPhone: Optional[str] = None
    mobilePhone: Optional[str] = None
    avatar: Optional[bytes] = None
    jobTitle: Optional[str] = None
    orgId: Optional[int] = None
    pictureURL: Optional[str] = None
    activated: bool = False
    emailNotifications: bool = True
    ldapUser: bool = False
    externalId: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastLogin: Optional[str] = None
    readOnly: bool = True
    roles: Optional[List[str]] = None

    @field_validator("homePageUrl")
    def validate_regscale_version_and_home_page_url(cls, v: str) -> Optional[str]:
        """
        Validate the RegScale version and if it is compatible with homePageUrl, has to be >=6.13

        :param str v: homePageUrl value
        :return: The homePageUrl if the RegScale version is compatible, None otherwise
        """
        from regscale.utils.version import RegscaleVersion

        rv = RegscaleVersion()
        if rv.meets_minimum_version("6.14.0.0"):
            return v
        else:
            return None

    @classmethod
    def _get_additional_endpoints(cls) -> ConfigDict:
        """
        Get additional endpoints for the Accounts model, using {model_slug} as a placeholder for the model slug.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all="/api/{model_slug}",
            create_account=cls._module_slug_url,
            update_account=cls._module_slug_url,
            get_accounts=cls._module_slug_url,
            register_questionnaire_user="/api/{model_slug}/registerQuestionnaireUser",
            cache_reset="/api/{model_slug}/cacheReset",
            create_ldap_accounts="/api/{model_slug}/ldap",
            create_azuread_accounts="/api/{model_slug}/azureAD",
            assign_role="/api/{model_slug}/assignRole",
            check_role="/api/{model_slug}/checkRole/{strUserId}/{strRoleId}",
            delete_role="/api/{model_slug}/deleteRole/{strUserId}/{strRoleId}",
            get_my_manager="/api/{model_slug}/getMyManager",
            get_manager_by_user_id="/api/{model_slug}/getManagerByUserId/{strUserId}",
            list="/api/{model_slug}/getList",
            get_inactive_users="/api/{model_slug}/getInactiveUsers",
            get_accounts_by_tenant="/api/{model_slug}/{tenantId}",
            get_accounts_by_email_flag="/api/{model_slug}/{intTenantId}/{bEmailFlag}",
            get_all_by_tenant="/api/{model_slug}/getAllByTenant/{intTenantId}",
            filter_users="/api/{model_slug}/filterUsers/{intTenant}/{strSearch}/{bActive}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            filter_user_roles="/api/{model_slug}/filterUserRoles/{intId}/{strRole}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
            change_user_status="/api/{model_slug}/changeUserStatus/{strId}/{bStatus}",
            get_user_by_username="/api/{model_slug}/getUserByUsername/{strUsername}",
            get="/api/{model_slug}/find/{id}",
            get_roles="/api/{model_slug}/getRoles",
            get_roles_by_user="/api/{model_slug}/getRolesByUser/{strUser}",
            is_delegate="/api/{model_slug}/isDelegate/{strUser}",
            get_delegates="/api/{model_slug}/getDelegates/{userId}",
            change_avatar="/api/{model_slug}/changeAvatar/{strUsername}",
        )

    @classmethod
    def get_roles(cls) -> List[dict]:
        """
        Get all roles from RegScale

        :return: List of RegScale roles
        :rtype: List[dict]
        """
        response = cls._get_api_handler().get(endpoint=cls.get_endpoint("get_roles"))
        if response and response.ok:
            return response.json()
        return []

    @classmethod
    def get_tenant_id_for_user_id(cls, user_id: str) -> Optional[int]:
        """
        Retrieve all users by tenant ID.

        Args:
            user_id: str : user id to find

        Returns:
            Optional[int]: optionals
        """
        user = cls.get_user_by_id(user_id)
        return user.tenantId if user else None

    @classmethod
    def get_user_by_id(cls, user_id: str) -> "User":
        """
        Get a user by their ID

        :param str user_id: The user's ID
        :return: The user object
        :rtype: User
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get").format(model_slug=cls._module_slug, id=user_id)
        )
        return cls._handle_response(response)

    @classmethod
    def get_all(cls) -> List["User"]:
        """
        Get all users from RegScale

        :return: List of RegScale users
        :rtype: List[User]
        """
        response = cls._get_api_handler().get(endpoint=cls.get_endpoint("get_all"))
        return cast(List[T], cls._handle_list_response(response))

    @classmethod
    def get_roles(cls) -> List["User"]:
        """
        Get all roles from RegScale

        :return: List of RegScale roles
        :rtype: dict
        """
        response = cls._get_api_handler().get(endpoint=cls.get_endpoint("get_roles"))
        return cast(List[T], cls._handle_list_response(response))

    def assign_role(self, role_id: str) -> bool:
        """
        Assign a role to a user

        :return: Whether the role was assigned
        :rtype: bool
        """
        response = self._get_api_handler().post(
            data={"roleId": role_id, "userId": self.id}, endpoint=self.get_endpoint("assign_role")
        )
        return response.ok

    @classmethod
    def get_list(cls) -> List[dict]:
        """
        Get a simple list of users

        :return: list of RegScale Users
        :rtype: List[dict]
        """

        response = cls._get_api_handler().get(endpoint=cls.get_endpoint("list"))
        if response and response.ok:
            return response.json()
        return []

    @classmethod
    def get_user_by_username(cls, username: str) -> Optional["User"]:
        """
        Get a user by their username.

        :param str username: The username to search for
        :return: The user object if found, None otherwise
        :rtype: Optional[User]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_user_by_username").format(model_slug=cls._module_slug, strUsername=username)
        )
        if response and response.ok:
            data = response.json()
            if data:
                return cls(**data)
        return None

    @staticmethod
    def _get_user_searchable_fields(user_data: dict) -> List[Tuple[str, str]]:
        """
        Extract searchable fields from user data as (field_name, value) tuples.

        :param dict user_data: User data dictionary
        :return: List of (field_name, lowercase_value) tuples for matching
        :rtype: List[Tuple[str, str]]
        """
        fields = []

        # Email
        email = (user_data.get("email") or "").lower()
        if email:
            fields.append(("email", email))

        # Username (check both camelCase and lowercase variants)
        username = (user_data.get("userName") or user_data.get("username") or "").lower()
        if username:
            fields.append(("username", username))

        # Name fields
        first_name = (user_data.get("firstName") or "").lower()
        last_name = (user_data.get("lastName") or "").lower()
        full_name = f"{first_name} {last_name}".strip()

        if full_name:
            fields.append(("full name", full_name))
        if first_name:
            fields.append(("first name", first_name))
        if last_name:
            fields.append(("last name", last_name))

        return fields

    @classmethod
    def search_by_name(cls, name: str, users: Optional[List[dict]] = None) -> Optional["User"]:
        """
        Search for a user by name (first name, last name, full name, or email).

        Performs case-insensitive matching against first name, last name,
        full name (first + last), and email.

        :param str name: The name or email to search for
        :param Optional[List[dict]] users: Optional pre-fetched list of users to search
        :return: The matching user if found, None otherwise
        :rtype: Optional[User]
        """
        import logging

        logger = logging.getLogger("regscale")

        if not name:
            return None

        name_lower = name.lower().strip()
        if not name_lower:
            return None

        # Get all users if not provided
        if users is None:
            users = cls.get_list()

        for user_data in users:
            searchable_fields = cls._get_user_searchable_fields(user_data)
            for field_name, field_value in searchable_fields:
                if field_value == name_lower:
                    logger.debug("Found user by %s: %s", field_name, field_value)
                    return cls.get_user_by_id(user_data.get("id"))

        return None

    @classmethod
    def _try_find_existing_user(cls, name: str, email: Optional[str], users: Optional[List[dict]]) -> Optional["User"]:
        """
        Try to find an existing user by name or email.

        :param str name: The name to search for
        :param Optional[str] email: Email to search for as fallback
        :param Optional[List[dict]] users: Optional pre-fetched list of users
        :return: The found user or None
        :rtype: Optional[User]
        """
        import logging

        logger = logging.getLogger("regscale")

        # Try to find by name first
        existing_user = cls.search_by_name(name, users)
        if existing_user:
            logger.info("Found existing user: %s (ID: %s)", name, existing_user.id)
            return existing_user

        # Try email as fallback
        if email:
            existing_user = cls.search_by_name(email, users)
            if existing_user:
                logger.info("Found existing user by email: %s (ID: %s)", email, existing_user.id)
                return existing_user

        return None

    @staticmethod
    def _prepare_user_data(name: str, email: Optional[str]) -> Tuple[str, str, str, str]:
        """
        Prepare user data for creation.

        :param str name: The user's name
        :param Optional[str] email: The user's email (or None to generate placeholder)
        :return: Tuple of (email, username, first_name, last_name)
        :rtype: Tuple[str, str, str, str]
        """
        import logging

        logger = logging.getLogger("regscale")

        # Generate placeholder email if needed
        if not email:
            sanitized_name = name.lower().replace(" ", ".").replace(",", "")
            email = f"{sanitized_name}@placeholder.regscale.com"
            logger.warning("No email provided for %s, using placeholder: %s", name, email)

        # Parse name into first/last
        name_parts = name.strip().split(" ", 1)
        first_name = name_parts[0] if name_parts else name
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Create username from email
        username = email.split("@")[0]

        return email, username, first_name, last_name

    @classmethod
    def find_or_create_user(
        cls,
        name: str,
        email: Optional[str] = None,
        job_title: Optional[str] = None,
        org_id: Optional[int] = None,
        users: Optional[List[dict]] = None,
    ) -> Optional["User"]:
        """
        Find an existing user by name/email or create a new general user.

        First searches for an existing user by name. If not found and email is provided,
        creates a new user account.

        :param str name: The name to search for / use as username
        :param Optional[str] email: Email address for new user creation
        :param Optional[str] job_title: Job title for new user
        :param Optional[int] org_id: Organization ID for new user
        :param Optional[List[dict]] users: Optional pre-fetched list of users
        :return: The found or created user, None if unable to create
        :rtype: Optional[User]
        """
        import logging

        logger = logging.getLogger("regscale")

        # Try to find existing user first
        existing_user = cls._try_find_existing_user(name, email, users)
        if existing_user:
            return existing_user

        # Prepare data for new user creation
        email, username, first_name, last_name = cls._prepare_user_data(name, email)

        # Create new user
        try:
            new_user = cls(
                userName=username,
                email=email,
                firstName=first_name,
                lastName=last_name,
                jobTitle=job_title or "",
                orgId=org_id,
                activated=True,
                readOnly=True,
            )
            created_user = new_user.create()
            if created_user and created_user.id:
                logger.info("Created new user: %s (ID: %s)", name, created_user.id)
                return created_user
        except Exception as e:
            logger.warning("Failed to create user %s: %s", name, e)

        return None
