"""Main client for SonarQube SDK.

This module provides the main entry point for interacting with the
SonarQube API. The SonarQubeClient class provides access to all API
namespaces through a clean, namespace-based interface.

Example:
    Using the SonarQube client::

        from sonarqube import SonarQubeClient

        # Initialize with token authentication
        client = SonarQubeClient(
            base_url="https://sonarqube.example.com", token="your-token"
        )

        # Access API namespaces
        projects = client.projects.search(q="backend")
        issues = client.issues.search(project_keys=["my-project"])

        # Close when done
        client.close()

    Using as context manager::

        with SonarQubeClient(base_url="...", token="...") as client:
            projects = client.projects.search()
"""

from __future__ import annotations

from typing import Optional

from sonarqube.api.applications import ApplicationsAPI
from sonarqube.api.components import ComponentsAPI
from sonarqube.api.hotspots import HotspotsAPI
from sonarqube.api.issues import IssuesAPI
from sonarqube.api.measures import MeasuresAPI
from sonarqube.api.projects import ProjectsAPI
from sonarqube.api.qualitygates import QualityGatesAPI
from sonarqube.api.qualityprofiles import QualityProfilesAPI
from sonarqube.api.rules import RulesAPI
from sonarqube.api.settings import SettingsAPI
from sonarqube.api.sources import SourcesAPI
from sonarqube.api.system import SystemAPI
from sonarqube.api.user_tokens import UserTokensAPI
from sonarqube.api.users import UsersAPI
from sonarqube.auth import BaseAuth, create_auth
from sonarqube.http import DEFAULT_TIMEOUT, HTTPClient


