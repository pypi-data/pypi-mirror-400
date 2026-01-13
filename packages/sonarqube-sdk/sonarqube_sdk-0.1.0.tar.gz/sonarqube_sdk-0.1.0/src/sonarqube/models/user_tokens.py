"""Pydantic models for User Tokens API.

This module provides models for the /api/user_tokens endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel


class UserToken(SonarQubeModel):
    """A user token.

    Attributes:
        name: Token name.
        created_at: Creation date.
        last_connection_date: Last connection date.
        type: Token type.
        expiration_date: Expiration date.
        is_expired: Whether the token is expired.
        project: Project key (for project tokens).
    """

    name: str = Field(description="Token name")
    created_at: Optional[str] = Field(
        default=None,
        alias="createdAt",
        description="Creation date",
    )
    last_connection_date: Optional[str] = Field(
        default=None,
        alias="lastConnectionDate",
        description="Last connection date",
    )
    type: Optional[str] = Field(default=None, description="Token type")
    expiration_date: Optional[str] = Field(
        default=None,
        alias="expirationDate",
        description="Expiration date",
    )
    is_expired: Optional[bool] = Field(
        default=None,
        alias="isExpired",
        description="Whether the token is expired",
    )
    project: Optional[dict[str, Any]] = Field(
        default=None,
        description="Project (for project tokens)",
    )


class UserTokenGenerateResponse(SonarQubeModel):
    """Response from generating a user token.

    Attributes:
        login: User login.
        name: Token name.
        token: The generated token value.
        created_at: Creation date.
        type: Token type.
        expiration_date: Expiration date.
    """

    login: str = Field(description="User login")
    name: str = Field(description="Token name")
    token: str = Field(description="Generated token value")
    created_at: Optional[str] = Field(
        default=None,
        alias="createdAt",
        description="Creation date",
    )
    type: Optional[str] = Field(default=None, description="Token type")
    expiration_date: Optional[str] = Field(
        default=None,
        alias="expirationDate",
        description="Expiration date",
    )


class UserTokenSearchResponse(SonarQubeModel):
    """Response from searching user tokens.

    Attributes:
        login: User login.
        user_tokens: List of tokens.
    """

    login: str = Field(description="User login")
    user_tokens: list[UserToken] = Field(
        default_factory=list,
        alias="userTokens",
        description="List of tokens",
    )
