"""Quality Gates API for SonarQube SDK.

This module provides methods to manage SonarQube quality gates.

Example:
    Using the Quality Gates API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # List quality gates
        gates = client.qualitygates.list()
        for gate in gates.qualitygates:
            print(gate.name)

        # Check project status
        status = client.qualitygates.project_status(project_key="my-project")
        print(f"Status: {status.project_status.status}")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.qualitygates import (
    CreateConditionResponse,
    ProjectStatusResponse,
    QualityGateCreateResponse,
    QualityGateListResponse,
    QualityGateShowResponse,
    SearchProjectsResponse,
)


class QualityGatesAPI(BaseAPI):
    """API for managing SonarQube quality gates.

    Quality gates are conditions that must be met for a project to pass.
    This API provides methods to create, update, and manage quality gates.

    Attributes:
        API_PATH: Base path for quality gates API ("/api/qualitygates").

    Example:
        Using the quality gates API::

            # List quality gates
            gates = client.qualitygates.list()

            # Check project status
            status = client.qualitygates.project_status(project_key="my-project")
    """

    API_PATH = "/api/qualitygates"

    def copy(self, source_name: str, name: str) -> QualityGateCreateResponse:
        """Copy a quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            source_name: Source quality gate name.
            name: Name for the new quality gate.

        Returns:
            Response containing the new quality gate.

        Example:
            >>> gate = client.qualitygates.copy(source_name="Sonar way", name="My Quality Gate")
        """
        return self._post_model(
            "/copy",
            QualityGateCreateResponse,
            data={
                "sourceName": source_name,
                "name": name,
            },
        )

    def create(self, name: str) -> QualityGateCreateResponse:
        """Create a new quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            name: Quality gate name.

        Returns:
            Response containing the created quality gate.

        Example:
            >>> gate = client.qualitygates.create(name="My Quality Gate")
            >>> print(gate.id)
        """
        return self._post_model(
            "/create",
            QualityGateCreateResponse,
            data={"name": name},
        )

    def create_condition(
        self,
        gate_name: str,
        metric: str,
        error: str,
        op: Optional[str] = None,
    ) -> CreateConditionResponse:
        """Create a condition on a quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            gate_name: Quality gate name.
            metric: Metric key.
            error: Error threshold.
            op: Operator (LT, GT).

        Returns:
            Response containing the created condition.

        Example:
            >>> condition = client.qualitygates.create_condition(
            ...     gate_name="My Quality Gate", metric="new_coverage", op="LT", error="80"
            ... )
        """
        data: dict[str, Any] = {
            "gateName": gate_name,
            "metric": metric,
            "error": error,
        }
        if op:
            data["op"] = op

        return self._post_model("/create_condition", CreateConditionResponse, data=data)

    def delete_condition(self, id: int) -> None:  # noqa: A002
        """Delete a condition from a quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            id: Condition ID.

        Example:
            >>> client.qualitygates.delete_condition(id=123)
        """
        self._post("/delete_condition", data={"id": id})

    def deselect(
        self,
        project_key: Optional[str] = None,
    ) -> None:
        """Remove quality gate from a project.

        Requires 'Administer' permission on the project.

        Args:
            project_key: Project key.

        Example:
            >>> client.qualitygates.deselect(project_key="my-project")
        """
        data: dict[str, Any] = {}
        if project_key:
            data["projectKey"] = project_key

        self._post("/deselect", data=data)

    def destroy(self, name: str) -> None:
        """Delete a quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            name: Quality gate name.

        Example:
            >>> client.qualitygates.destroy(name="My Quality Gate")
        """
        self._post("/destroy", data={"name": name})

    def get_by_project(self, project: str) -> dict[str, Any]:
        """Get the quality gate for a project.

        Requires 'Browse' permission on the project.

        Args:
            project: Project key.

        Returns:
            Dictionary containing quality gate information.

        Example:
            >>> gate = client.qualitygates.get_by_project(project="my-project")
        """
        return self._get("/get_by_project", params={"project": project})

    def list(self) -> QualityGateListResponse:
        """List all quality gates.

        Returns:
            Response containing list of quality gates.

        Example:
            >>> response = client.qualitygates.list()
            >>> for gate in response.qualitygates:
            ...     print(gate.name)
        """
        return self._get_model("/list", QualityGateListResponse)

    def project_status(
        self,
        analysis_id: Optional[str] = None,
        branch: Optional[str] = None,
        project_id: Optional[str] = None,
        project_key: Optional[str] = None,
        pull_request: Optional[str] = None,
    ) -> ProjectStatusResponse:
        """Get quality gate status for a project.

        Requires 'Browse' permission on the project.

        Args:
            analysis_id: Analysis ID.
            branch: Branch name.
            project_id: Project ID.
            project_key: Project key.
            pull_request: Pull request ID.

        Returns:
            Response containing project status.

        Example:
            >>> status = client.qualitygates.project_status(project_key="my-project")
            >>> if status.project_status.status == "OK":
            ...     print("Quality gate passed!")
        """
        return self._get_model(
            "/project_status",
            ProjectStatusResponse,
            params={
                "analysisId": analysis_id,
                "branch": branch,
                "projectId": project_id,
                "projectKey": project_key,
                "pullRequest": pull_request,
            },
        )

    def rename(self, current_name: str, name: str) -> None:
        """Rename a quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            current_name: Current quality gate name.
            name: New name.

        Example:
            >>> client.qualitygates.rename(current_name="Old Name", name="New Name")
        """
        self._post(
            "/rename",
            data={
                "currentName": current_name,
                "name": name,
            },
        )

    def search(
        self,
        gate_name: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        query: Optional[str] = None,
        selected: Optional[str] = None,
    ) -> SearchProjectsResponse:
        """Search projects associated with a quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            gate_name: Quality gate name.
            page: Page number.
            page_size: Page size.
            query: Search query.
            selected: Filter selection (all, selected, deselected).

        Returns:
            Response containing projects.

        Example:
            >>> response = client.qualitygates.search(gate_name="Sonar way")
        """
        return self._get_model(
            "/search",
            SearchProjectsResponse,
            params={
                "gateName": gate_name,
                "page": page,
                "pageSize": page_size,
                "query": query,
                "selected": selected,
            },
        )

    def select(
        self,
        gate_name: str,
        project_key: Optional[str] = None,
    ) -> None:
        """Associate a project with a quality gate.

        Requires 'Administer' permission on the project.

        Args:
            gate_name: Quality gate name.
            project_key: Project key.

        Example:
            >>> client.qualitygates.select(gate_name="Sonar way", project_key="my-project")
        """
        data: dict[str, Any] = {"gateName": gate_name}
        if project_key:
            data["projectKey"] = project_key

        self._post("/select", data=data)

    def set_as_default(self, name: str) -> None:
        """Set a quality gate as the default.

        Requires 'Administer Quality Gates' permission.

        Args:
            name: Quality gate name.

        Example:
            >>> client.qualitygates.set_as_default(name="My Quality Gate")
        """
        self._post("/set_as_default", data={"name": name})

    def show(
        self,
        name: Optional[str] = None,
    ) -> QualityGateShowResponse:
        """Get quality gate details.

        Args:
            name: Quality gate name.

        Returns:
            Response containing quality gate details.

        Example:
            >>> gate = client.qualitygates.show(name="Sonar way")
            >>> print(gate.name)
        """
        return self._get_model(
            "/show",
            QualityGateShowResponse,
            params={"name": name},
        )

    def update_condition(
        self,
        id: int,  # noqa: A002
        error: str,
        metric: str,
        op: Optional[str] = None,
    ) -> None:
        """Update a condition on a quality gate.

        Requires 'Administer Quality Gates' permission.

        Args:
            id: Condition ID.
            error: Error threshold.
            metric: Metric key.
            op: Operator (LT, GT).

        Example:
            >>> client.qualitygates.update_condition(id=123, metric="new_coverage", error="85")
        """
        data: dict[str, Any] = {
            "id": id,
            "error": error,
            "metric": metric,
        }
        if op:
            data["op"] = op

        self._post("/update_condition", data=data)
