"""Base API class for SonarQube SDK.

This module provides the base class that all API namespace classes
inherit from. It provides common functionality for making API requests.

Example:
    Creating a custom API namespace::

        from sonarqube.api.base import BaseAPI


        class CustomAPI(BaseAPI):
            API_PATH = "/api/custom"

            def get_items(self) -> dict:
                return self._get("/items")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from sonarqube.http import HTTPClient

T = TypeVar("T", bound=BaseModel)


class BaseAPI:
    """Base class for all API namespace classes.

    This class provides common functionality for making HTTP requests
    to the SonarQube API. All API domain classes (like ApplicationsAPI,
    ProjectsAPI, etc.) inherit from this class.

    Example:
        Using in a subclass::

            class ProjectsAPI(BaseAPI):
                API_PATH = "/api/projects"

                def search(self, q: Optional[str] = None) -> ProjectSearchResponse:
                    return self._get_model(
                        "/search", ProjectSearchResponse, params={"q": q}
                    )
    """

    API_PATH: str = ""

    def __init__(self, client: HTTPClient) -> None:
        """Initialize the API namespace.

        Args:
            client: HTTP client for making requests.
        """
        self._client = client

    def _build_path(self, endpoint: str) -> str:
        """Build full API path from endpoint.

        Args:
            endpoint: Endpoint path relative to API_PATH.

        Returns:
            Full API path.

        Example:
            >>> api = ProjectsAPI(client)
            >>> api._build_path("/search")
            '/api/projects/search'
        """
        return f"{self.API_PATH}{endpoint}"

    def _get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a GET request to the API.

        Args:
            endpoint: Endpoint path relative to API_PATH.
            params: Optional query parameters.

        Returns:
            Parsed JSON response data.

        Example:
            >>> data = api._get("/search", params={"q": "test"})
        """
        return self._client.get(self._build_path(endpoint), params=params)

    def _post(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a POST request to the API.

        Args:
            endpoint: Endpoint path relative to API_PATH.
            params: Optional query parameters.
            data: Optional form data.

        Returns:
            Parsed JSON response data.

        Example:
            >>> data = api._post("/create", data={"name": "Test"})
        """
        return self._client.post(self._build_path(endpoint), params=params, data=data)

    def _get_model(
        self,
        endpoint: str,
        response_model: type[T],
        params: Optional[dict[str, Any]] = None,
    ) -> T:
        """Make a GET request and deserialize to a Pydantic model.

        Args:
            endpoint: Endpoint path relative to API_PATH.
            response_model: Pydantic model class for response.
            params: Optional query parameters.

        Returns:
            Deserialized response as Pydantic model.

        Example:
            >>> response = api._get_model("/search", ProjectSearchResponse)
        """
        return self._client.get_model(
            self._build_path(endpoint),
            response_model,
            params=params,
        )

    def _post_model(
        self,
        endpoint: str,
        response_model: type[T],
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> T:
        """Make a POST request and deserialize to a Pydantic model.

        Args:
            endpoint: Endpoint path relative to API_PATH.
            response_model: Pydantic model class for response.
            params: Optional query parameters.
            data: Optional form data.

        Returns:
            Deserialized response as Pydantic model.

        Example:
            >>> response = api._post_model(
            ...     "/create", ProjectCreateResponse, data={"name": "Test"}
            ... )
        """
        return self._client.post_model(
            self._build_path(endpoint),
            response_model,
            params=params,
            data=data,
        )
