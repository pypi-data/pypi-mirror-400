"""Hotspots API for SonarQube SDK.

This module provides methods to manage security hotspots.

Example:
    Using the Hotspots API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Search for hotspots
        hotspots = client.hotspots.search(project_key="my-project")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.hotspots import (
    HotspotSearchResponse,
    HotspotShowResponse,
)


class HotspotsAPI(BaseAPI):
    """API for managing security hotspots.

    Attributes:
        API_PATH: Base path for hotspots API ("/api/hotspots").
    """

    API_PATH = "/api/hotspots"

    def change_status(
        self,
        hotspot: str,
        status: str,
        comment: Optional[str] = None,
        resolution: Optional[str] = None,
    ) -> None:
        """Change hotspot status.

        Requires 'Administer Security Hotspots' permission.

        Args:
            hotspot: Hotspot key.
            status: New status (TO_REVIEW, ACKNOWLEDGED, FIXED, SAFE).
            comment: Comment.
            resolution: Resolution (FIXED, SAFE).

        Example:
            >>> client.hotspots.change_status(
            ...     hotspot="AX123", status="REVIEWED", resolution="SAFE"
            ... )
        """
        data: dict[str, Any] = {
            "hotspot": hotspot,
            "status": status,
        }
        if comment:
            data["comment"] = comment
        if resolution:
            data["resolution"] = resolution

        self._post("/change_status", data=data)

    def search(
        self,
        branch: Optional[str] = None,
        files: Optional[list[str]] = None,
        hotspots: Optional[list[str]] = None,
        in_new_code_period: Optional[bool] = None,
        only_mine: Optional[bool] = None,
        owasp_asvs_level: Optional[str] = None,
        p: Optional[int] = None,
        project_key: Optional[str] = None,
        ps: Optional[int] = None,
        pull_request: Optional[str] = None,
        resolution: Optional[str] = None,
        status: Optional[str] = None,
    ) -> HotspotSearchResponse:
        """Search for hotspots.

        Requires 'Browse' permission on the project.

        Args:
            branch: Branch name.
            files: File paths to filter.
            hotspots: Hotspot keys to filter.
            in_new_code_period: Filter by new code period.
            only_mine: Only show hotspots assigned to me.
            owasp_asvs_level: OWASP ASVS level filter.
            p: Page number.
            project_key: Project key.
            ps: Page size.
            pull_request: Pull request ID.
            resolution: Resolution filter.
            status: Status filter.

        Returns:
            Response containing hotspots.

        Example:
            >>> response = client.hotspots.search(project_key="my-project")
            >>> for hotspot in response.hotspots:
            ...     print(f"{hotspot.security_category}: {hotspot.message}")
        """
        params: dict[str, Any] = {}

        if branch:
            params["branch"] = branch
        if files:
            params["files"] = ",".join(files)
        if hotspots:
            params["hotspots"] = ",".join(hotspots)
        if in_new_code_period is not None:
            params["inNewCodePeriod"] = str(in_new_code_period).lower()
        if only_mine is not None:
            params["onlyMine"] = str(only_mine).lower()
        if owasp_asvs_level:
            params["owaspAsvsLevel"] = owasp_asvs_level
        if p:
            params["p"] = p
        if project_key:
            params["projectKey"] = project_key
        if ps:
            params["ps"] = ps
        if pull_request:
            params["pullRequest"] = pull_request
        if resolution:
            params["resolution"] = resolution
        if status:
            params["status"] = status

        return self._get_model("/search", HotspotSearchResponse, params=params)

    def show(self, hotspot: str) -> HotspotShowResponse:
        """Get hotspot details.

        Requires 'Browse' permission on the project.

        Args:
            hotspot: Hotspot key.

        Returns:
            Response containing hotspot details.

        Example:
            >>> hotspot = client.hotspots.show(hotspot="AX123")
            >>> print(hotspot.message)
        """
        return self._get_model(
            "/show", HotspotShowResponse, params={"hotspot": hotspot}
        )

    def assign(
        self,
        hotspot: str,
        assignee: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        """Assign a hotspot.

        Requires 'Browse' permission on the project.

        Args:
            hotspot: Hotspot key.
            assignee: Assignee login (omit to unassign).
            comment: Optional comment.

        Example:
            >>> client.hotspots.assign(hotspot="AX123", assignee="jdoe")
        """
        data: dict[str, Any] = {"hotspot": hotspot}
        if assignee:
            data["assignee"] = assignee
        if comment:
            data["comment"] = comment

        self._post("/assign", data=data)

    def add_comment(self, hotspot: str, comment: str) -> None:
        """Add a comment to a hotspot.

        Requires 'Browse' permission on the project.

        Args:
            hotspot: Hotspot key.
            comment: Comment text.

        Example:
            >>> client.hotspots.add_comment(
            ...     hotspot="AX123", comment="This looks like a false positive."
            ... )
        """
        self._post(
            "/add_comment",
            data={
                "hotspot": hotspot,
                "comment": comment,
            },
        )
