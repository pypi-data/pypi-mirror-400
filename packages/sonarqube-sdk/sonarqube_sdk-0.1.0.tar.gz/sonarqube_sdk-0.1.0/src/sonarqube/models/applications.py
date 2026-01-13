"""Pydantic models for Applications API.

This module provides models for the /api/applications endpoints including
creating, updating, and managing applications and their projects.

Example:
    Using application models::

        from sonarqube.models.applications import Application, ApplicationCreateResponse

        # Response from create endpoint
        response = ApplicationCreateResponse(
            application=Application(
                key="my-app", name="My Application", visibility="private"
            )
        )
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel
from sonarqube.models.common import Branch, Paging


class ApplicationProject(SonarQubeModel):
    """A project within an application.

    Attributes:
        key: Project key.
        name: Project name.
        enabled: Whether the project is enabled.
        selected: Whether the project is selected.
        branch: Branch name (if branch-specific).

    Example:
        >>> project = ApplicationProject(key="my-project", name="My Project", enabled=True)
    """

    key: str = Field(description="Project key")
    name: str = Field(description="Project name")
    enabled: Optional[bool] = Field(
        default=None,
        description="Whether the project is enabled",
    )
    selected: Optional[bool] = Field(
        default=None,
        description="Whether the project is selected",
    )
    branch: Optional[str] = Field(
        default=None,
        description="Branch name",
    )


class ApplicationBranch(SonarQubeModel):
    """A branch within an application.

    Attributes:
        name: Branch name.
        is_main: Whether this is the main branch.

    Example:
        >>> branch = ApplicationBranch(name="main", isMain=True)
        >>> print(branch.is_main)
        True
    """

    name: str = Field(description="Branch name")
    is_main: bool = Field(
        default=False,
        alias="isMain",
        description="Whether this is the main branch",
    )


class Application(SonarQubeModel):
    """A SonarQube application.

    Applications are collections of projects that can be analyzed together.

    Attributes:
        key: Unique application key.
        name: Application display name.
        description: Application description.
        visibility: Application visibility (public/private).
        projects: List of projects in the application.
        branches: List of branches in the application.

    Example:
        >>> app = Application(key="my-app", name="My Application", visibility="private")
    """

    key: str = Field(description="Unique application key")
    name: str = Field(description="Application display name")
    description: Optional[str] = Field(
        default=None,
        description="Application description",
    )
    visibility: Optional[str] = Field(
        default=None,
        description="Application visibility (public/private)",
    )
    projects: Optional[list[ApplicationProject]] = Field(
        default=None,
        description="List of projects in the application",
    )
    branches: Optional[list[ApplicationBranch]] = Field(
        default=None,
        description="List of branches in the application",
    )


class ApplicationCreateResponse(SonarQubeModel):
    """Response from creating an application.

    Attributes:
        application: The created application.

    Example:
        >>> response = ApplicationCreateResponse(
        ...     application=Application(key="my-app", name="My App")
        ... )
    """

    application: Application = Field(description="The created application")


class ApplicationShowResponse(SonarQubeModel):
    """Response from showing an application.

    Attributes:
        application: The application details.

    Example:
        >>> response = client.applications.show(application="my-app")
        >>> print(response.application.name)
    """

    application: Application = Field(description="The application details")


class ApplicationSearchResponse(SonarQubeModel):
    """Response from searching applications.

    Attributes:
        paging: Paging information.
        applications: List of applications.

    Example:
        >>> response = client.applications.search(q="my-app")
        >>> for app in response.applications:
        ...     print(app.name)
    """

    paging: Paging = Field(description="Paging information")
    applications: list[Application] = Field(
        default_factory=list,
        description="List of applications",
    )


class ApplicationProjectsSearchResponse(SonarQubeModel):
    """Response from searching projects for an application.

    Attributes:
        paging: Paging information.
        projects: List of projects.

    Example:
        >>> response = client.applications.search_projects(application="my-app")
        >>> for project in response.projects:
        ...     print(project.name)
    """

    paging: Paging = Field(description="Paging information")
    projects: list[ApplicationProject] = Field(
        default_factory=list,
        description="List of projects",
    )


class ApplicationBranchesResponse(SonarQubeModel):
    """Response from listing application branches.

    Attributes:
        branches: List of branches.

    Example:
        >>> response = client.applications.list_branches(application="my-app")
        >>> for branch in response.branches:
        ...     print(branch.name)
    """

    branches: list[Branch] = Field(
        default_factory=list,
        description="List of branches",
    )


class CreateBranchRequest(SonarQubeModel):
    """Request model for creating an application branch.

    Attributes:
        application: Application key.
        branch: Branch name.
        project: Project keys and branches mapping.

    Example:
        >>> request = CreateBranchRequest(
        ...     application="my-app", branch="feature-x", project=["project1", "project2"]
        ... )
    """

    application: str = Field(description="Application key")
    branch: str = Field(description="Branch name to create")
    project: list[str] = Field(description="Project keys to include")
    project_branch: Optional[list[str]] = Field(
        default=None,
        alias="projectBranch",
        description="Branch names for each project",
    )
