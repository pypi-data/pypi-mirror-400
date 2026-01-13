"""System API for SonarQube SDK.

This module provides methods to get system information and status.

Example:
    Using the System API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Get system status
        status = client.system.status()
        print(f"SonarQube {status.version}")
"""

from __future__ import annotations

from typing import Any

from sonarqube.api.base import BaseAPI
from sonarqube.models.system import (
    SystemHealth,
    SystemStatus,
    SystemUpgradesResponse,
)


class SystemAPI(BaseAPI):
    """API for getting SonarQube system information.

    Attributes:
        API_PATH: Base path for system API ("/api/system").
    """

    API_PATH = "/api/system"

    def db_migration_status(self) -> dict[str, Any]:
        """Get database migration status.

        Returns:
            Dictionary containing migration status.

        Example:
            >>> status = client.system.db_migration_status()
        """
        return self._get("/db_migration_status")

    def health(self) -> SystemHealth:
        """Get system health status.

        Requires 'Administer System' permission or system passcode.

        Returns:
            System health status.

        Example:
            >>> health = client.system.health()
            >>> if health.health == "GREEN":
            ...     print("System is healthy!")
        """
        return self._get_model("/health", SystemHealth)

    def info(self) -> dict[str, Any]:
        """Get detailed system information.

        Requires 'Administer System' permission.

        Returns:
            Dictionary containing detailed system info.

        Example:
            >>> info = client.system.info()
        """
        return self._get("/info")

    def liveness(self) -> None:
        """Check if system is alive.

        Returns 204 No Content if system is alive.

        Example:
            >>> client.system.liveness()
        """
        self._get("/liveness")

    def ping(self) -> str:
        """Ping the system.

        Returns:
            "pong" if system is reachable.

        Example:
            >>> result = client.system.ping()
            >>> assert result == "pong"
        """
        response = self._get("/ping")
        return str(response) if response else "pong"

    def restart(self) -> None:
        """Restart the SonarQube server.

        Requires 'Administer System' permission.

        Example:
            >>> client.system.restart()
        """
        self._post("/restart")

    def status(self) -> SystemStatus:
        """Get system status.

        Returns:
            System status including version.

        Example:
            >>> status = client.system.status()
            >>> print(f"SonarQube {status.version} is {status.status}")
        """
        return self._get_model("/status", SystemStatus)

    def upgrades(self) -> SystemUpgradesResponse:
        """Check for available upgrades.

        Requires 'Administer System' permission.

        Returns:
            Response containing available upgrades.

        Example:
            >>> upgrades = client.system.upgrades()
        """
        return self._get_model("/upgrades", SystemUpgradesResponse)
