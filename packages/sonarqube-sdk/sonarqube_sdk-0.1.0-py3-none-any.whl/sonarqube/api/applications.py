"""Applications API for SonarQube SDK.

This module provides methods to manage SonarQube applications, which are
collections of projects that can be analyzed together.

Example:
    Using the Applications API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Create an application
        app = client.applications.create(
            name="My Application", key="my-app", visibility="private"
        )

        # Add a project to the application
        client.applications.add_project(application="my-app", project="my-project")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.applications import (
    ApplicationCreateResponse,
    ApplicationProjectsSearchResponse,
    ApplicationSearchResponse,
    ApplicationShowResponse,
)


class ApplicationsAPI(BaseAPI):
    """API for managing SonarQube applications.

    Applications are collections of projects that can be analyzed together.
    This API provides methods to create, update, delete, and manage
    applications and their projects.

    Attributes:
        API_PATH: Base path for applications API ("/api/applications").

    Example:
        Using the applications API::

            # Create an application
            app = client.applications.create(name="My Application", key="my-app")

            # Add a project
            client.applications.add_project(application="my-app", project="my-project")

            # Get application details
            details = client.applications.show(application="my-app")
            print(details.application.name)
    """

    API_PATH = "/api/applications"

    def add_project(
        self,
        application: str,
        project: str,
    ) -> None:
        """Add a project to an application.

        Requires 'Administrator' permission on the application and 'Browse'
        permission on the project.

        Args:
            application: Application key.
            project: Project key.

        Raises:
            SonarQubeNotFoundError: If application or project not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.add_project(application="my-app", project="my-project")
        """
        self._post(
            "/add_project",
            data={
                "application": application,
                "project": project,
            },
        )

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        key: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> ApplicationCreateResponse:
        """Create a new application.

        Requires 'Administrator' permission on the portfolio parent if it exists.

        Args:
            name: Application name.
            description: Application description.
            key: Application key. If not provided, a key will be generated.
            visibility: Application visibility (public/private).

        Returns:
            Response containing the created application.

        Raises:
            SonarQubeValidationError: If validation fails.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> app = client.applications.create(
            ...     name="My Application", key="my-app", visibility="private"
            ... )
            >>> print(app.application.key)
            'my-app'
        """
        return self._post_model(
            "/create",
            ApplicationCreateResponse,
            data={
                "name": name,
                "description": description,
                "key": key,
                "visibility": visibility,
            },
        )

    def create_branch(
        self,
        application: str,
        branch: str,
        project: list[str],
        project_branch: Optional[list[str]] = None,
    ) -> None:
        """Create a new branch for an application.

        Requires 'Administrator' permission on the application.

        Args:
            application: Application key.
            branch: Branch name to create.
            project: List of project keys to include in the branch.
            project_branch: List of branch names for each project.

        Raises:
            SonarQubeValidationError: If validation fails.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.create_branch(
            ...     application="my-app",
            ...     branch="feature-x",
            ...     project=["project1", "project2"],
            ...     project_branch=["feature-x", "feature-x"],
            ... )
        """
        data: dict[str, Any] = {
            "application": application,
            "branch": branch,
            "project": project,
        }
        if project_branch:
            data["projectBranch"] = project_branch

        self._post("/create_branch", data=data)

    def delete(self, application: str) -> None:
        """Delete an application.

        Requires 'Administrator' permission on the application.

        Args:
            application: Application key.

        Raises:
            SonarQubeNotFoundError: If application not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.delete(application="my-app")
        """
        self._post("/delete", data={"application": application})

    def delete_branch(self, application: str, branch: str) -> None:
        """Delete a branch from an application.

        Requires 'Administrator' permission on the application.

        Args:
            application: Application key.
            branch: Branch name to delete.

        Raises:
            SonarQubeNotFoundError: If application or branch not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.delete_branch(application="my-app", branch="feature-x")
        """
        self._post(
            "/delete_branch",
            data={
                "application": application,
                "branch": branch,
            },
        )

    def remove_project(self, application: str, project: str) -> None:
        """Remove a project from an application.

        Requires 'Administrator' permission on the application.

        Args:
            application: Application key.
            project: Project key.

        Raises:
            SonarQubeNotFoundError: If application or project not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.remove_project(application="my-app", project="my-project")
        """
        self._post(
            "/remove_project",
            data={
                "application": application,
                "project": project,
            },
        )

    def search(
        self,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
    ) -> ApplicationSearchResponse:
        """Search for applications.

        Requires 'Browse' permission on the application.

        Args:
            p: Page number (1-based).
            ps: Page size (max 500).
            q: Search query for application name.

        Returns:
            Response containing list of applications and paging info.

        Example:
            >>> response = client.applications.search(q="my-app")
            >>> for app in response.applications:
            ...     print(app.name)
        """
        return self._get_model(
            "/search",
            ApplicationSearchResponse,
            params={
                "p": p,
                "ps": ps,
                "q": q,
            },
        )

    def search_projects(
        self,
        application: str,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
        selected: Optional[str] = None,
    ) -> ApplicationProjectsSearchResponse:
        """Search for projects in an application.

        Requires 'Browse' permission on the application.

        Args:
            application: Application key.
            p: Page number (1-based).
            ps: Page size (max 500).
            q: Search query for project name.
            selected: Filter by selection (all, selected, deselected).

        Returns:
            Response containing list of projects and paging info.

        Example:
            >>> response = client.applications.search_projects(
            ...     application="my-app", q="backend"
            ... )
            >>> for project in response.projects:
            ...     print(project.name)
        """
        return self._get_model(
            "/search_projects",
            ApplicationProjectsSearchResponse,
            params={
                "application": application,
                "p": p,
                "ps": ps,
                "q": q,
                "selected": selected,
            },
        )

    def set_tags(self, application: str, tags: list[str]) -> None:
        """Set tags on an application.

        Requires 'Administrator' permission on the application.

        Args:
            application: Application key.
            tags: List of tags to set.

        Raises:
            SonarQubeNotFoundError: If application not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.set_tags(
            ...     application="my-app", tags=["team-a", "production"]
            ... )
        """
        self._post(
            "/set_tags",
            data={
                "application": application,
                "tags": ",".join(tags),
            },
        )

    def show(
        self,
        application: str,
        branch: Optional[str] = None,
    ) -> ApplicationShowResponse:
        """Get application details.

        Requires 'Browse' permission on the application.

        Args:
            application: Application key.
            branch: Branch name (optional).

        Returns:
            Response containing application details.

        Raises:
            SonarQubeNotFoundError: If application not found.

        Example:
            >>> response = client.applications.show(application="my-app")
            >>> print(response.application.name)
        """
        return self._get_model(
            "/show",
            ApplicationShowResponse,
            params={
                "application": application,
                "branch": branch,
            },
        )

    def show_leak(
        self,
        application: str,
        branch: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get the leak period for an application.

        Requires 'Browse' permission on the application.

        Args:
            application: Application key.
            branch: Branch name (optional).

        Returns:
            Dictionary containing leak period information.

        Example:
            >>> leak = client.applications.show_leak(application="my-app")
        """
        return self._get(
            "/show_leak",
            params={
                "application": application,
                "branch": branch,
            },
        )

    def update(
        self,
        application: str,
        name: str,
        description: Optional[str] = None,
    ) -> None:
        """Update an application.

        Requires 'Administrator' permission on the application.

        Args:
            application: Application key.
            name: New application name.
            description: New application description.

        Raises:
            SonarQubeNotFoundError: If application not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.update(
            ...     application="my-app",
            ...     name="My Updated Application",
            ...     description="Updated description",
            ... )
        """
        self._post(
            "/update",
            data={
                "application": application,
                "name": name,
                "description": description,
            },
        )

    def update_branch(
        self,
        application: str,
        branch: str,
        name: str,
        project: list[str],
        project_branch: Optional[list[str]] = None,
    ) -> None:
        """Update an application branch.

        Requires 'Administrator' permission on the application.

        Args:
            application: Application key.
            branch: Current branch name.
            name: New branch name.
            project: List of project keys.
            project_branch: List of branch names for each project.

        Raises:
            SonarQubeNotFoundError: If application or branch not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> client.applications.update_branch(
            ...     application="my-app",
            ...     branch="feature-x",
            ...     name="feature-y",
            ...     project=["project1", "project2"],
            ... )
        """
        data: dict[str, Any] = {
            "application": application,
            "branch": branch,
            "name": name,
            "project": project,
        }
        if project_branch:
            data["projectBranch"] = project_branch

        self._post("/update_branch", data=data)
