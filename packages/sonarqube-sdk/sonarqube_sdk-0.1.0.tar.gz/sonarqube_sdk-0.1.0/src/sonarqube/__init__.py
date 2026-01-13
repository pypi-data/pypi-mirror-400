"""SonarQube SDK - A fully-typed Python SDK for SonarQube API.

This package provides a comprehensive, type-safe interface to interact with
SonarQube's REST API. It supports all major API domains including projects,
issues, rules, quality gates, and more.

Example:
    Basic usage with token authentication::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(
            base_url="https://sonarqube.example.com", token="your-token"
        )

        # Search for projects
        projects = client.projects.search(q="backend")
        for project in projects.components:
            print(f"Project: {project.name}")

    Using basic authentication::

        client = SonarQubeClient(
            base_url="https://sonarqube.example.com", username="admin", password="admin"
        )

Attributes:
    __version__: The current version of the SDK.
    __all__: List of public objects exported by this module.
"""

from __future__ import annotations

from sonarqube.client import SonarQubeClient
from sonarqube.exceptions import (
    SonarQubeAPIError,
    SonarQubeAuthenticationError,
    SonarQubeConnectionError,
    SonarQubeError,
    SonarQubeNotFoundError,
    SonarQubePermissionError,
    SonarQubeValidationError,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "SonarQubeClient",
    # Exceptions
    "SonarQubeError",
    "SonarQubeAPIError",
    "SonarQubeAuthenticationError",
    "SonarQubeConnectionError",
    "SonarQubeNotFoundError",
    "SonarQubePermissionError",
    "SonarQubeValidationError",
    # Version
    "__version__",
]
