"""Common Pydantic models shared across API domains.

This module provides models that are used by multiple API domains,
such as paging, components, and other shared data structures.

Example:
    Using the Paging model::

        from sonarqube.models.common import Paging

        paging = Paging(pageIndex=1, pageSize=100, total=250)
        print(f"Page {paging.page_index} of {paging.total_pages}")
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from pydantic import Field

from sonarqube.models.base import SonarQubeModel

T = TypeVar("T")


class Visibility(str, Enum):
    """Project/Application visibility.

    Attributes:
        PUBLIC: Visible to all users.
        PRIVATE: Visible only to users with explicit permissions.
    """

    PUBLIC = "public"
    PRIVATE = "private"


class Paging(SonarQubeModel):
    """Paging information for paginated API responses.

    Attributes:
        page_index: Current page number (1-based).
        page_size: Number of items per page.
        total: Total number of items.

    Example:
        >>> paging = Paging(pageIndex=1, pageSize=100, total=250)
        >>> paging.total_pages
        3
        >>> paging.has_next_page
        True
    """

    page_index: int = Field(
        alias="pageIndex", description="Current page number (1-based)"
    )
    page_size: int = Field(alias="pageSize", description="Number of items per page")
    total: int = Field(description="Total number of items")

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages.

        Returns:
            Total number of pages.
        """
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next_page(self) -> bool:
        """Check if there is a next page.

        Returns:
            True if there are more pages.
        """
        return self.page_index < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        """Check if there is a previous page.

        Returns:
            True if current page is not the first.
        """
        return self.page_index > 1


class PagingResponse(SonarQubeModel, Generic[T]):
    """Base model for paginated API responses.

    This is a generic model that can be used as a base for
    paginated response models.

    Attributes:
        paging: Paging information.
    """

    paging: Paging = Field(description="Paging information")


class Component(SonarQubeModel):
    """A SonarQube component (project, application, portfolio, etc.).

    Attributes:
        key: Unique component key.
        name: Component display name.
        qualifier: Component type (TRK=project, APP=application, etc.).
        visibility: Component visibility (public/private).
        project: Parent project key (for sub-components).

    Example:
        >>> component = Component(
        ...     key="my-project", name="My Project", qualifier="TRK", visibility="private"
        ... )
        >>> print(component.name)
        'My Project'
    """

    key: str = Field(description="Unique component key")
    name: str = Field(description="Component display name")
    qualifier: Optional[str] = Field(
        default=None,
        description="Component type (TRK=project, APP=application, VW=portfolio)",
    )
    visibility: Optional[str] = Field(
        default=None,
        description="Component visibility (public/private)",
    )
    project: Optional[str] = Field(
        default=None,
        description="Parent project key (for sub-components)",
    )


class Project(SonarQubeModel):
    """A SonarQube project.

    Attributes:
        key: Unique project key.
        name: Project display name.
        qualifier: Component qualifier (always 'TRK' for projects).
        visibility: Project visibility.
        last_analysis_date: Date of last analysis.
        revision: Last analysis revision.
        managed: Whether the project is managed.

    Example:
        >>> project = Project(
        ...     key="my-project", name="My Project", qualifier="TRK", visibility="private"
        ... )
    """

    key: str = Field(description="Unique project key")
    name: str = Field(description="Project display name")
    qualifier: str = Field(default="TRK", description="Component qualifier")
    visibility: Optional[str] = Field(
        default=None,
        description="Project visibility",
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


class Branch(SonarQubeModel):
    """A project or application branch.

    Attributes:
        name: Branch name.
        is_main: Whether this is the main branch.
        type: Branch type (LONG, SHORT, PULL_REQUEST).
        status: Analysis status.
        analysis_date: Date of last analysis.

    Example:
        >>> branch = Branch(name="main", isMain=True, type="LONG")
        >>> print(branch.is_main)
        True
    """

    name: str = Field(description="Branch name")
    is_main: bool = Field(
        default=False,
        alias="isMain",
        description="Whether this is the main branch",
    )
    type: Optional[str] = Field(
        default=None,
        description="Branch type (LONG, SHORT, PULL_REQUEST)",
    )
    status: Optional[dict[str, Any]] = Field(
        default=None,
        description="Analysis status",
    )
    analysis_date: Optional[str] = Field(
        default=None,
        alias="analysisDate",
        description="Date of last analysis",
    )


class ErrorMessage(SonarQubeModel):
    """An error message from the API.

    Attributes:
        msg: Error message text.
    """

    msg: str = Field(description="Error message text")


class ErrorResponse(SonarQubeModel):
    """Error response from the API.

    Attributes:
        errors: List of error messages.
    """

    errors: list[ErrorMessage] = Field(
        default_factory=list,
        description="List of error messages",
    )
