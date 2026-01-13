"""Sources API for SonarQube SDK.

This module provides methods to get source code and SCM information.

Example:
    Using the Sources API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Get source lines
        sources = client.sources.lines(key="my-project:src/main.py")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.sources import ScmResponse, SourcesResponse


class SourcesAPI(BaseAPI):
    """API for getting source code.

    Attributes:
        API_PATH: Base path for sources API ("/api/sources").
    """

    API_PATH = "/api/sources"

    def raw(
        self,
        key: str,
        branch: Optional[str] = None,
        pull_request: Optional[str] = None,
    ) -> str:
        """Get raw source code.

        Requires 'Browse' permission on the file's project.

        Args:
            key: File key.
            branch: Branch name.
            pull_request: Pull request ID.

        Returns:
            Raw source code content.

        Example:
            >>> source = client.sources.raw(key="my-project:src/main.py")
            >>> print(source)
        """
        response = self._get(
            "/raw",
            params={
                "key": key,
                "branch": branch,
                "pullRequest": pull_request,
            },
        )
        return str(response) if response else ""

    def lines(
        self,
        key: str,
        branch: Optional[str] = None,
        from_line: Optional[int] = None,
        pull_request: Optional[str] = None,
        to: Optional[int] = None,
    ) -> SourcesResponse:
        """Get source code with line information.

        Requires 'Browse' permission on the file's project.

        Args:
            key: File key.
            branch: Branch name.
            from_line: Start line number.
            pull_request: Pull request ID.
            to: End line number.

        Returns:
            Response containing source lines.

        Example:
            >>> response = client.sources.lines(
            ...     key="my-project:src/main.py", from_line=1, to=50
            ... )
            >>> for line in response.sources:
            ...     print(f"{line.line}: {line.code}")
        """
        params: dict[str, Any] = {"key": key}

        if branch:
            params["branch"] = branch
        if from_line:
            params["from"] = from_line
        if pull_request:
            params["pullRequest"] = pull_request
        if to:
            params["to"] = to

        return self._get_model("/lines", SourcesResponse, params=params)

    def scm(
        self,
        key: str,
        commits_by_line: Optional[bool] = None,
        from_line: Optional[int] = None,
        to: Optional[int] = None,
    ) -> ScmResponse:
        """Get SCM information for source code.

        Requires 'Browse' permission on the file's project.

        Args:
            key: File key.
            commits_by_line: Return commits by line.
            from_line: Start line number.
            to: End line number.

        Returns:
            Response containing SCM information.

        Example:
            >>> scm = client.sources.scm(key="my-project:src/main.py")
        """
        params: dict[str, Any] = {"key": key}

        if commits_by_line is not None:
            params["commits_by_line"] = str(commits_by_line).lower()
        if from_line:
            params["from"] = from_line
        if to:
            params["to"] = to

        return self._get_model("/scm", ScmResponse, params=params)
