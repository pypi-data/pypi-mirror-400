"""Custom exceptions for SonarQube SDK.

This module defines the exception hierarchy used throughout the SDK to
provide clear and actionable error information when API calls fail.

Example:
    Handling specific exceptions::

        from sonarqube import SonarQubeClient
        from sonarqube.exceptions import (
            SonarQubeAuthenticationError,
            SonarQubeNotFoundError,
        )

        client = SonarQubeClient(base_url="...", token="...")

        try:
            project = client.projects.search(q="nonexistent")
        except SonarQubeAuthenticationError:
            print("Invalid credentials")
        except SonarQubeNotFoundError:
            print("Resource not found")
"""

from __future__ import annotations

from typing import Any, Optional


class SonarQubeError(Exception):
    """Base exception for all SonarQube SDK errors.

    All other exceptions in this module inherit from this class,
    allowing you to catch all SDK-related errors with a single
    except clause.

    Attributes:
        message: Human-readable error message.
        details: Optional additional error details from the API.

    Example:
        Catching all SDK errors::

            try:
                client.projects.search(q="test")
            except SonarQubeError as e:
                print(f"SDK error: {e.message}")
    """

    def __init__(
        self,
        message: str,
        details: Optional[Any] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            details: Optional additional error details.
        """
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


class SonarQubeAPIError(SonarQubeError):
    """Exception raised when the SonarQube API returns an error response.

    This exception is raised for HTTP 4xx and 5xx responses that don't
    fall into more specific categories.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code from the response.
        errors: List of error objects from the API response.
        details: Raw response data.

    Example:
        Handling API errors::

            try:
                client.projects.create(name="", key="")
            except SonarQubeAPIError as e:
                print(f"API error {e.status_code}: {e.message}")
                for error in e.errors:
                    print(f"  - {error}")
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        errors: Optional[list[dict[str, Any]]] = None,
        details: Optional[Any] = None,
    ) -> None:
        """Initialize the API error exception.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code.
            errors: List of error objects from the API.
            details: Raw response data.
        """
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message, details)

    def __str__(self) -> str:
        """Return string representation of the error."""
        base = f"[{self.status_code}] {self.message}"
        if self.errors:
            error_messages = [e.get("msg", str(e)) for e in self.errors]
            base += f": {'; '.join(error_messages)}"
        return base


class SonarQubeAuthenticationError(SonarQubeAPIError):
    """Exception raised when authentication fails.

    This exception is raised for HTTP 401 responses, indicating
    invalid or missing credentials.

    Example:
        Handling authentication errors::

            try:
                client = SonarQubeClient(
                    base_url="https://sonarqube.example.com", token="invalid-token"
                )
                client.projects.search()
            except SonarQubeAuthenticationError:
                print("Please check your credentials")
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Any] = None,
    ) -> None:
        """Initialize the authentication error.

        Args:
            message: Human-readable error message.
            details: Optional additional error details.
        """
        super().__init__(message, status_code=401, details=details)


class SonarQubePermissionError(SonarQubeAPIError):
    """Exception raised when the user lacks required permissions.

    This exception is raised for HTTP 403 responses, indicating
    the authenticated user doesn't have permission to perform
    the requested action.

    Example:
        Handling permission errors::

            try:
                client.projects.delete(project="protected-project")
            except SonarQubePermissionError:
                print("You don't have permission to delete this project")
    """

    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Any] = None,
    ) -> None:
        """Initialize the permission error.

        Args:
            message: Human-readable error message.
            details: Optional additional error details.
        """
        super().__init__(message, status_code=403, details=details)


class SonarQubeNotFoundError(SonarQubeAPIError):
    """Exception raised when a requested resource is not found.

    This exception is raised for HTTP 404 responses, indicating
    the requested resource doesn't exist.

    Example:
        Handling not found errors::

            try:
                project = client.projects.search(q="nonexistent-project")
            except SonarQubeNotFoundError:
                print("Project not found")
    """

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Any] = None,
    ) -> None:
        """Initialize the not found error.

        Args:
            message: Human-readable error message.
            details: Optional additional error details.
        """
        super().__init__(message, status_code=404, details=details)


class SonarQubeValidationError(SonarQubeAPIError):
    """Exception raised when request validation fails.

    This exception is raised for HTTP 400 responses, indicating
    the request was malformed or contained invalid parameters.

    Example:
        Handling validation errors::

            try:
                client.projects.create(name="", key="invalid key!")
            except SonarQubeValidationError as e:
                print(f"Validation failed: {e.message}")
                for error in e.errors:
                    print(f"  - {error}")
    """

    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[list[dict[str, Any]]] = None,
        details: Optional[Any] = None,
    ) -> None:
        """Initialize the validation error.

        Args:
            message: Human-readable error message.
            errors: List of validation error objects.
            details: Optional additional error details.
        """
        super().__init__(message, status_code=400, errors=errors, details=details)


class SonarQubeConnectionError(SonarQubeError):
    """Exception raised when connection to SonarQube fails.

    This exception is raised when the SDK cannot establish a
    connection to the SonarQube server, such as network errors,
    DNS resolution failures, or timeouts.

    Example:
        Handling connection errors::

            try:
                client = SonarQubeClient(
                    base_url="https://invalid-host.example.com", token="token"
                )
                client.projects.search()
            except SonarQubeConnectionError:
                print("Cannot connect to SonarQube server")
    """

    def __init__(
        self,
        message: str = "Failed to connect to SonarQube",
        details: Optional[Any] = None,
    ) -> None:
        """Initialize the connection error.

        Args:
            message: Human-readable error message.
            details: Optional additional error details.
        """
        super().__init__(message, details)
