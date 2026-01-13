"""Pydantic models for Quality Profiles API.

This module provides models for the /api/qualityprofiles endpoints including
creating, updating, and managing quality profiles.

Example:
    Using quality profile models::

        from sonarqube.models.qualityprofiles import QualityProfileSearchResponse

        response = client.qualityprofiles.search()
        for profile in response.profiles:
            print(f"{profile.name} ({profile.language})")
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel


class QualityProfile(SonarQubeModel):
    """A SonarQube quality profile.

    Attributes:
        key: Quality profile key.
        name: Quality profile name.
        language: Language key.
        language_name: Language display name.
        is_inherited: Whether this is inherited.
        is_default: Whether this is the default.
        is_built_in: Whether this is built-in.
        active_rule_count: Number of active rules.
        active_deprecated_rule_count: Number of deprecated active rules.
        rules_updated_at: Date rules were last updated.
        last_used: Date profile was last used.
        user_updated_at: Date profile was last updated by user.

    Example:
        >>> profile = QualityProfile(
        ...     key="py-my-profile-12345",
        ...     name="My Python Profile",
        ...     language="py",
        ...     languageName="Python",
        ... )
    """

    key: str = Field(description="Quality profile key")
    name: str = Field(description="Quality profile name")
    language: str = Field(description="Language key")
    language_name: Optional[str] = Field(
        default=None,
        alias="languageName",
        description="Language display name",
    )
    is_inherited: Optional[bool] = Field(
        default=None,
        alias="isInherited",
        description="Whether this is inherited",
    )
    is_default: Optional[bool] = Field(
        default=None,
        alias="isDefault",
        description="Whether this is the default",
    )
    is_built_in: Optional[bool] = Field(
        default=None,
        alias="isBuiltIn",
        description="Whether this is built-in",
    )
    parent_key: Optional[str] = Field(
        default=None,
        alias="parentKey",
        description="Parent profile key",
    )
    parent_name: Optional[str] = Field(
        default=None,
        alias="parentName",
        description="Parent profile name",
    )
    active_rule_count: Optional[int] = Field(
        default=None,
        alias="activeRuleCount",
        description="Number of active rules",
    )
    active_deprecated_rule_count: Optional[int] = Field(
        default=None,
        alias="activeDeprecatedRuleCount",
        description="Number of deprecated active rules",
    )
    rules_updated_at: Optional[str] = Field(
        default=None,
        alias="rulesUpdatedAt",
        description="Date rules were last updated",
    )
    last_used: Optional[str] = Field(
        default=None,
        alias="lastUsed",
        description="Date profile was last used",
    )
    user_updated_at: Optional[str] = Field(
        default=None,
        alias="userUpdatedAt",
        description="Date profile was last updated by user",
    )
    project_count: Optional[int] = Field(
        default=None,
        alias="projectCount",
        description="Number of projects using this profile",
    )
    actions: Optional[dict[str, Any]] = Field(
        default=None,
        description="Available actions",
    )


class QualityProfileSearchResponse(SonarQubeModel):
    """Response from searching quality profiles.

    Attributes:
        profiles: List of quality profiles.
        actions: Available actions.

    Example:
        >>> response = client.qualityprofiles.search()
        >>> for profile in response.profiles:
        ...     print(f"{profile.name} ({profile.language})")
    """

    profiles: list[QualityProfile] = Field(
        default_factory=list,
        description="List of quality profiles",
    )
    actions: Optional[dict[str, Any]] = Field(
        default=None,
        description="Available actions",
    )


class QualityProfileCreateResponse(SonarQubeModel):
    """Response from creating a quality profile.

    Attributes:
        profile: Created quality profile.
        warnings: List of warnings.
        infos: List of info messages.
    """

    profile: QualityProfile = Field(description="Created quality profile")
    warnings: Optional[list[str]] = Field(default=None, description="Warnings")
    infos: Optional[list[str]] = Field(default=None, description="Info messages")


class QualityProfileShowResponse(SonarQubeModel):
    """Response from showing a quality profile.

    Attributes:
        profile: Quality profile details.
    """

    profile: QualityProfile = Field(description="Quality profile details")


class QualityProfileInheritanceResponse(SonarQubeModel):
    """Response from getting quality profile inheritance.

    Attributes:
        profile: Profile details.
        ancestors: Ancestor profiles.
        children: Child profiles.
    """

    profile: QualityProfile = Field(description="Profile details")
    ancestors: Optional[list[QualityProfile]] = Field(
        default=None,
        description="Ancestor profiles",
    )
    children: Optional[list[QualityProfile]] = Field(
        default=None,
        description="Child profiles",
    )


class QualityProfileChangelogEntry(SonarQubeModel):
    """A changelog entry for a quality profile.

    Attributes:
        date: Date of the change.
        author_login: Author login.
        author_name: Author name.
        action: Action performed.
        rule_key: Rule key.
        rule_name: Rule name.
        params: Changed parameters.
    """

    date: str = Field(description="Date of the change")
    author_login: Optional[str] = Field(
        default=None,
        alias="authorLogin",
        description="Author login",
    )
    author_name: Optional[str] = Field(
        default=None,
        alias="authorName",
        description="Author name",
    )
    action: Optional[str] = Field(default=None, description="Action performed")
    rule_key: Optional[str] = Field(
        default=None,
        alias="ruleKey",
        description="Rule key",
    )
    rule_name: Optional[str] = Field(
        default=None,
        alias="ruleName",
        description="Rule name",
    )
    params: Optional[dict[str, Any]] = Field(
        default=None,
        description="Changed parameters",
    )


class QualityProfileChangelogResponse(SonarQubeModel):
    """Response from getting quality profile changelog.

    Attributes:
        events: List of changelog entries.
        paging: Paging information.
    """

    events: list[QualityProfileChangelogEntry] = Field(
        default_factory=list,
        description="Changelog entries",
    )
    paging: Optional[dict[str, Any]] = Field(
        default=None, description="Paging information"
    )
    p: Optional[int] = Field(default=None, description="Page number")
    ps: Optional[int] = Field(default=None, description="Page size")
    total: Optional[int] = Field(default=None, description="Total count")


class QualityProfileProjectsResponse(SonarQubeModel):
    """Response from getting projects using a quality profile.

    Attributes:
        paging: Paging information.
        results: List of projects.
    """

    paging: Optional[dict[str, Any]] = Field(default=None, description="Paging")
    results: list[dict[str, Any]] = Field(default_factory=list, description="Projects")


class RuleActivation(SonarQubeModel):
    """A rule activation in a quality profile.

    Attributes:
        qProfile: Quality profile key.
        inherit: Inheritance status.
        severity: Rule severity.
        params: Activation parameters.
    """

    q_profile: str = Field(alias="qProfile", description="Quality profile key")
    inherit: Optional[str] = Field(default=None, description="Inheritance status")
    severity: Optional[str] = Field(default=None, description="Rule severity")
    params: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Activation parameters",
    )
