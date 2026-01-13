"""Projects API for SonarQube SDK.

This module provides methods to manage SonarQube projects including
creating, searching, updating, and deleting projects.

Example:
    Using the Projects API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Search for projects
        projects = client.projects.search(q="backend")
        for project in projects.components:
            print(project.name)

        # Create a project
        project = client.projects.create(name="My Project", project="my-project")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.projects import (
    ExportFindingsResponse,
    LicenseUsageResponse,
    ProjectCreateResponse,
    ProjectSearchResponse,
)


class ProjectsAPI(BaseAPI):
    """API for managing SonarQube projects.

    Projects are the main organizational unit in SonarQube. This API
    provides methods to create, search, update, and delete projects.

    Attributes:
        API_PATH: Base path for projects API ("/api/projects").

    Example:
        Using the projects API::

            # Search for projects
            projects = client.projects.search(q="backend")

            # Create a project
            project = client.projects.create(name="My Project", project="my-project")

            # Delete a project
            client.projects.delete(project="my-project")
    """

    API_PATH = "/api/projects"

    def bulk_delete(
        self,
        analyzed_before: Optional[str] = None,
        on_provisioned_only: Optional[bool] = None,
        projects: Optional[list[str]] = None,
        q: Optional[str] = None,
        qualifiers: Optional[list[str]] = None,
        visibility: Optional[str] = None,
    ) -> None:
        """Delete multiple projects at once.

        Requires 'Administer System' permission. At most 1000 projects
        can be deleted per request.

        Args:
            analyzed_before: Filter projects analyzed before this date (ISO format).
            on_provisioned_only: Filter on provisioned projects only.
            projects: Comma-separated list of project keys to delete.
            q: Search query for project names or keys.
            qualifiers: Filter by component qualifiers (TRK, VW, APP).
            visibility: Filter by visibility (public/private).

        Raises:
            SonarQubeValidationError: If validation fails.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.projects.bulk_delete(projects=["project1", "project2"])
        """
        data: dict[str, Any] = {}
        if analyzed_before:
            data["analyzedBefore"] = analyzed_before
        if on_provisioned_only is not None:
            data["onProvisionedOnly"] = str(on_provisioned_only).lower()
        if projects:
            data["projects"] = ",".join(projects)
        if q:
            data["q"] = q
        if qualifiers:
            data["qualifiers"] = ",".join(qualifiers)
        if visibility:
            data["visibility"] = visibility

        self._post("/bulk_delete", data=data)

    def create(
        self,
        name: str,
        project: str,
        main_branch: Optional[str] = None,
        new_code_definition_type: Optional[str] = None,
        new_code_definition_value: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> ProjectCreateResponse:
        """Create a new project.

        Requires 'Create Projects' permission.

        Args:
            name: Project name (max 500 characters).
            project: Project key (unique identifier).
            main_branch: Main branch name (defaults to 'main').
            new_code_definition_type: Type for new code definition.
            new_code_definition_value: Value for new code definition.
            visibility: Project visibility (public/private).

        Returns:
            Response containing the created project.

        Raises:
            SonarQubeValidationError: If validation fails.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> project = client.projects.create(
            ...     name="My Project", project="my-project", visibility="private"
            ... )
            >>> print(project.project.key)
            'my-project'
        """
        return self._post_model(
            "/create",
            ProjectCreateResponse,
            data={
                "name": name,
                "project": project,
                "mainBranch": main_branch,
                "newCodeDefinitionType": new_code_definition_type,
                "newCodeDefinitionValue": new_code_definition_value,
                "visibility": visibility,
            },
        )

    def delete(self, project: str) -> None:
        """Delete a project.

        Requires 'Administer System' permission or 'Administer' on the project.

        Args:
            project: Project key.

        Raises:
            SonarQubeNotFoundError: If project not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.projects.delete(project="my-project")
        """
        self._post("/delete", data={"project": project})

    def export_findings(
        self,
        project: str,
        branch: Optional[str] = None,
        pull_request: Optional[str] = None,
    ) -> ExportFindingsResponse:
        """Export all findings for a project.

        Requires 'Browse' permission on the project.

        Args:
            project: Project key.
            branch: Branch name.
            pull_request: Pull request ID.

        Returns:
            Response containing exported findings.

        Example:
            >>> findings = client.projects.export_findings(project="my-project")
        """
        return self._get_model(
            "/export_findings",
            ExportFindingsResponse,
            params={
                "project": project,
                "branch": branch,
                "pullRequest": pull_request,
            },
        )

    def license_usage(self) -> LicenseUsageResponse:
        """Get license usage statistics.

        Requires 'Administer System' permission.

        Returns:
            Response containing license usage information.

        Example:
            >>> usage = client.projects.license_usage()
            >>> print(f"Total lines of code: {usage.lines_of_code}")
        """
        return self._get_model("/license_usage", LicenseUsageResponse)

    def search(
        self,
        analyzed_before: Optional[str] = None,
        on_provisioned_only: Optional[bool] = None,
        p: Optional[int] = None,
        projects: Optional[list[str]] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
        qualifiers: Optional[list[str]] = None,
        s: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> ProjectSearchResponse:
        """Search for projects.

        Requires 'Browse' permission on each returned project.

        Args:
            analyzed_before: Filter projects analyzed before this date.
            on_provisioned_only: Filter on provisioned projects only.
            p: Page number (1-based).
            projects: Comma-separated list of project keys.
            ps: Page size (max 500).
            q: Search query for project names or keys.
            qualifiers: Filter by component qualifiers.
            s: Sort field (key, name, qualifier, visibility).
            visibility: Filter by visibility.

        Returns:
            Response containing list of projects and paging info.

        Example:
            >>> response = client.projects.search(q="backend")
            >>> for project in response.components:
            ...     print(project.name)
        """
        params: dict[str, Any] = {}
        if analyzed_before:
            params["analyzedBefore"] = analyzed_before
        if on_provisioned_only is not None:
            params["onProvisionedOnly"] = str(on_provisioned_only).lower()
        if p:
            params["p"] = p
        if projects:
            params["projects"] = ",".join(projects)
        if ps:
            params["ps"] = ps
        if q:
            params["q"] = q
        if qualifiers:
            params["qualifiers"] = ",".join(qualifiers)
        if s:
            params["s"] = s
        if visibility:
            params["visibility"] = visibility

        return self._get_model("/search", ProjectSearchResponse, params=params)

    def update_key(self, from_key: str, to_key: str) -> None:
        """Update a project's key.

        Requires 'Administer' permission on the project.

        Args:
            from_key: Current project key.
            to_key: New project key.

        Raises:
            SonarQubeNotFoundError: If project not found.
            SonarQubeValidationError: If new key is invalid.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.projects.update_key(from_key="old-project-key", to_key="new-project-key")
        """
        self._post(
            "/update_key",
            data={
                "from": from_key,
                "to": to_key,
            },
        )

    def update_visibility(self, project: str, visibility: str) -> None:
        """Update a project's visibility.

        Requires 'Administer' permission on the project.

        Args:
            project: Project key.
            visibility: New visibility (public/private).

        Raises:
            SonarQubeNotFoundError: If project not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.projects.update_visibility(project="my-project", visibility="private")
        """
        self._post(
            "/update_visibility",
            data={
                "project": project,
                "visibility": visibility,
            },
        )
