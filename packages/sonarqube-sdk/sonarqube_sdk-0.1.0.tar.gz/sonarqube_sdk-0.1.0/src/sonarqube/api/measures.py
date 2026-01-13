"""Measures API for SonarQube SDK.

This module provides methods to get measures and metrics from SonarQube.

Example:
    Using the Measures API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Get component measures
        measures = client.measures.component(
            component="my-project", metric_keys=["coverage", "bugs", "vulnerabilities"]
        )
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.measures import (
    ComponentMeasuresResponse,
    ComponentTreeMeasuresResponse,
    SearchHistoryResponse,
)


class MeasuresAPI(BaseAPI):
    """API for getting SonarQube measures.

    Attributes:
        API_PATH: Base path for measures API ("/api/measures").
    """

    API_PATH = "/api/measures"

    def component(
        self,
        component: str,
        metric_keys: list[str],
        additional_fields: Optional[list[str]] = None,
        branch: Optional[str] = None,
        pull_request: Optional[str] = None,
    ) -> ComponentMeasuresResponse:
        """Get measures for a component.

        Requires 'Browse' permission on the project.

        Args:
            component: Component key.
            metric_keys: List of metric keys.
            additional_fields: Additional fields to return.
            branch: Branch name.
            pull_request: Pull request ID.

        Returns:
            Response containing component measures.

        Example:
            >>> measures = client.measures.component(
            ...     component="my-project", metric_keys=["coverage", "bugs"]
            ... )
            >>> for measure in measures.component.measures:
            ...     print(f"{measure.metric}: {measure.value}")
        """
        params: dict[str, Any] = {
            "component": component,
            "metricKeys": ",".join(metric_keys),
        }

        if additional_fields:
            params["additionalFields"] = ",".join(additional_fields)
        if branch:
            params["branch"] = branch
        if pull_request:
            params["pullRequest"] = pull_request

        return self._get_model("/component", ComponentMeasuresResponse, params=params)

    def component_tree(
        self,
        component: str,
        metric_keys: list[str],
        additional_fields: Optional[list[str]] = None,
        asc: Optional[bool] = None,
        branch: Optional[str] = None,
        metric_period_sort: Optional[str] = None,
        metric_sort: Optional[str] = None,
        metric_sort_filter: Optional[str] = None,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        pull_request: Optional[str] = None,
        q: Optional[str] = None,
        qualifiers: Optional[list[str]] = None,
        s: Optional[str] = None,
        strategy: Optional[str] = None,
    ) -> ComponentTreeMeasuresResponse:
        """Get measures for a component tree.

        Requires 'Browse' permission on the project.

        Args:
            component: Component key.
            metric_keys: List of metric keys.
            additional_fields: Additional fields to return.
            asc: Ascending sort order.
            branch: Branch name.
            metric_period_sort: Metric to use for sorting.
            metric_sort: Metric to sort by.
            metric_sort_filter: Metric sort filter.
            p: Page number.
            ps: Page size.
            pull_request: Pull request ID.
            q: Search query.
            qualifiers: Component qualifiers to filter.
            s: Sort field.
            strategy: Tree strategy (all, children, leaves).

        Returns:
            Response containing component tree measures.

        Example:
            >>> tree = client.measures.component_tree(
            ...     component="my-project", metric_keys=["coverage"], qualifiers=["FIL"]
            ... )
            >>> for comp in tree.components:
            ...     print(f"{comp.path}: {comp.measures}")
        """
        params: dict[str, Any] = {
            "component": component,
            "metricKeys": ",".join(metric_keys),
        }

        if additional_fields:
            params["additionalFields"] = ",".join(additional_fields)
        if asc is not None:
            params["asc"] = str(asc).lower()
        if branch:
            params["branch"] = branch
        if metric_period_sort:
            params["metricPeriodSort"] = metric_period_sort
        if metric_sort:
            params["metricSort"] = metric_sort
        if metric_sort_filter:
            params["metricSortFilter"] = metric_sort_filter
        if p:
            params["p"] = p
        if ps:
            params["ps"] = ps
        if pull_request:
            params["pullRequest"] = pull_request
        if q:
            params["q"] = q
        if qualifiers:
            params["qualifiers"] = ",".join(qualifiers)
        if s:
            params["s"] = s
        if strategy:
            params["strategy"] = strategy

        return self._get_model(
            "/component_tree", ComponentTreeMeasuresResponse, params=params
        )

    def search_history(
        self,
        component: str,
        metrics: list[str],
        branch: Optional[str] = None,
        from_date: Optional[str] = None,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        pull_request: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> SearchHistoryResponse:
        """Search measure history for a component.

        Requires 'Browse' permission on the project.

        Args:
            component: Component key.
            metrics: List of metric keys.
            branch: Branch name.
            from_date: Start date.
            p: Page number.
            ps: Page size.
            pull_request: Pull request ID.
            to_date: End date.

        Returns:
            Response containing measure history.

        Example:
            >>> history = client.measures.search_history(
            ...     component="my-project", metrics=["coverage"]
            ... )
        """
        params: dict[str, Any] = {
            "component": component,
            "metrics": ",".join(metrics),
        }

        if branch:
            params["branch"] = branch
        if from_date:
            params["from"] = from_date
        if p:
            params["p"] = p
        if ps:
            params["ps"] = ps
        if pull_request:
            params["pullRequest"] = pull_request
        if to_date:
            params["to"] = to_date

        return self._get_model("/search_history", SearchHistoryResponse, params=params)
