"""Pydantic models for Measures API.

This module provides models for the /api/measures endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel


class Measure(SonarQubeModel):
    """A measure value.

    Attributes:
        metric: Metric key.
        value: Measure value.
        period: Period information.
        best_value: Whether this is the best value.
    """

    metric: str = Field(description="Metric key")
    value: Optional[str] = Field(default=None, description="Measure value")
    period: Optional[dict[str, Any]] = Field(
        default=None, description="Period information"
    )
    best_value: Optional[bool] = Field(
        default=None,
        alias="bestValue",
        description="Whether this is the best value",
    )


class MeasureComponent(SonarQubeModel):
    """A component with measures.

    Attributes:
        key: Component key.
        name: Component name.
        qualifier: Component qualifier.
        path: Component path.
        language: Component language.
        measures: List of measures.
    """

    key: str = Field(description="Component key")
    name: Optional[str] = Field(default=None, description="Component name")
    qualifier: Optional[str] = Field(default=None, description="Component qualifier")
    path: Optional[str] = Field(default=None, description="Component path")
    language: Optional[str] = Field(default=None, description="Component language")
    measures: Optional[list[Measure]] = Field(
        default=None,
        description="List of measures",
    )


class ComponentMeasuresResponse(SonarQubeModel):
    """Response from getting component measures.

    Attributes:
        component: Component with measures.
        metrics: List of metrics.
        period: Period information.
    """

    component: MeasureComponent = Field(description="Component with measures")
    metrics: Optional[list[dict[str, Any]]] = Field(default=None, description="Metrics")
    period: Optional[dict[str, Any]] = Field(
        default=None, description="Period information"
    )


class ComponentTreeMeasuresResponse(SonarQubeModel):
    """Response from getting component tree measures.

    Attributes:
        base_component: Base component.
        components: List of child components.
        metrics: List of metrics.
        paging: Paging information.
    """

    base_component: MeasureComponent = Field(
        alias="baseComponent",
        description="Base component",
    )
    components: list[MeasureComponent] = Field(
        default_factory=list,
        description="Child components",
    )
    metrics: Optional[list[dict[str, Any]]] = Field(default=None, description="Metrics")
    paging: Optional[dict[str, Any]] = Field(
        default=None, description="Paging information"
    )


class SearchHistoryResponse(SonarQubeModel):
    """Response from searching measure history.

    Attributes:
        paging: Paging information.
        measures: List of measure histories.
    """

    paging: Optional[dict[str, Any]] = Field(default=None, description="Paging")
    measures: list[dict[str, Any]] = Field(
        default_factory=list, description="Measure histories"
    )
