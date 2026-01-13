"""User Tokens API for SonarQube SDK.

This module provides methods to manage SonarQube user tokens.

Example:
    Using the User Tokens API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Generate a new token
        token = client.user_tokens.generate(name="my-token")
        print(f"Token: {token.token}")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.user_tokens import (
    UserTokenGenerateResponse,
    UserTokenSearchResponse,
)


class UserTokensAPI(BaseAPI):
    """API for managing SonarQube user tokens.

    Attributes:
        API_PATH: Base path for user tokens API ("/api/user_tokens").
    """

    API_PATH = "/api/user_tokens"

    def generate(
        self,
        name: str,
        login: Optional[str] = None,
        expiration_date: Optional[str] = None,
        project_key: Optional[str] = None,
        type_: Optional[str] = None,
    ) -> UserTokenGenerateResponse:
        """Generate a new user token.

        Args:
            name: Token name.
            login: User login (defaults to current user).
            expiration_date: Token expiration date (YYYY-MM-DD).
            project_key: Project key (for project tokens).
            type_: Token type (USER_TOKEN, GLOBAL_ANALYSIS_TOKEN, PROJECT_ANALYSIS_TOKEN).

        Returns:
            Response containing the generated token.

        Example:
            >>> token = client.user_tokens.generate(
            ...     name="ci-token", expiration_date="2025-12-31"
            ... )
            >>> print(f"Token: {token.token}")
        """
        data: dict[str, Any] = {"name": name}

        if login:
            data["login"] = login
        if expiration_date:
            data["expirationDate"] = expiration_date
        if project_key:
            data["projectKey"] = project_key
        if type_:
            data["type"] = type_

        return self._post_model("/generate", UserTokenGenerateResponse, data=data)

    def revoke(self, name: str, login: Optional[str] = None) -> None:
        """Revoke a user token.

        Args:
            name: Token name.
            login: User login (defaults to current user).

        Example:
            >>> client.user_tokens.revoke(name="old-token")
        """
        data: dict[str, Any] = {"name": name}
        if login:
            data["login"] = login

        self._post("/revoke", data=data)

    def search(self, login: Optional[str] = None) -> UserTokenSearchResponse:
        """List user tokens.

        Args:
            login: User login (defaults to current user).

        Returns:
            Response containing list of tokens.

        Example:
            >>> response = client.user_tokens.search()
            >>> for token in response.user_tokens:
            ...     print(token.name)
        """
        return self._get_model(
            "/search",
            UserTokenSearchResponse,
            params={"login": login},
        )
