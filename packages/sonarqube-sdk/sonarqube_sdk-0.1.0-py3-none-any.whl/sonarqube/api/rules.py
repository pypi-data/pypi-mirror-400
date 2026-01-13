"""Rules API for SonarQube SDK.

This module provides methods to search and manage SonarQube rules.

Example:
    Using the Rules API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Search for rules
        rules = client.rules.search(languages=["py"])
        for rule in rules.rules:
            print(f"{rule.key}: {rule.name}")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.rules import (
    Rule,
    RuleRepositoriesResponse,
    RuleSearchResponse,
    RuleShowResponse,
    RuleTagsResponse,
)


class RulesAPI(BaseAPI):
    """API for managing SonarQube rules.

    Rules are the coding standards that SonarQube uses to analyze code.
    This API provides methods to search, view, and customize rules.

    Attributes:
        API_PATH: Base path for rules API ("/api/rules").

    Example:
        Using the rules API::

            # Search for Python rules
            rules = client.rules.search(languages=["py"])

            # Get rule details
            rule = client.rules.show(key="python:S1234")
    """

    API_PATH = "/api/rules"

    def create(
        self,
        custom_key: str,
        markdown_description: str,
        name: str,
        template_key: str,
        clean_code_attribute: Optional[str] = None,
        impacts: Optional[str] = None,
        params: Optional[str] = None,
        prevent_reactivation: Optional[bool] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        type_: Optional[str] = None,
    ) -> Rule:
        """Create a custom rule.

        Requires 'Administer Quality Profiles' permission.

        Args:
            custom_key: Key for the custom rule.
            markdown_description: Rule description in markdown.
            name: Rule name.
            template_key: Template rule key.
            clean_code_attribute: Clean code attribute.
            impacts: Impacts specification.
            params: Rule parameters.
            prevent_reactivation: Prevent reactivation of a removed rule.
            severity: Rule severity.
            status: Rule status.
            type_: Rule type.

        Returns:
            The created rule.

        Example:
            >>> rule = client.rules.create(
            ...     custom_key="my-rule",
            ...     markdown_description="Description",
            ...     name="My Custom Rule",
            ...     template_key="python:S100",
            ... )
        """
        data: dict[str, Any] = {
            "customKey": custom_key,
            "markdownDescription": markdown_description,
            "name": name,
            "templateKey": template_key,
        }
        if clean_code_attribute:
            data["cleanCodeAttribute"] = clean_code_attribute
        if impacts:
            data["impacts"] = impacts
        if params:
            data["params"] = params
        if prevent_reactivation is not None:
            data["preventReactivation"] = str(prevent_reactivation).lower()
        if severity:
            data["severity"] = severity
        if status:
            data["status"] = status
        if type_:
            data["type"] = type_

        response = self._post("/create", data=data)
        return Rule.model_validate(response.get("rule", response))

    def delete(self, key: str) -> None:
        """Delete a custom rule.

        Requires 'Administer Quality Profiles' permission.

        Args:
            key: Rule key.

        Example:
            >>> client.rules.delete(key="python:my-rule")
        """
        self._post("/delete", data={"key": key})

    def repositories(
        self,
        language: Optional[str] = None,
        q: Optional[str] = None,
    ) -> RuleRepositoriesResponse:
        """List rule repositories.

        Args:
            language: Filter by language.
            q: Search query for repository name.

        Returns:
            Response containing list of repositories.

        Example:
            >>> repos = client.rules.repositories(language="py")
            >>> for repo in repos.repositories:
            ...     print(repo)
        """
        return self._get_model(
            "/repositories",
            RuleRepositoriesResponse,
            params={
                "language": language,
                "q": q,
            },
        )

    def search(
        self,
        activation: Optional[bool] = None,
        active_severities: Optional[list[str]] = None,
        asc: Optional[bool] = None,
        available_since: Optional[str] = None,
        clean_code_attribute_categories: Optional[list[str]] = None,
        cwe: Optional[list[str]] = None,
        f: Optional[list[str]] = None,
        facets: Optional[list[str]] = None,
        impact_severities: Optional[list[str]] = None,
        impact_software_qualities: Optional[list[str]] = None,
        include_external: Optional[bool] = None,
        inheritance: Optional[list[str]] = None,
        is_template: Optional[bool] = None,
        languages: Optional[list[str]] = None,
        owasp_top10: Optional[list[str]] = None,
        owasp_top10_2021: Optional[list[str]] = None,
        p: Optional[int] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
        qprofile: Optional[str] = None,
        repositories: Optional[list[str]] = None,
        rule_key: Optional[str] = None,
        s: Optional[str] = None,
        sans_top25: Optional[list[str]] = None,
        severities: Optional[list[str]] = None,
        sonarsource_security: Optional[list[str]] = None,
        statuses: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        template_key: Optional[str] = None,
        types: Optional[list[str]] = None,
    ) -> RuleSearchResponse:
        """Search for rules.

        Args:
            activation: Filter by activation status in quality profile.
            active_severities: Filter by active severities.
            asc: Ascending sort order.
            available_since: Filter by availability date.
            clean_code_attribute_categories: Clean code attribute categories.
            cwe: Filter by CWE identifiers.
            f: Fields to return.
            facets: Facets to return.
            impact_severities: Impact severities.
            impact_software_qualities: Impact software qualities.
            include_external: Include external rules.
            inheritance: Filter by inheritance.
            is_template: Filter template rules.
            languages: Filter by languages.
            owasp_top10: Filter by OWASP Top 10 2017.
            owasp_top10_2021: Filter by OWASP Top 10 2021.
            p: Page number.
            ps: Page size.
            q: Search query.
            qprofile: Quality profile key.
            repositories: Filter by repositories.
            rule_key: Filter by rule key.
            s: Sort field.
            sans_top25: Filter by SANS Top 25.
            severities: Filter by severities.
            sonarsource_security: Filter by SonarSource security.
            statuses: Filter by statuses.
            tags: Filter by tags.
            template_key: Filter by template key.
            types: Filter by types.

        Returns:
            Response containing list of rules.

        Example:
            >>> response = client.rules.search(languages=["py"])
            >>> for rule in response.rules:
            ...     print(f"{rule.key}: {rule.name}")
        """
        params: dict[str, Any] = {}

        if activation is not None:
            params["activation"] = str(activation).lower()
        if active_severities:
            params["active_severities"] = ",".join(active_severities)
        if asc is not None:
            params["asc"] = str(asc).lower()
        if available_since:
            params["available_since"] = available_since
        if clean_code_attribute_categories:
            params["cleanCodeAttributeCategories"] = ",".join(
                clean_code_attribute_categories
            )
        if cwe:
            params["cwe"] = ",".join(cwe)
        if f:
            params["f"] = ",".join(f)
        if facets:
            params["facets"] = ",".join(facets)
        if impact_severities:
            params["impactSeverities"] = ",".join(impact_severities)
        if impact_software_qualities:
            params["impactSoftwareQualities"] = ",".join(impact_software_qualities)
        if include_external is not None:
            params["include_external"] = str(include_external).lower()
        if inheritance:
            params["inheritance"] = ",".join(inheritance)
        if is_template is not None:
            params["is_template"] = str(is_template).lower()
        if languages:
            params["languages"] = ",".join(languages)
        if owasp_top10:
            params["owaspTop10"] = ",".join(owasp_top10)
        if owasp_top10_2021:
            params["owaspTop10-2021"] = ",".join(owasp_top10_2021)
        if p:
            params["p"] = p
        if ps:
            params["ps"] = ps
        if q:
            params["q"] = q
        if qprofile:
            params["qprofile"] = qprofile
        if repositories:
            params["repositories"] = ",".join(repositories)
        if rule_key:
            params["rule_key"] = rule_key
        if s:
            params["s"] = s
        if sans_top25:
            params["sansTop25"] = ",".join(sans_top25)
        if severities:
            params["severities"] = ",".join(severities)
        if sonarsource_security:
            params["sonarsourceSecurity"] = ",".join(sonarsource_security)
        if statuses:
            params["statuses"] = ",".join(statuses)
        if tags:
            params["tags"] = ",".join(tags)
        if template_key:
            params["template_key"] = template_key
        if types:
            params["types"] = ",".join(types)

        return self._get_model("/search", RuleSearchResponse, params=params)

    def show(
        self,
        key: str,
        actives: Optional[bool] = None,
    ) -> RuleShowResponse:
        """Get rule details.

        Args:
            key: Rule key.
            actives: Include active instances in quality profiles.

        Returns:
            Response containing rule details.

        Example:
            >>> response = client.rules.show(key="python:S1234")
            >>> print(response.rule.name)
        """
        params: dict[str, Any] = {"key": key}
        if actives is not None:
            params["actives"] = str(actives).lower()

        return self._get_model("/show", RuleShowResponse, params=params)

    def tags(
        self,
        ps: Optional[int] = None,
        q: Optional[str] = None,
    ) -> RuleTagsResponse:
        """List rule tags.

        Args:
            ps: Page size.
            q: Search query for tags.

        Returns:
            Response containing list of tags.

        Example:
            >>> response = client.rules.tags()
            >>> for tag in response.tags:
            ...     print(tag)
        """
        return self._get_model(
            "/tags",
            RuleTagsResponse,
            params={
                "ps": ps,
                "q": q,
            },
        )

    def update(
        self,
        key: str,
        markdown_description: Optional[str] = None,
        markdown_note: Optional[str] = None,
        name: Optional[str] = None,
        params: Optional[str] = None,
        remediation_fn_base_effort: Optional[str] = None,
        remediation_fn_type: Optional[str] = None,
        remediation_gap_multiplier: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Rule:
        """Update a rule.

        Requires 'Administer Quality Profiles' permission.

        Args:
            key: Rule key.
            markdown_description: Rule description in markdown.
            markdown_note: Note in markdown.
            name: Rule name.
            params: Rule parameters.
            remediation_fn_base_effort: Remediation function base effort.
            remediation_fn_type: Remediation function type.
            remediation_gap_multiplier: Remediation gap multiplier.
            severity: Rule severity.
            status: Rule status.
            tags: Rule tags.

        Returns:
            The updated rule.

        Example:
            >>> rule = client.rules.update(key="python:S1234", tags=["team-a", "security"])
        """
        data: dict[str, Any] = {"key": key}

        if markdown_description:
            data["markdownDescription"] = markdown_description
        if markdown_note:
            data["markdown_note"] = markdown_note
        if name:
            data["name"] = name
        if params:
            data["params"] = params
        if remediation_fn_base_effort:
            data["remediationFnBaseEffort"] = remediation_fn_base_effort
        if remediation_fn_type:
            data["remediationFnType"] = remediation_fn_type
        if remediation_gap_multiplier:
            data["remediationGapMultiplier"] = remediation_gap_multiplier
        if severity:
            data["severity"] = severity
        if status:
            data["status"] = status
        if tags:
            data["tags"] = ",".join(tags)

        response = self._post("/update", data=data)
        return Rule.model_validate(response.get("rule", response))
