"""HTTP client wrapper for SonarQube SDK.

This module provides a configured HTTP client for making requests to
the SonarQube API with proper authentication, error handling, and
retry logic.

Example:
    Using the HTTP client directly::

        from sonarqube.http import HTTPClient
        from sonarqube.auth import TokenAuth

        auth = TokenAuth(token="your-token")
        client = HTTPClient(base_url="https://sonarqube.example.com", auth=auth)

        response = client.get("/api/projects/search", params={"q": "test"})
"""

from __future__ import annotations

import logging
from typing import Any, Optional, TypeVar

import httpx
from pydantic import BaseModel

from sonarqube.auth import BaseAuth
from sonarqube.exceptions import (
    SonarQubeAPIError,
    SonarQubeAuthenticationError,
    SonarQubeConnectionError,
    SonarQubeNotFoundError,
    SonarQubePermissionError,
    SonarQubeValidationError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Default timeout in seconds
DEFAULT_TIMEOUT = 30.0

# Default retry settings
DEFAULT_MAX_RETRIES = 3


class HTTPClient:
    """HTTP client for making requests to SonarQube API.

    This client wraps httpx and provides:
    - Automatic authentication header injection
    - Error handling with specific exception types
    - Response deserialization to Pydantic models
    - Configurable timeout and retry settings

    Attributes:
        base_url: Base URL of the SonarQube instance.
        auth: Authentication handler.
        timeout: Request timeout in seconds.
        client: Underlying httpx client.

    Example:
        Basic usage::

            client = HTTPClient(
                base_url="https://sonarqube.example.com", auth=TokenAuth(token="your-token")
            )

            # GET request
            data = client.get("/api/projects/search")

            # POST request
            data = client.post("/api/projects/create", data={"name": "Test"})
    """

    def __init__(
        self,
        base_url: str,
        auth: Optional[BaseAuth] = None,
        timeout: float = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: Base URL of the SonarQube instance.
            auth: Optional authentication handler.
            timeout: Request timeout in seconds.
            verify_ssl: Whether to verify SSL certificates.

        Example:
            >>> client = HTTPClient(
            ...     base_url="https://sonarqube.example.com",
            ...     auth=TokenAuth(token="token"),
            ...     timeout=60.0,
            ... )
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout

        # Build default headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Add auth headers if auth is provided
        if auth:
            headers.update(auth.get_auth_headers())

        self.client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl,
        )

    def close(self) -> None:
        """Close the HTTP client and release resources.

        Example:
            >>> client = HTTPClient(base_url="https://sonarqube.example.com")
            >>> # ... use client ...
            >>> client.close()
        """
        self.client.close()

    def __enter__(self) -> HTTPClient:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Exit context manager and close client."""
        self.close()

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object.

        Returns:
            Parsed JSON response data.

        Raises:
            SonarQubeAuthenticationError: For 401 responses.
            SonarQubePermissionError: For 403 responses.
            SonarQubeNotFoundError: For 404 responses.
            SonarQubeValidationError: For 400 responses.
            SonarQubeAPIError: For other error responses.
        """
        # Log request details
        logger.debug(
            "Response: %s %s -> %s",
            response.request.method,
            response.request.url,
            response.status_code,
        )

        # Handle successful responses
        if response.is_success:
            if response.status_code == 204:
                return {}
            try:
                result: dict[str, Any] = response.json()
                return result
            except ValueError:
                # Some endpoints return empty responses
                return {}

        # Parse error response
        try:
            error_data = response.json()
            errors = error_data.get("errors", [])
            message = (
                errors[0].get("msg", "Unknown error") if errors else "Unknown error"
            )
        except ValueError:
            error_data = None
            errors = []
            message = response.text or "Unknown error"

        # Raise appropriate exception based on status code
        if response.status_code == 401:
            raise SonarQubeAuthenticationError(message=message, details=error_data)
        if response.status_code == 403:
            raise SonarQubePermissionError(message=message, details=error_data)
        if response.status_code == 404:
            raise SonarQubeNotFoundError(message=message, details=error_data)
        if response.status_code == 400:
            raise SonarQubeValidationError(
                message=message, errors=errors, details=error_data
            )

        raise SonarQubeAPIError(
            message=message,
            status_code=response.status_code,
            errors=errors,
            details=error_data,
        )

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the SonarQube API.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            params: Optional query parameters.
            data: Optional form data for POST requests.
            json_data: Optional JSON data for POST requests.

        Returns:
            Parsed JSON response data.

        Raises:
            SonarQubeConnectionError: If connection fails.
            SonarQubeAPIError: If API returns an error.

        Example:
            >>> response = client.request("GET", "/api/projects/search", params={"q": "test"})
        """
        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        # Filter out None values from data
        if data:
            data = {k: v for k, v in data.items() if v is not None}

        logger.debug("Request: %s %s params=%s data=%s", method, path, params, data)

        try:
            response = self.client.request(
                method=method,
                url=path,
                params=params,
                data=data,
                json=json_data,
            )
        except httpx.ConnectError as e:
            raise SonarQubeConnectionError(
                message=f"Failed to connect to {self.base_url}",
                details=str(e),
            ) from e
        except httpx.TimeoutException as e:
            raise SonarQubeConnectionError(
                message=f"Request timed out after {self.timeout}s",
                details=str(e),
            ) from e
        except httpx.HTTPError as e:
            raise SonarQubeConnectionError(
                message="HTTP error occurred",
                details=str(e),
            ) from e

        return self._handle_response(response)

    def get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a GET request.

        Args:
            path: API endpoint path.
            params: Optional query parameters.

        Returns:
            Parsed JSON response data.

        Example:
            >>> projects = client.get("/api/projects/search", params={"q": "test"})
        """
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a POST request.

        Args:
            path: API endpoint path.
            params: Optional query parameters.
            data: Optional form data.

        Returns:
            Parsed JSON response data.

        Example:
            >>> result = client.post(
            ...     "/api/projects/create", data={"name": "My Project", "project": "my-project"}
            ... )
        """
        return self.request("POST", path, params=params, data=data)

    def request_model(
        self,
        method: str,
        path: str,
        response_model: type[T],
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> T:
        """Make a request and deserialize response to a Pydantic model.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            response_model: Pydantic model class for response.
            params: Optional query parameters.
            data: Optional form data for POST requests.

        Returns:
            Deserialized response as Pydantic model.

        Example:
            >>> from sonarqube.models.projects import ProjectSearchResponse
            >>> response = client.request_model(
            ...     "GET", "/api/projects/search", ProjectSearchResponse, params={"q": "test"}
            ... )
            >>> for project in response.components:
            ...     print(project.name)
        """
        response_data = self.request(method, path, params=params, data=data)
        return response_model.model_validate(response_data)

    def get_model(
        self,
        path: str,
        response_model: type[T],
        params: Optional[dict[str, Any]] = None,
    ) -> T:
        """Make a GET request and deserialize to a Pydantic model.

        Args:
            path: API endpoint path.
            response_model: Pydantic model class for response.
            params: Optional query parameters.

        Returns:
            Deserialized response as Pydantic model.
        """
        return self.request_model("GET", path, response_model, params=params)

    def post_model(
        self,
        path: str,
        response_model: type[T],
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> T:
        """Make a POST request and deserialize to a Pydantic model.

        Args:
            path: API endpoint path.
            response_model: Pydantic model class for response.
            params: Optional query parameters.
            data: Optional form data.

        Returns:
            Deserialized response as Pydantic model.
        """
        return self.request_model(
            "POST", path, response_model, params=params, data=data
        )
