"""Pydantic models for Components API.

This module provides models for the /api/components endpoints.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel
from sonarqube.models.common import Paging


class ComponentItem(SonarQubeModel):
    """A component item.

    Attributes:
        key: Component key.
        name: Component name.
        qualifier: Component qualifier.
        path: Component path.
        language: Component language.
        project: Project key.
        branch: Branch name.
        pull_request: Pull request ID.
    """

    key: str = Field(description="Component key")
    name: Optional[str] = Field(default=None, description="Component name")
    qualifier: Optional[str] = Field(default=None, description="Component qualifier")
    path: Optional[str] = Field(default=None, description="Component path")
    language: Optional[str] = Field(default=None, description="Component language")
    project: Optional[str] = Field(default=None, description="Project key")
    branch: Optional[str] = Field(default=None, description="Branch name")
    pull_request: Optional[str] = Field(
        default=None,
        alias="pullRequest",
        description="Pull request ID",
    )
    description: Optional[str] = Field(default=None, description="Description")
    visibility: Optional[str] = Field(default=None, description="Visibility")
    analysisDate: Optional[str] = Field(default=None, description="Analysis date")
    version: Optional[str] = Field(default=None, description="Version")
    needIssueSync: Optional[bool] = Field(
        default=None,
        description="Whether component needs issue sync",
    )


class ComponentShowResponse(SonarQubeModel):
    """Response from showing a component.

    Attributes:
        component: The component.
        ancestors: List of ancestor components.
    """

    component: ComponentItem = Field(description="The component")
    ancestors: Optional[list[ComponentItem]] = Field(
        default=None,
        description="Ancestor components",
    )


class ComponentTreeResponse(SonarQubeModel):
    """Response from getting component tree.

    Attributes:
        paging: Paging information.
        base_component: Base component.
        components: List of child components.
    """

    paging: Paging = Field(description="Paging information")
    base_component: ComponentItem = Field(
        alias="baseComponent",
        description="Base component",
    )
    components: list[ComponentItem] = Field(
        default_factory=list,
        description="Child components",
    )


class ComponentSearchResponse(SonarQubeModel):
    """Response from searching components.

    Attributes:
        paging: Paging information.
        components: List of components.
    """

    paging: Paging = Field(description="Paging information")
    components: list[ComponentItem] = Field(
        default_factory=list,
        description="List of components",
    )