class SonarQubeClient:
    """Main client for interacting with the SonarQube API.

    This client provides access to all SonarQube API domains through
    namespace properties. Each namespace corresponds to an API domain
    (e.g., projects, issues, rules).

    Example:
        Basic usage::

            from sonarqube import SonarQubeClient

            client = SonarQubeClient(
                base_url="https://sonarqube.example.com", token="your-token"
            )

            # Search for projects
            projects = client.projects.search(q="backend")
            for project in projects.components:
                print(project.name)

            # Get issues for a project
            issues = client.issues.search(
                project_keys=["my-project"], severities=["CRITICAL", "BLOCKER"]
            )
            for issue in issues.issues:
                print(f"{issue.severity}: {issue.message}")

            client.close()

        Using context manager::

            with SonarQubeClient(base_url="...", token="...") as client:
                projects = client.projects.search()

        Using basic authentication::

            client = SonarQubeClient(
                base_url="https://sonarqube.example.com", username="admin", password="admin"
            )
    """

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth: Optional[BaseAuth] = None,
        timeout: float = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the SonarQube client.

        Args:
            base_url: Base URL of the SonarQube instance.
            token: Optional API token for authentication.
            username: Optional username for basic authentication.
            password: Optional password for basic authentication.
            auth: Optional custom authentication handler.
            timeout: Request timeout in seconds.
            verify_ssl: Whether to verify SSL certificates.

        Raises:
            ValueError: If no authentication is provided or if
                username is provided without password.

        Example:
            Token authentication::

                client = SonarQubeClient(
                    base_url="https://sonarqube.example.com", token="squ_abcdef123456"
                )

            Basic authentication::

                client = SonarQubeClient(
                    base_url="https://sonarqube.example.com", username="admin", password="admin"
                )

            Custom authentication::

                from sonarqube.auth import TokenAuth

                auth = TokenAuth(token="my-token")
                client = SonarQubeClient(base_url="https://sonarqube.example.com", auth=auth)
        """
        self.base_url = base_url.rstrip("/")

        # Create authentication handler
        if auth is None:
            auth = create_auth(token=token, username=username, password=password)

        # Create HTTP client
        self._http_client = HTTPClient(
            base_url=self.base_url,
            auth=auth,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        # Initialize API namespaces (lazy initialization)
        self._applications: Optional[ApplicationsAPI] = None
        self._components: Optional[ComponentsAPI] = None
        self._hotspots: Optional[HotspotsAPI] = None
        self._issues: Optional[IssuesAPI] = None
        self._measures: Optional[MeasuresAPI] = None
        self._projects: Optional[ProjectsAPI] = None
        self._qualitygates: Optional[QualityGatesAPI] = None
        self._qualityprofiles: Optional[QualityProfilesAPI] = None
        self._rules: Optional[RulesAPI] = None
        self._settings: Optional[SettingsAPI] = None
        self._sources: Optional[SourcesAPI] = None
        self._system: Optional[SystemAPI] = None
        self._users: Optional[UsersAPI] = None
        self._user_tokens: Optional[UserTokensAPI] = None

    def close(self) -> None:
        """Close the client and release resources.

        Example:
            >>> client = SonarQubeClient(base_url="...", token="...")
            >>> # ... use client ...
            >>> client.close()
        """
        self._http_client.close()

    def __enter__(self) -> SonarQubeClient:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: object,
    ) -> None:
        """Exit context manager and close client."""
        self.close()

    # API Namespace Properties

    @property
    def applications(self) -> ApplicationsAPI:
        """Access the Applications API.

        Returns:
            ApplicationsAPI instance for managing applications.

        Example:
            >>> app = client.applications.create(name="My Application", key="my-app")
        """
        if self._applications is None:
            self._applications = ApplicationsAPI(self._http_client)
        return self._applications

    @property
    def components(self) -> ComponentsAPI:
        """Access the Components API.

        Returns:
            ComponentsAPI instance for searching components.

        Example:
            >>> component = client.components.show(component="my-project")
        """
        if self._components is None:
            self._components = ComponentsAPI(self._http_client)
        return self._components

    @property
    def hotspots(self) -> HotspotsAPI:
        """Access the Hotspots API.

        Returns:
            HotspotsAPI instance for managing security hotspots.

        Example:
            >>> hotspots = client.hotspots.search(project_key="my-project")
        """
        if self._hotspots is None:
            self._hotspots = HotspotsAPI(self._http_client)
        return self._hotspots

    @property
    def issues(self) -> IssuesAPI:
        """Access the Issues API.

        Returns:
            IssuesAPI instance for managing issues.

        Example:
            >>> issues = client.issues.search(
            ...     project_keys=["my-project"], severities=["CRITICAL"]
            ... )
        """
        if self._issues is None:
            self._issues = IssuesAPI(self._http_client)
        return self._issues

    @property
    def measures(self) -> MeasuresAPI:
        """Access the Measures API.

        Returns:
            MeasuresAPI instance for getting measures.

        Example:
            >>> measures = client.measures.component(
            ...     component="my-project", metric_keys=["coverage", "bugs"]
            ... )
        """
        if self._measures is None:
            self._measures = MeasuresAPI(self._http_client)
        return self._measures

    @property
    def projects(self) -> ProjectsAPI:
        """Access the Projects API.

        Returns:
            ProjectsAPI instance for managing projects.

        Example:
            >>> projects = client.projects.search(q="backend")
            >>> for project in projects.components:
            ...     print(project.name)
        """
        if self._projects is None:
            self._projects = ProjectsAPI(self._http_client)
        return self._projects

    @property
    def qualitygates(self) -> QualityGatesAPI:
        """Access the Quality Gates API.

        Returns:
            QualityGatesAPI instance for managing quality gates.

        Example:
            >>> status = client.qualitygates.project_status(project_key="my-project")
            >>> print(status.project_status.status)
        """
        if self._qualitygates is None:
            self._qualitygates = QualityGatesAPI(self._http_client)
        return self._qualitygates

    @property
    def qualityprofiles(self) -> QualityProfilesAPI:
        """Access the Quality Profiles API.

        Returns:
            QualityProfilesAPI instance for managing quality profiles.

        Example:
            >>> profiles = client.qualityprofiles.search(language="py")
            >>> for profile in profiles.profiles:
            ...     print(profile.name)
        """
        if self._qualityprofiles is None:
            self._qualityprofiles = QualityProfilesAPI(self._http_client)
        return self._qualityprofiles

    @property
    def rules(self) -> RulesAPI:
        """Access the Rules API.

        Returns:
            RulesAPI instance for managing rules.

        Example:
            >>> rules = client.rules.search(languages=["py"])
            >>> for rule in rules.rules:
            ...     print(rule.name)
        """
        if self._rules is None:
            self._rules = RulesAPI(self._http_client)
        return self._rules

    @property
    def settings(self) -> SettingsAPI:
        """Access the Settings API.

        Returns:
            SettingsAPI instance for managing settings.

        Example:
            >>> settings = client.settings.values(keys=["sonar.core.serverBaseURL"])
        """
        if self._settings is None:
            self._settings = SettingsAPI(self._http_client)
        return self._settings

    @property
    def sources(self) -> SourcesAPI:
        """Access the Sources API.

        Returns:
            SourcesAPI instance for getting source code.

        Example:
            >>> sources = client.sources.lines(key="my-project:src/main.py")
        """
        if self._sources is None:
            self._sources = SourcesAPI(self._http_client)
        return self._sources

    @property
    def system(self) -> SystemAPI:
        """Access the System API.

        Returns:
            SystemAPI instance for system information.

        Example:
            >>> status = client.system.status()
            >>> print(f"SonarQube {status.version}")
        """
        if self._system is None:
            self._system = SystemAPI(self._http_client)
        return self._system

    @property
    def users(self) -> UsersAPI:
        """Access the Users API.

        Returns:
            UsersAPI instance for managing users.

        Example:
            >>> users = client.users.search(q="john")
        """
        if self._users is None:
            self._users = UsersAPI(self._http_client)
        return self._users

    @property
    def user_tokens(self) -> UserTokensAPI:
        """Access the User Tokens API.

        Returns:
            UserTokensAPI instance for managing user tokens.

        Example:
            >>> token = client.user_tokens.generate(name="ci-token")
        """
        if self._user_tokens is None:
            self._user_tokens = UserTokensAPI(self._http_client)
        return self._user_tokens
