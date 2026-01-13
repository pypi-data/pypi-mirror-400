"""Components API for SonarQube SDK.

This module provides methods to search and get component information.

Example:
    Using the Components API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Show component
        component = client.components.show(component="my-project")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.components import (
    ComponentSearchResponse,
    ComponentShowResponse,
    ComponentTreeResponse,
)


class ComponentsAPI(BaseAPI):
    """API for searching and getting SonarQube components.

    Attributes:
        API_PATH: Base path for components API ("/api/components").
    """

    API_PATH = "/api/components"

    def show(
        self,
        component: str,
        branch: Optional[str] = None,
        pull_request: Optional[str] = None,
    ) -> ComponentShowResponse:
        """Get component details.

        Requires 'Browse' permission on the project.

        Args:
            component: Component key.
            branch: Branch name.
            pull_request: Pull request ID.

        Returns:
            Response containing component details.

        Example:
            >>> response = client.components.show(component="my-project")
            >>> print(response.component.name)
        """
        return self._get_model(
            "/show",
            ComponentShowResponse,
            params={
                "component": component,
                "branch": branch,
                "pullRequest": pull_request,
            },
        )

    def tree(
        self,
        component: str,
        asc: Optional[bool] = None,
        branch: Optional[str] = None,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        pull_request: Optional[str] = None,
        q: Optional[str] = None,
        qualifiers: Optional[list[str]] = None,
        s: Optional[str] = None,
        strategy: Optional[str] = None,
    ) -> ComponentTreeResponse:
        """Get component tree.

        Requires 'Browse' permission on the project.

        Args:
            component: Component key.
            asc: Ascending sort order.
            branch: Branch name.
            p: Page number.
            ps: Page size.
            pull_request: Pull request ID.
            q: Search query.
            qualifiers: Component qualifiers to filter.
            s: Sort field.
            strategy: Tree strategy (all, children, leaves).

        Returns:
            Response containing component tree.

        Example:
            >>> tree = client.components.tree(component="my-project", qualifiers=["FIL"])
            >>> for comp in tree.components:
            ...     print(comp.path)
        """
        params: dict[str, Any] = {"component": component}

        if asc is not None:
            params["asc"] = str(asc).lower()
        if branch:
            params["branch"] = branch
        if p:
            params["p"] = p
        if ps:
            params["ps"] = ps
        if pull_request:
            params["pullRequest"] = pull_request
        if q:
            params["q"] = q
        if qualifiers:
            params["qualifiers"] = ",".join(qualifiers)
        if s:
            params["s"] = s
        if strategy:
            params["strategy"] = strategy

        return self._get_model("/tree", ComponentTreeResponse, params=params)

    def search(
        self,
        qualifiers: list[str],
        p: Optional[int] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
    ) -> ComponentSearchResponse:
        """Search for components.

        Args:
            qualifiers: Component qualifiers to search.
            p: Page number.
            ps: Page size.
            q: Search query.

        Returns:
            Response containing components.

        Example:
            >>> response = client.components.search(qualifiers=["TRK"], q="backend")
        """
        params: dict[str, Any] = {"qualifiers": ",".join(qualifiers)}

        if p:
            params["p"] = p
        if ps:
            params["ps"] = ps
        if q:
            params["q"] = q

        return self._get_model("/search", ComponentSearchResponse, params=params)
