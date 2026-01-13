"""Pydantic models for Users API.

This module provides models for the /api/users endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel
from sonarqube.models.common import Paging


class User(SonarQubeModel):
    """A SonarQube user.

    Attributes:
        login: User login.
        name: User display name.
        active: Whether the user is active.
        email: User email.
        local: Whether the user is local.
        external_identity: External identity provider.
        external_provider: External provider name.
        groups: User groups.
        tokens_count: Number of tokens.
        last_connection_date: Last connection date.
        sonar_lint_last_connection_date: SonarLint last connection date.
    """

    login: str = Field(description="User login")
    name: Optional[str] = Field(default=None, description="Display name")
    active: Optional[bool] = Field(default=None, description="Whether user is active")
    email: Optional[str] = Field(default=None, description="User email")
    local: Optional[bool] = Field(default=None, description="Whether user is local")
    external_identity: Optional[str] = Field(
        default=None,
        alias="externalIdentity",
        description="External identity",
    )
    external_provider: Optional[str] = Field(
        default=None,
        alias="externalProvider",
        description="External provider",
    )
    groups: Optional[list[str]] = Field(default=None, description="User groups")
    tokens_count: Optional[int] = Field(
        default=None,
        alias="tokensCount",
        description="Number of tokens",
    )
    last_connection_date: Optional[str] = Field(
        default=None,
        alias="lastConnectionDate",
        description="Last connection date",
    )
    sonar_lint_last_connection_date: Optional[str] = Field(
        default=None,
        alias="sonarLintLastConnectionDate",
        description="SonarLint last connection date",
    )
    avatar: Optional[str] = Field(default=None, description="Avatar hash")
    managed: Optional[bool] = Field(default=None, description="Whether user is managed")


class UserSearchResponse(SonarQubeModel):
    """Response from searching users.

    Attributes:
        paging: Paging information.
        users: List of users.
    """

    paging: Paging = Field(description="Paging information")
    users: list[User] = Field(default_factory=list, description="List of users")


class UserCreateResponse(SonarQubeModel):
    """Response from creating a user.

    Attributes:
        user: Created user.
    """

    user: User = Field(description="Created user")


class CurrentUserResponse(SonarQubeModel):
    """Response from getting current user.

    Attributes:
        login: User login.
        name: User display name.
        email: User email.
        local: Whether the user is local.
        groups: User groups.
        permissions: User permissions.
    """

    login: str = Field(description="User login")
    name: Optional[str] = Field(default=None, description="Display name")
    email: Optional[str] = Field(default=None, description="User email")
    local: Optional[bool] = Field(default=None, description="Whether user is local")
    groups: Optional[list[str]] = Field(default=None, description="User groups")
    permissions: Optional[dict[str, Any]] = Field(
        default=None, description="User permissions"
    )
    is_logged_in: Optional[bool] = Field(
        default=None,
        alias="isLoggedIn",
        description="Whether user is logged in",
    )


class UserGroupsResponse(SonarQubeModel):
    """Response from getting user groups.

    Attributes:
        paging: Paging information.
        groups: List of groups.
    """

    paging: Paging = Field(description="Paging information")
    groups: list[dict[str, Any]] = Field(
        default_factory=list, description="List of groups"
    )
