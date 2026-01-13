"""Pydantic models for System API.

This module provides models for the /api/system endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel


class SystemHealth(SonarQubeModel):
    """System health status.

    Attributes:
        health: Health status (GREEN, YELLOW, RED).
        causes: List of causes for non-GREEN status.
        nodes: Cluster nodes (for Data Center Edition).
    """

    health: str = Field(description="Health status")
    causes: Optional[list[str]] = Field(default=None, description="Causes")
    nodes: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Cluster nodes"
    )


class SystemStatus(SonarQubeModel):
    """System status.

    Attributes:
        id: Instance ID.
        version: SonarQube version.
        status: System status.
    """

    id: str = Field(description="Instance ID")
    version: str = Field(description="SonarQube version")
    status: str = Field(description="System status")


class SystemInfo(SonarQubeModel):
    """Detailed system information.

    Attributes:
        health: Health status.
        causes: Health causes.
        system: System section.
        database: Database section.
        plugins: Installed plugins section.
        settings: Global settings section.
        statistics: Statistics section.
    """

    health: Optional[str] = Field(
        default=None, alias="Health", description="Health status"
    )
    causes: Optional[list[str]] = Field(
        default=None,
        alias="Health Causes",
        description="Health causes",
    )
    system: Optional[dict[str, Any]] = Field(
        default=None,
        alias="System",
        description="System section",
    )
    database: Optional[dict[str, Any]] = Field(
        default=None,
        alias="Database",
        description="Database section",
    )
    plugins: Optional[dict[str, Any]] = Field(
        default=None,
        alias="Plugins",
        description="Installed plugins",
    )


class SystemUpgradesResponse(SonarQubeModel):
    """Response from checking for upgrades.

    Attributes:
        upgrades: Available upgrades.
        update_center_refresh: Update center refresh date.
        installed_version_active: Whether installed version is active.
    """

    upgrades: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Available upgrades",
    )
    update_center_refresh: Optional[str] = Field(
        default=None,
        alias="updateCenterRefresh",
        description="Update center refresh date",
    )
    installed_version_active: Optional[bool] = Field(
        default=None,
        alias="installedVersionActive",
        description="Whether installed version is active",
    )
