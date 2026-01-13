"""API namespace modules for SonarQube SDK.

Each module in this package represents a SonarQube API domain and provides
methods to interact with the corresponding endpoints.
"""

from __future__ import annotations

from sonarqube.api.base import BaseAPI

__all__ = [
    "BaseAPI",
]
