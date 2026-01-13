"""Settings API for SonarQube SDK.

This module provides methods to manage SonarQube settings.

Example:
    Using the Settings API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Get settings
        settings = client.settings.values(keys=["sonar.core.serverBaseURL"])
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.settings import (
    SettingsListResponse,
    SettingsValuesResponse,
)


class SettingsAPI(BaseAPI):
    """API for managing SonarQube settings.

    Attributes:
        API_PATH: Base path for settings API ("/api/settings").
    """

    API_PATH = "/api/settings"

    def list_definitions(
        self,
        component: Optional[str] = None,
    ) -> SettingsListResponse:
        """List settings definitions.

        Args:
            component: Component key.

        Returns:
            Response containing settings definitions.

        Example:
            >>> definitions = client.settings.list_definitions()
            >>> for defn in definitions.definitions:
            ...     print(f"{defn.key}: {defn.name}")
        """
        return self._get_model(
            "/list_definitions",
            SettingsListResponse,
            params={"component": component},
        )

    def reset(
        self,
        keys: list[str],
        branch: Optional[str] = None,
        component: Optional[str] = None,
        pull_request: Optional[str] = None,
    ) -> None:
        """Reset settings to their default values.

        Requires 'Administer' permission on the component.

        Args:
            keys: List of setting keys to reset.
            branch: Branch name.
            component: Component key.
            pull_request: Pull request ID.

        Example:
            >>> client.settings.reset(keys=["sonar.links.homepage"], component="my-project")
        """
        data: dict[str, Any] = {"keys": ",".join(keys)}

        if branch:
            data["branch"] = branch
        if component:
            data["component"] = component
        if pull_request:
            data["pullRequest"] = pull_request

        self._post("/reset", data=data)

    def set(
        self,
        key: str,
        branch: Optional[str] = None,
        component: Optional[str] = None,
        field_values: Optional[list[str]] = None,
        pull_request: Optional[str] = None,
        value: Optional[str] = None,
        values: Optional[list[str]] = None,
    ) -> None:
        """Set a setting value.

        Requires 'Administer' permission on the component.

        Args:
            key: Setting key.
            branch: Branch name.
            component: Component key.
            field_values: Field values (for property sets).
            pull_request: Pull request ID.
            value: Setting value.
            values: Setting values (for multi-value settings).

        Example:
            >>> client.settings.set(
            ...     key="sonar.links.homepage",
            ...     value="https://example.com",
            ...     component="my-project",
            ... )
        """
        data: dict[str, Any] = {"key": key}

        if branch:
            data["branch"] = branch
        if component:
            data["component"] = component
        if field_values:
            data["fieldValues"] = field_values
        if pull_request:
            data["pullRequest"] = pull_request
        if value:
            data["value"] = value
        if values:
            data["values"] = values

        self._post("/set", data=data)

    def values(
        self,
        component: Optional[str] = None,
        keys: Optional[list[str]] = None,
    ) -> SettingsValuesResponse:
        """Get settings values.

        Args:
            component: Component key.
            keys: List of setting keys to retrieve.

        Returns:
            Response containing settings values.

        Example:
            >>> response = client.settings.values(keys=["sonar.core.serverBaseURL"])
            >>> for setting in response.settings:
            ...     print(f"{setting.key}: {setting.value}")
        """
        params: dict[str, Any] = {}

        if component:
            params["component"] = component
        if keys:
            params["keys"] = ",".join(keys)

        return self._get_model("/values", SettingsValuesResponse, params=params)
