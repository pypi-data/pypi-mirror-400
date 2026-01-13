"""Pydantic models for Hotspots API.

This module provides models for the /api/hotspots endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel
from sonarqube.models.common import Component, Paging


class Hotspot(SonarQubeModel):
    """A security hotspot.

    Attributes:
        key: Hotspot key.
        component: Component key.
        project: Project key.
        security_category: Security category.
        vulnerability_probability: Vulnerability probability.
        status: Hotspot status.
        resolution: Hotspot resolution.
        line: Line number.
        message: Hotspot message.
        assignee: Assignee login.
        author: Author.
        creation_date: Creation date.
        update_date: Update date.
        flows: Issue flows.
        rule_key: Rule key.
    """

    key: str = Field(description="Hotspot key")
    component: str = Field(description="Component key")
    project: str = Field(description="Project key")
    security_category: Optional[str] = Field(
        default=None,
        alias="securityCategory",
        description="Security category",
    )
    vulnerability_probability: Optional[str] = Field(
        default=None,
        alias="vulnerabilityProbability",
        description="Vulnerability probability",
    )
    status: Optional[str] = Field(default=None, description="Status")
    resolution: Optional[str] = Field(default=None, description="Resolution")
    line: Optional[int] = Field(default=None, description="Line number")
    message: Optional[str] = Field(default=None, description="Message")
    assignee: Optional[str] = Field(default=None, description="Assignee")
    author: Optional[str] = Field(default=None, description="Author")
    creation_date: Optional[str] = Field(
        default=None,
        alias="creationDate",
        description="Creation date",
    )
    update_date: Optional[str] = Field(
        default=None,
        alias="updateDate",
        description="Update date",
    )
    flows: Optional[list[dict[str, Any]]] = Field(default=None, description="Flows")
    rule_key: Optional[str] = Field(
        default=None,
        alias="ruleKey",
        description="Rule key",
    )
    text_range: Optional[dict[str, Any]] = Field(
        default=None,
        alias="textRange",
        description="Text range",
    )


class HotspotSearchResponse(SonarQubeModel):
    """Response from searching hotspots.

    Attributes:
        paging: Paging information.
        hotspots: List of hotspots.
        components: Referenced components.
    """

    paging: Paging = Field(description="Paging information")
    hotspots: list[Hotspot] = Field(
        default_factory=list,
        description="List of hotspots",
    )
    components: Optional[list[Component]] = Field(
        default=None,
        description="Referenced components",
    )


class HotspotShowResponse(SonarQubeModel):
    """Response from showing a hotspot.

    Attributes:
        key: Hotspot key.
        component: Component details.
        project: Project details.
        rule: Rule details.
        status: Hotspot status.
        resolution: Hotspot resolution.
        message: Hotspot message.
        line: Line number.
        author: Author.
        creation_date: Creation date.
        update_date: Update date.
        changelog: Changelog entries.
        comment: Comments.
        users: Referenced users.
        can_change_status: Whether status can be changed.
    """

    key: str = Field(description="Hotspot key")
    component: Optional[dict[str, Any]] = Field(
        default=None, description="Component details"
    )
    project: Optional[dict[str, Any]] = Field(
        default=None, description="Project details"
    )
    rule: Optional[dict[str, Any]] = Field(default=None, description="Rule details")
    status: Optional[str] = Field(default=None, description="Status")
    resolution: Optional[str] = Field(default=None, description="Resolution")
    message: Optional[str] = Field(default=None, description="Message")
    line: Optional[int] = Field(default=None, description="Line number")
    author: Optional[str] = Field(default=None, description="Author")
    creation_date: Optional[str] = Field(
        default=None,
        alias="creationDate",
        description="Creation date",
    )
    update_date: Optional[str] = Field(
        default=None,
        alias="updateDate",
        description="Update date",
    )
    changelog: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Changelog"
    )
    comment: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Comments"
    )
    users: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Referenced users"
    )
    can_change_status: Optional[bool] = Field(
        default=None,
        alias="canChangeStatus",
        description="Whether status can be changed",
    )
