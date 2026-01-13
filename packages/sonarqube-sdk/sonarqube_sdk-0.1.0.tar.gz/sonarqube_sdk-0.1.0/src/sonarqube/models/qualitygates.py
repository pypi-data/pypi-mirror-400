"""Pydantic models for Quality Gates API.

This module provides models for the /api/qualitygates endpoints including
creating, updating, and managing quality gates.

Example:
    Using quality gate models::

        from sonarqube.models.qualitygates import QualityGateListResponse

        response = client.qualitygates.list()
        for gate in response.qualitygates:
            print(gate.name)
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel


class QualityGateCondition(SonarQubeModel):
    """A condition in a quality gate.

    Attributes:
        id: Condition ID.
        metric: Metric key.
        op: Operator (LT, GT, EQ).
        error: Error threshold.
    """

    id: Optional[int] = Field(default=None, description="Condition ID")
    metric: str = Field(description="Metric key")
    op: Optional[str] = Field(default=None, description="Operator")
    error: Optional[str] = Field(default=None, description="Error threshold")


class QualityGate(SonarQubeModel):
    """A SonarQube quality gate.

    Attributes:
        id: Quality gate ID.
        name: Quality gate name.
        is_default: Whether this is the default quality gate.
        is_built_in: Whether this is a built-in quality gate.
        actions: Available actions on this quality gate.
        conditions: List of conditions.

    Example:
        >>> gate = QualityGate(id="1", name="My Quality Gate", isDefault=True)
    """

    id: Optional[str] = Field(default=None, description="Quality gate ID")
    name: str = Field(description="Quality gate name")
    is_default: Optional[bool] = Field(
        default=None,
        alias="isDefault",
        description="Whether this is the default",
    )
    is_built_in: Optional[bool] = Field(
        default=None,
        alias="isBuiltIn",
        description="Whether this is built-in",
    )
    actions: Optional[dict[str, Any]] = Field(
        default=None,
        description="Available actions",
    )
    conditions: Optional[list[QualityGateCondition]] = Field(
        default=None,
        description="List of conditions",
    )
    caycStatus: Optional[str] = Field(
        default=None,
        description="Clean as You Code status",
    )


class QualityGateCreateResponse(SonarQubeModel):
    """Response from creating a quality gate.

    Attributes:
        id: Created quality gate ID.
        name: Quality gate name.
    """

    id: str = Field(description="Quality gate ID")
    name: str = Field(description="Quality gate name")


class QualityGateListResponse(SonarQubeModel):
    """Response from listing quality gates.

    Attributes:
        qualitygates: List of quality gates.
        default: ID of the default quality gate.
        actions: Available actions.
    """

    qualitygates: list[QualityGate] = Field(
        default_factory=list,
        description="List of quality gates",
    )
    default: Optional[str] = Field(
        default=None,
        description="Default quality gate ID",
    )
    actions: Optional[dict[str, Any]] = Field(
        default=None,
        description="Available actions",
    )


class QualityGateShowResponse(SonarQubeModel):
    """Response from showing a quality gate.

    Attributes:
        id: Quality gate ID.
        name: Quality gate name.
        is_default: Whether this is the default.
        is_built_in: Whether this is built-in.
        conditions: List of conditions.
        actions: Available actions.
    """

    id: str = Field(description="Quality gate ID")
    name: str = Field(description="Quality gate name")
    is_default: Optional[bool] = Field(
        default=None,
        alias="isDefault",
        description="Whether this is the default",
    )
    is_built_in: Optional[bool] = Field(
        default=None,
        alias="isBuiltIn",
        description="Whether this is built-in",
    )
    conditions: Optional[list[QualityGateCondition]] = Field(
        default=None,
        description="List of conditions",
    )
    actions: Optional[dict[str, Any]] = Field(
        default=None,
        description="Available actions",
    )
    caycStatus: Optional[str] = Field(
        default=None,
        description="Clean as You Code status",
    )


class ProjectStatusCondition(SonarQubeModel):
    """A condition status for a project.

    Attributes:
        status: Condition status (OK, ERROR).
        metric_key: Metric key.
        comparator: Comparator used.
        error_threshold: Error threshold.
        actual_value: Actual metric value.
    """

    status: str = Field(description="Condition status")
    metric_key: str = Field(alias="metricKey", description="Metric key")
    comparator: str = Field(description="Comparator")
    error_threshold: Optional[str] = Field(
        default=None,
        alias="errorThreshold",
        description="Error threshold",
    )
    actual_value: Optional[str] = Field(
        default=None,
        alias="actualValue",
        description="Actual value",
    )


class ProjectStatus(SonarQubeModel):
    """Project quality gate status.

    Attributes:
        status: Overall status (OK, ERROR, NONE).
        conditions: List of condition statuses.
        periods: Analysis periods.
        ignored_conditions: Whether conditions were ignored.
    """

    status: str = Field(description="Overall status")
    conditions: Optional[list[ProjectStatusCondition]] = Field(
        default=None,
        description="Condition statuses",
    )
    periods: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Analysis periods",
    )
    ignored_conditions: Optional[bool] = Field(
        default=None,
        alias="ignoredConditions",
        description="Whether conditions were ignored",
    )


class ProjectStatusResponse(SonarQubeModel):
    """Response from getting project status.

    Attributes:
        project_status: Project quality gate status.
    """

    project_status: ProjectStatus = Field(
        alias="projectStatus",
        description="Project status",
    )


class CreateConditionResponse(SonarQubeModel):
    """Response from creating a condition.

    Attributes:
        id: Condition ID.
        metric: Metric key.
        op: Operator.
        error: Error threshold.
    """

    id: int = Field(description="Condition ID")
    metric: str = Field(description="Metric key")
    op: str = Field(description="Operator")
    error: str = Field(description="Error threshold")


class SearchProjectsResponse(SonarQubeModel):
    """Response from searching projects with quality gate.

    Attributes:
        paging: Paging information.
        results: List of projects.
    """

    paging: Optional[dict[str, Any]] = Field(default=None, description="Paging")
    results: list[dict[str, Any]] = Field(default_factory=list, description="Results")
