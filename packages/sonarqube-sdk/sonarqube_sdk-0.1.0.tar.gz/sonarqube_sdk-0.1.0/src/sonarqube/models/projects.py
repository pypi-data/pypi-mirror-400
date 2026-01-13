"""Pydantic models for Projects API.

This module provides models for the /api/projects endpoints including
creating, searching, and managing projects.

Example:
    Using project models::

        from sonarqube.models.projects import ProjectSearchResponse

        response = client.projects.search(q="backend")
        for project in response.components:
            print(project.name)
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel
from sonarqube.models.common import Paging


class ProjectComponent(SonarQubeModel):
    """A project component in search results.

    Attributes:
        key: Unique project key.
        name: Project display name.
        qualifier: Component qualifier (TRK for projects).
        visibility: Project visibility.
        last_analysis_date: Date of last analysis.
        revision: Last analysis revision.
        managed: Whether the project is managed.

    Example:
        >>> component = ProjectComponent(
        ...     key="my-project", name="My Project", qualifier="TRK", visibility="private"
        ... )
    """

    key: str = Field(description="Unique project key")
    name: str = Field(description="Project display name")
    qualifier: str = Field(default="TRK", description="Component qualifier")
    visibility: Optional[str] = Field(
        default=None,
        description="Project visibility (public/private)",
    )
    last_analysis_date: Optional[str] = Field(
        default=None,
        alias="lastAnalysisDate",
        description="Date of last analysis",
    )
    revision: Optional[str] = Field(
        default=None,
        description="Last analysis revision",
    )
    managed: Optional[bool] = Field(
        default=None,
        description="Whether the project is managed",
    )
    is_favorite: Optional[bool] = Field(
        default=None,
        alias="isFavorite",
        description="Whether the project is marked as favorite",
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Project tags",
    )
    needs_issue_sync: Optional[bool] = Field(
        default=None,
        alias="needIssueSync",
        description="Whether the project needs issue sync",
    )


class ProjectSearchResponse(SonarQubeModel):
    """Response from searching projects.

    Attributes:
        paging: Paging information.
        components: List of project components.

    Example:
        >>> response = client.projects.search(q="backend")
        >>> print(f"Found {response.paging.total} projects")
        >>> for project in response.components:
        ...     print(project.name)
    """

    paging: Paging = Field(description="Paging information")
    components: list[ProjectComponent] = Field(
        default_factory=list,
        description="List of project components",
    )


class ProjectCreateResponse(SonarQubeModel):
    """Response from creating a project.

    Attributes:
        project: The created project.

    Example:
        >>> response = client.projects.create(name="My Project", project="my-project")
        >>> print(response.project.key)
    """

    project: ProjectComponent = Field(description="The created project")


class ExportFindingsResponse(SonarQubeModel):
    """Response from exporting findings.

    Attributes:
        export_date: Date of the export.
        findings: List of findings.
    """

    export_date: Optional[str] = Field(
        default=None,
        alias="exportDate",
        description="Date of the export",
    )
    findings: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="List of findings",
    )


class LicenseUsageResponse(SonarQubeModel):
    """Response from getting license usage.

    Attributes:
        lines_of_code: Total lines of code.
    """

    lines_of_code: Optional[int] = Field(
        default=None,
        alias="linesOfCode",
        description="Total lines of code",
    )
