"""Users API for SonarQube SDK.

This module provides methods to manage SonarQube users.

Example:
    Using the Users API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Search for users
        users = client.users.search(q="john")
        for user in users.users:
            print(f"{user.login}: {user.name}")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.users import (
    CurrentUserResponse,
    User,
    UserCreateResponse,
    UserGroupsResponse,
    UserSearchResponse,
)


class UsersAPI(BaseAPI):
    """API for managing SonarQube users.

    Attributes:
        API_PATH: Base path for users API ("/api/users").
    """

    API_PATH = "/api/users"

    def anonymize(self, login: str) -> None:
        """Anonymize a deactivated user.

        Requires 'Administer System' permission.

        Args:
            login: User login.

        Example:
            >>> client.users.anonymize(login="old-user")
        """
        self._post("/anonymize", data={"login": login})

    def create(
        self,
        login: str,
        name: str,
        email: Optional[str] = None,
        local: Optional[bool] = None,
        password: Optional[str] = None,
        scm_accounts: Optional[list[str]] = None,
    ) -> UserCreateResponse:
        """Create a new user.

        Requires 'Administer System' permission.

        Args:
            login: User login.
            name: User display name.
            email: User email.
            local: Whether the user is local.
            password: User password (required for local users).
            scm_accounts: SCM accounts.

        Returns:
            Response containing the created user.

        Example:
            >>> user = client.users.create(
            ...     login="jdoe", name="John Doe", email="jdoe@example.com", password="secret"
            ... )
        """
        data: dict[str, Any] = {
            "login": login,
            "name": name,
        }
        if email:
            data["email"] = email
        if local is not None:
            data["local"] = str(local).lower()
        if password:
            data["password"] = password
        if scm_accounts:
            data["scmAccount"] = scm_accounts

        return self._post_model("/create", UserCreateResponse, data=data)

    def current(self) -> CurrentUserResponse:
        """Get the current authenticated user.

        Returns:
            Response containing current user details.

        Example:
            >>> user = client.users.current()
            >>> print(f"Logged in as: {user.login}")
        """
        return self._get_model("/current", CurrentUserResponse)

    def deactivate(self, login: str, anonymize: Optional[bool] = None) -> User:
        """Deactivate a user.

        Requires 'Administer System' permission.

        Args:
            login: User login.
            anonymize: Whether to anonymize the user.

        Returns:
            The deactivated user.

        Example:
            >>> user = client.users.deactivate(login="old-user")
        """
        data: dict[str, Any] = {"login": login}
        if anonymize is not None:
            data["anonymize"] = str(anonymize).lower()

        response = self._post("/deactivate", data=data)
        return User.model_validate(response.get("user", response))

    def groups(
        self,
        login: str,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
        selected: Optional[str] = None,
    ) -> UserGroupsResponse:
        """Get groups for a user.

        Requires 'Administer System' permission.

        Args:
            login: User login.
            p: Page number.
            ps: Page size.
            q: Search query.
            selected: Filter selection.

        Returns:
            Response containing user groups.

        Example:
            >>> groups = client.users.groups(login="jdoe")
        """
        return self._get_model(
            "/groups",
            UserGroupsResponse,
            params={
                "login": login,
                "p": p,
                "ps": ps,
                "q": q,
                "selected": selected,
            },
        )

    def search(
        self,
        active: Optional[bool] = None,
        external_identity: Optional[str] = None,
        last_connected_after: Optional[str] = None,
        last_connected_before: Optional[str] = None,
        managed: Optional[bool] = None,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
        sonar_lint_last_connection_date_from: Optional[str] = None,
        sonar_lint_last_connection_date_to: Optional[str] = None,
    ) -> UserSearchResponse:
        """Search for users.

        Requires 'Administer System' permission.

        Args:
            active: Filter by active status.
            external_identity: Filter by external identity.
            last_connected_after: Filter by last connection date.
            last_connected_before: Filter by last connection date.
            managed: Filter by managed status.
            p: Page number.
            ps: Page size.
            q: Search query.
            sonar_lint_last_connection_date_from: SonarLint connection date filter.
            sonar_lint_last_connection_date_to: SonarLint connection date filter.

        Returns:
            Response containing list of users.

        Example:
            >>> response = client.users.search(q="john")
            >>> for user in response.users:
            ...     print(user.name)
        """
        params: dict[str, Any] = {}

        if active is not None:
            params["active"] = str(active).lower()
        if external_identity:
            params["externalIdentity"] = external_identity
        if last_connected_after:
            params["lastConnectedAfter"] = last_connected_after
        if last_connected_before:
            params["lastConnectedBefore"] = last_connected_before
        if managed is not None:
            params["managed"] = str(managed).lower()
        if p:
            params["p"] = p
        if ps:
            params["ps"] = ps
        if q:
            params["q"] = q
        if sonar_lint_last_connection_date_from:
            params["sonarLintLastConnectionDateFrom"] = (
                sonar_lint_last_connection_date_from
            )
        if sonar_lint_last_connection_date_to:
            params["sonarLintLastConnectionDateTo"] = sonar_lint_last_connection_date_to

        return self._get_model("/search", UserSearchResponse, params=params)

    def update(
        self,
        login: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        scm_accounts: Optional[list[str]] = None,
    ) -> User:
        """Update a user.

        Requires 'Administer System' permission.

        Args:
            login: User login.
            email: New email.
            name: New display name.
            scm_accounts: New SCM accounts.

        Returns:
            The updated user.

        Example:
            >>> user = client.users.update(login="jdoe", name="John Doe Jr.")
        """
        data: dict[str, Any] = {"login": login}

        if email:
            data["email"] = email
        if name:
            data["name"] = name
        if scm_accounts:
            data["scmAccount"] = scm_accounts

        response = self._post("/update", data=data)
        return User.model_validate(response.get("user", response))

    def update_login(self, login: str, new_login: str) -> None:
        """Update a user's login.

        Requires 'Administer System' permission.

        Args:
            login: Current user login.
            new_login: New user login.

        Example:
            >>> client.users.update_login(login="old-login", new_login="new-login")
        """
        self._post(
            "/update_login",
            data={
                "login": login,
                "newLogin": new_login,
            },
        )
