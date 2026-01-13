"""Quality Profiles API for SonarQube SDK.

This module provides methods to manage SonarQube quality profiles.

Example:
    Using the Quality Profiles API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # List quality profiles
        profiles = client.qualityprofiles.search()
        for profile in profiles.profiles:
            print(f"{profile.name} ({profile.language})")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.qualityprofiles import (
    QualityProfileChangelogResponse,
    QualityProfileCreateResponse,
    QualityProfileInheritanceResponse,
    QualityProfileProjectsResponse,
    QualityProfileSearchResponse,
    QualityProfileShowResponse,
)


class QualityProfilesAPI(BaseAPI):
    """API for managing SonarQube quality profiles.

    Quality profiles are collections of rules that define coding standards
    for a specific language. This API provides methods to create, update,
    and manage quality profiles.

    Attributes:
        API_PATH: Base path for quality profiles API ("/api/qualityprofiles").

    Example:
        Using the quality profiles API::

            # Search quality profiles
            profiles = client.qualityprofiles.search(language="py")

            # Activate a rule
            client.qualityprofiles.activate_rule(
                key="py-my-profile-12345", rule="python:S1234"
            )
    """

    API_PATH = "/api/qualityprofiles"

    def activate_rule(
        self,
        key: str,
        rule: str,
        params: Optional[str] = None,
        reset: Optional[bool] = None,
        severity: Optional[str] = None,
    ) -> None:
        """Activate a rule in a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            key: Quality profile key.
            rule: Rule key.
            params: Activation parameters.
            reset: Reset to default values.
            severity: Rule severity.

        Example:
            >>> client.qualityprofiles.activate_rule(
            ...     key="py-my-profile-12345", rule="python:S1234", severity="MAJOR"
            ... )
        """
        data: dict[str, Any] = {
            "key": key,
            "rule": rule,
        }
        if params:
            data["params"] = params
        if reset is not None:
            data["reset"] = str(reset).lower()
        if severity:
            data["severity"] = severity

        self._post("/activate_rule", data=data)

    def activate_rules(
        self,
        target_key: str,
        active_severities: Optional[list[str]] = None,
        asc: Optional[bool] = None,
        available_since: Optional[str] = None,
        inheritance: Optional[list[str]] = None,
        is_template: Optional[bool] = None,
        languages: Optional[list[str]] = None,
        q: Optional[str] = None,
        qprofile: Optional[str] = None,
        repositories: Optional[list[str]] = None,
        rule_key: Optional[str] = None,
        s: Optional[str] = None,
        severities: Optional[list[str]] = None,
        statuses: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        target_severity: Optional[str] = None,
        template_key: Optional[str] = None,
        types: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Bulk activate rules in a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            target_key: Target quality profile key.
            active_severities: Filter by active severities.
            asc: Ascending sort order.
            available_since: Filter by availability date.
            inheritance: Filter by inheritance.
            is_template: Filter template rules.
            languages: Filter by languages.
            q: Search query.
            qprofile: Source quality profile key.
            repositories: Filter by repositories.
            rule_key: Filter by rule key.
            s: Sort field.
            severities: Filter by severities.
            statuses: Filter by statuses.
            tags: Filter by tags.
            target_severity: Severity to set on activated rules.
            template_key: Filter by template key.
            types: Filter by types.

        Returns:
            Response containing activation results.

        Example:
            >>> result = client.qualityprofiles.activate_rules(
            ...     target_key="py-my-profile-12345", languages=["py"]
            ... )
        """
        data: dict[str, Any] = {"targetKey": target_key}

        if active_severities:
            data["active_severities"] = ",".join(active_severities)
        if asc is not None:
            data["asc"] = str(asc).lower()
        if available_since:
            data["available_since"] = available_since
        if inheritance:
            data["inheritance"] = ",".join(inheritance)
        if is_template is not None:
            data["is_template"] = str(is_template).lower()
        if languages:
            data["languages"] = ",".join(languages)
        if q:
            data["q"] = q
        if qprofile:
            data["qprofile"] = qprofile
        if repositories:
            data["repositories"] = ",".join(repositories)
        if rule_key:
            data["rule_key"] = rule_key
        if s:
            data["s"] = s
        if severities:
            data["severities"] = ",".join(severities)
        if statuses:
            data["statuses"] = ",".join(statuses)
        if tags:
            data["tags"] = ",".join(tags)
        if target_severity:
            data["targetSeverity"] = target_severity
        if template_key:
            data["template_key"] = template_key
        if types:
            data["types"] = ",".join(types)

        return self._post("/activate_rules", data=data)

    def add_project(self, key: str, project: str) -> None:
        """Associate a project with a quality profile.

        Requires 'Administer' permission on the project.

        Args:
            key: Quality profile key.
            project: Project key.

        Example:
            >>> client.qualityprofiles.add_project(
            ...     key="py-my-profile-12345", project="my-project"
            ... )
        """
        self._post(
            "/add_project",
            data={
                "key": key,
                "project": project,
            },
        )

    def backup(self, language: str, quality_profile: str) -> str:
        """Backup a quality profile as XML.

        Requires 'Administer Quality Profiles' permission.

        Args:
            language: Language key.
            quality_profile: Quality profile name.

        Returns:
            XML backup content.

        Example:
            >>> backup = client.qualityprofiles.backup(
            ...     language="py", quality_profile="My Profile"
            ... )
        """
        response = self._get(
            "/backup",
            params={
                "language": language,
                "qualityProfile": quality_profile,
            },
        )
        return str(response)

    def changelog(
        self,
        language: Optional[str] = None,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        quality_profile: Optional[str] = None,
        since: Optional[str] = None,
        to: Optional[str] = None,
    ) -> QualityProfileChangelogResponse:
        """Get changelog for a quality profile.

        Requires 'Browse' permission on the quality profile.

        Args:
            language: Language key.
            p: Page number.
            ps: Page size.
            quality_profile: Quality profile name.
            since: Start date for changelog.
            to: End date for changelog.

        Returns:
            Response containing changelog entries.

        Example:
            >>> changelog = client.qualityprofiles.changelog(
            ...     language="py", quality_profile="My Profile"
            ... )
        """
        return self._get_model(
            "/changelog",
            QualityProfileChangelogResponse,
            params={
                "language": language,
                "p": p,
                "ps": ps,
                "qualityProfile": quality_profile,
                "since": since,
                "to": to,
            },
        )

    def change_parent(
        self,
        language: str,
        quality_profile: str,
        parent_quality_profile: Optional[str] = None,
    ) -> None:
        """Change parent of a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            language: Language key.
            quality_profile: Quality profile name.
            parent_quality_profile: Parent quality profile name.

        Example:
            >>> client.qualityprofiles.change_parent(
            ...     language="py",
            ...     quality_profile="My Profile",
            ...     parent_quality_profile="Sonar way",
            ... )
        """
        data: dict[str, Any] = {
            "language": language,
            "qualityProfile": quality_profile,
        }
        if parent_quality_profile:
            data["parentQualityProfile"] = parent_quality_profile

        self._post("/change_parent", data=data)

    def copy(self, from_key: str, to_name: str) -> QualityProfileCreateResponse:
        """Copy a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            from_key: Source quality profile key.
            to_name: Name for the new profile.

        Returns:
            Response containing the new quality profile.

        Example:
            >>> profile = client.qualityprofiles.copy(
            ...     from_key="py-sonar-way-12345", to_name="My Custom Profile"
            ... )
        """
        return self._post_model(
            "/copy",
            QualityProfileCreateResponse,
            data={
                "fromKey": from_key,
                "toName": to_name,
            },
        )

    def create(
        self,
        language: str,
        name: str,
    ) -> QualityProfileCreateResponse:
        """Create a new quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            language: Language key.
            name: Quality profile name.

        Returns:
            Response containing the created profile.

        Example:
            >>> profile = client.qualityprofiles.create(language="py", name="My Custom Profile")
        """
        return self._post_model(
            "/create",
            QualityProfileCreateResponse,
            data={
                "language": language,
                "name": name,
            },
        )

    def deactivate_rule(self, key: str, rule: str) -> None:
        """Deactivate a rule in a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            key: Quality profile key.
            rule: Rule key.

        Example:
            >>> client.qualityprofiles.deactivate_rule(
            ...     key="py-my-profile-12345", rule="python:S1234"
            ... )
        """
        self._post(
            "/deactivate_rule",
            data={
                "key": key,
                "rule": rule,
            },
        )

    def deactivate_rules(
        self,
        target_key: str,
        active_severities: Optional[list[str]] = None,
        asc: Optional[bool] = None,
        available_since: Optional[str] = None,
        inheritance: Optional[list[str]] = None,
        is_template: Optional[bool] = None,
        languages: Optional[list[str]] = None,
        q: Optional[str] = None,
        qprofile: Optional[str] = None,
        repositories: Optional[list[str]] = None,
        rule_key: Optional[str] = None,
        s: Optional[str] = None,
        severities: Optional[list[str]] = None,
        statuses: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        template_key: Optional[str] = None,
        types: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Bulk deactivate rules in a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            target_key: Target quality profile key.
            active_severities: Filter by active severities.
            asc: Ascending sort order.
            available_since: Filter by availability date.
            inheritance: Filter by inheritance.
            is_template: Filter template rules.
            languages: Filter by languages.
            q: Search query.
            qprofile: Source quality profile key.
            repositories: Filter by repositories.
            rule_key: Filter by rule key.
            s: Sort field.
            severities: Filter by severities.
            statuses: Filter by statuses.
            tags: Filter by tags.
            template_key: Filter by template key.
            types: Filter by types.

        Returns:
            Response containing deactivation results.

        Example:
            >>> result = client.qualityprofiles.deactivate_rules(
            ...     target_key="py-my-profile-12345", tags=["deprecated"]
            ... )
        """
        data: dict[str, Any] = {"targetKey": target_key}

        if active_severities:
            data["active_severities"] = ",".join(active_severities)
        if asc is not None:
            data["asc"] = str(asc).lower()
        if available_since:
            data["available_since"] = available_since
        if inheritance:
            data["inheritance"] = ",".join(inheritance)
        if is_template is not None:
            data["is_template"] = str(is_template).lower()
        if languages:
            data["languages"] = ",".join(languages)
        if q:
            data["q"] = q
        if qprofile:
            data["qprofile"] = qprofile
        if repositories:
            data["repositories"] = ",".join(repositories)
        if rule_key:
            data["rule_key"] = rule_key
        if s:
            data["s"] = s
        if severities:
            data["severities"] = ",".join(severities)
        if statuses:
            data["statuses"] = ",".join(statuses)
        if tags:
            data["tags"] = ",".join(tags)
        if template_key:
            data["template_key"] = template_key
        if types:
            data["types"] = ",".join(types)

        return self._post("/deactivate_rules", data=data)

    def delete(self, language: str, quality_profile: str) -> None:
        """Delete a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            language: Language key.
            quality_profile: Quality profile name.

        Example:
            >>> client.qualityprofiles.delete(language="py", quality_profile="My Profile")
        """
        self._post(
            "/delete",
            data={
                "language": language,
                "qualityProfile": quality_profile,
            },
        )

    def inheritance(
        self,
        language: str,
        quality_profile: str,
    ) -> QualityProfileInheritanceResponse:
        """Get inheritance information for a quality profile.

        Args:
            language: Language key.
            quality_profile: Quality profile name.

        Returns:
            Response containing inheritance information.

        Example:
            >>> inheritance = client.qualityprofiles.inheritance(
            ...     language="py", quality_profile="My Profile"
            ... )
        """
        return self._get_model(
            "/inheritance",
            QualityProfileInheritanceResponse,
            params={
                "language": language,
                "qualityProfile": quality_profile,
            },
        )

    def projects(
        self,
        key: str,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
        selected: Optional[str] = None,
    ) -> QualityProfileProjectsResponse:
        """Get projects using a quality profile.

        Requires 'Browse' permission on the quality profile.

        Args:
            key: Quality profile key.
            p: Page number.
            ps: Page size.
            q: Search query for project name.
            selected: Filter selection (all, selected, deselected).

        Returns:
            Response containing projects.

        Example:
            >>> projects = client.qualityprofiles.projects(key="py-my-profile-12345")
        """
        return self._get_model(
            "/projects",
            QualityProfileProjectsResponse,
            params={
                "key": key,
                "p": p,
                "ps": ps,
                "q": q,
                "selected": selected,
            },
        )

    def remove_project(self, key: str, project: str) -> None:
        """Remove project association from a quality profile.

        Requires 'Administer' permission on the project.

        Args:
            key: Quality profile key.
            project: Project key.

        Example:
            >>> client.qualityprofiles.remove_project(
            ...     key="py-my-profile-12345", project="my-project"
            ... )
        """
        self._post(
            "/remove_project",
            data={
                "key": key,
                "project": project,
            },
        )

    def rename(self, key: str, name: str) -> None:
        """Rename a quality profile.

        Requires 'Administer Quality Profiles' permission.

        Args:
            key: Quality profile key.
            name: New name.

        Example:
            >>> client.qualityprofiles.rename(
            ...     key="py-my-profile-12345", name="New Profile Name"
            ... )
        """
        self._post(
            "/rename",
            data={
                "key": key,
                "name": name,
            },
        )

    def search(
        self,
        defaults: Optional[bool] = None,
        language: Optional[str] = None,
        project: Optional[str] = None,
        quality_profile: Optional[str] = None,
    ) -> QualityProfileSearchResponse:
        """Search for quality profiles.

        Args:
            defaults: Filter by default profiles.
            language: Filter by language.
            project: Filter by project.
            quality_profile: Filter by profile name.

        Returns:
            Response containing quality profiles.

        Example:
            >>> response = client.qualityprofiles.search(language="py")
            >>> for profile in response.profiles:
            ...     print(f"{profile.name} ({profile.language})")
        """
        params: dict[str, Any] = {}

        if defaults is not None:
            params["defaults"] = str(defaults).lower()
        if language:
            params["language"] = language
        if project:
            params["project"] = project
        if quality_profile:
            params["qualityProfile"] = quality_profile

        return self._get_model("/search", QualityProfileSearchResponse, params=params)

    def set_default(self, language: str, quality_profile: str) -> None:
        """Set a quality profile as the default.

        Requires 'Administer Quality Profiles' permission.

        Args:
            language: Language key.
            quality_profile: Quality profile name.

        Example:
            >>> client.qualityprofiles.set_default(language="py", quality_profile="My Profile")
        """
        self._post(
            "/set_default",
            data={
                "language": language,
                "qualityProfile": quality_profile,
            },
        )

    def show(
        self,
        key: Optional[str] = None,
        compare_to_sonar_way: Optional[bool] = None,
    ) -> QualityProfileShowResponse:
        """Get quality profile details.

        Args:
            key: Quality profile key.
            compare_to_sonar_way: Compare to Sonar way.

        Returns:
            Response containing quality profile details.

        Example:
            >>> profile = client.qualityprofiles.show(key="py-my-profile-12345")
        """
        params: dict[str, Any] = {}
        if key:
            params["key"] = key
        if compare_to_sonar_way is not None:
            params["compareToSonarWay"] = str(compare_to_sonar_way).lower()

        return self._get_model("/show", QualityProfileShowResponse, params=params)
