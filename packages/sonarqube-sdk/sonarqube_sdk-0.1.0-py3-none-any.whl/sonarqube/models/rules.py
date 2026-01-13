"""Pydantic models for Rules API.

This module provides models for the /api/rules endpoints including
searching and managing rules.

Example:
    Using rule models::

        from sonarqube.models.rules import RuleSearchResponse

        response = client.rules.search(languages=["py"])
        for rule in response.rules:
            print(f"{rule.key}: {rule.name}")
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel
from sonarqube.models.common import Paging


class RuleParam(SonarQubeModel):
    """A parameter for a rule.

    Attributes:
        key: Parameter key.
        html_desc: HTML description.
        default_value: Default value.
        type: Parameter type.
    """

    key: str = Field(description="Parameter key")
    html_desc: Optional[str] = Field(
        default=None,
        alias="htmlDesc",
        description="HTML description",
    )
    default_value: Optional[str] = Field(
        default=None,
        alias="defaultValue",
        description="Default value",
    )
    type: Optional[str] = Field(default=None, description="Parameter type")


class Rule(SonarQubeModel):
    """A SonarQube rule.

    Attributes:
        key: Unique rule key.
        repo: Rule repository.
        name: Rule name.
        created_at: Creation date.
        html_desc: HTML description.
        md_desc: Markdown description.
        severity: Rule severity.
        status: Rule status.
        is_template: Whether this is a template rule.
        template_key: Template rule key if this is based on a template.
        tags: Rule tags.
        sys_tags: System tags.
        lang: Language key.
        lang_name: Language name.
        params: Rule parameters.
        type: Rule type (BUG, VULNERABILITY, CODE_SMELL, SECURITY_HOTSPOT).
        internal_key: Internal rule key.
        is_external: Whether this is an external rule.

    Example:
        >>> rule = Rule(
        ...     key="python:S1234",
        ...     repo="python",
        ...     name="Unused variables should be removed",
        ...     severity="MAJOR",
        ... )
    """

    key: str = Field(description="Unique rule key")
    repo: Optional[str] = Field(default=None, description="Rule repository")
    name: Optional[str] = Field(default=None, description="Rule name")
    created_at: Optional[str] = Field(
        default=None,
        alias="createdAt",
        description="Creation date",
    )
    html_desc: Optional[str] = Field(
        default=None,
        alias="htmlDesc",
        description="HTML description",
    )
    md_desc: Optional[str] = Field(
        default=None,
        alias="mdDesc",
        description="Markdown description",
    )
    severity: Optional[str] = Field(default=None, description="Rule severity")
    status: Optional[str] = Field(default=None, description="Rule status")
    is_template: Optional[bool] = Field(
        default=None,
        alias="isTemplate",
        description="Whether this is a template rule",
    )
    template_key: Optional[str] = Field(
        default=None,
        alias="templateKey",
        description="Template rule key",
    )
    tags: Optional[list[str]] = Field(default=None, description="Rule tags")
    sys_tags: Optional[list[str]] = Field(
        default=None,
        alias="sysTags",
        description="System tags",
    )
    lang: Optional[str] = Field(default=None, description="Language key")
    lang_name: Optional[str] = Field(
        default=None,
        alias="langName",
        description="Language name",
    )
    params: Optional[list[RuleParam]] = Field(
        default=None,
        description="Rule parameters",
    )
    type: Optional[str] = Field(default=None, description="Rule type")
    internal_key: Optional[str] = Field(
        default=None,
        alias="internalKey",
        description="Internal rule key",
    )
    is_external: Optional[bool] = Field(
        default=None,
        alias="isExternal",
        description="Whether this is an external rule",
    )
    clean_code_attribute: Optional[str] = Field(
        default=None,
        alias="cleanCodeAttribute",
        description="Clean code attribute",
    )
    clean_code_attribute_category: Optional[str] = Field(
        default=None,
        alias="cleanCodeAttributeCategory",
        description="Clean code attribute category",
    )
    impacts: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Rule impacts",
    )
    description_sections: Optional[list[dict[str, Any]]] = Field(
        default=None,
        alias="descriptionSections",
        description="Description sections",
    )
    education_principles: Optional[list[str]] = Field(
        default=None,
        alias="educationPrinciples",
        description="Education principles",
    )


class RuleSearchResponse(SonarQubeModel):
    """Response from searching rules.

    Attributes:
        total: Total number of rules.
        p: Page number.
        ps: Page size.
        rules: List of rules.
        facets: Facet information.

    Example:
        >>> response = client.rules.search(languages=["py"])
        >>> print(f"Found {response.total} rules")
        >>> for rule in response.rules:
        ...     print(rule.name)
    """

    total: int = Field(description="Total number of rules")
    p: int = Field(description="Page number")
    ps: int = Field(description="Page size")
    rules: list[Rule] = Field(default_factory=list, description="List of rules")
    facets: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Facet information"
    )
    paging: Optional[Paging] = Field(default=None, description="Paging information")


class RuleShowResponse(SonarQubeModel):
    """Response from showing a rule.

    Attributes:
        rule: The rule details.
        actives: Active instances of the rule in quality profiles.
    """

    rule: Rule = Field(description="The rule details")
    actives: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Active instances in quality profiles",
    )


class RuleRepositoriesResponse(SonarQubeModel):
    """Response from listing rule repositories.

    Attributes:
        repositories: List of repositories.
    """

    repositories: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of repositories",
    )


class RuleTagsResponse(SonarQubeModel):
    """Response from listing rule tags.

    Attributes:
        tags: List of tags.
    """

    tags: list[str] = Field(default_factory=list, description="List of tags")
