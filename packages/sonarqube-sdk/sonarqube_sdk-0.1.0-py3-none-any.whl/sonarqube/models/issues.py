"""Pydantic models for Issues API.

This module provides models for the /api/issues endpoints including
searching, updating, and managing issues.

Example:
    Using issue models::

        from sonarqube.models.issues import IssueSearchResponse

        response = client.issues.search(project_keys=["my-project"])
        for issue in response.issues:
            print(f"{issue.severity}: {issue.message}")
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel
from sonarqube.models.common import Component, Paging


class TextRange(SonarQubeModel):
    """Text range within a file.

    Attributes:
        start_line: Starting line number.
        end_line: Ending line number.
        start_offset: Starting character offset.
        end_offset: Ending character offset.
    """

    start_line: int = Field(alias="startLine", description="Starting line number")
    end_line: int = Field(alias="endLine", description="Ending line number")
    start_offset: Optional[int] = Field(
        default=None,
        alias="startOffset",
        description="Starting character offset",
    )
    end_offset: Optional[int] = Field(
        default=None,
        alias="endOffset",
        description="Ending character offset",
    )


class IssueLocation(SonarQubeModel):
    """A location within an issue flow.

    Attributes:
        component: Component key.
        text_range: Text range in the component.
        msg: Message for this location.
    """

    component: Optional[str] = Field(default=None, description="Component key")
    text_range: Optional[TextRange] = Field(
        default=None,
        alias="textRange",
        description="Text range in the component",
    )
    msg: Optional[str] = Field(default=None, description="Message for this location")


class IssueFlow(SonarQubeModel):
    """A flow of locations for an issue.

    Attributes:
        locations: List of locations in the flow.
    """

    locations: list[IssueLocation] = Field(
        default_factory=list,
        description="List of locations in the flow",
    )


class IssueComment(SonarQubeModel):
    """A comment on an issue.

    Attributes:
        key: Comment key.
        login: User login who made the comment.
        html_text: HTML-formatted comment text.
        markdown: Markdown-formatted comment text.
        created_at: Comment creation date.
    """

    key: str = Field(description="Comment key")
    login: str = Field(description="User login")
    html_text: Optional[str] = Field(
        default=None,
        alias="htmlText",
        description="HTML-formatted comment text",
    )
    markdown: Optional[str] = Field(
        default=None,
        description="Markdown-formatted comment text",
    )
    created_at: Optional[str] = Field(
        default=None,
        alias="createdAt",
        description="Comment creation date",
    )


class Issue(SonarQubeModel):
    """A SonarQube issue.

    Attributes:
        key: Unique issue key.
        rule: Rule key that raised the issue.
        severity: Issue severity (BLOCKER, CRITICAL, MAJOR, MINOR, INFO).
        component: Component key where issue was found.
        project: Project key.
        line: Line number in the file.
        message: Issue message.
        status: Issue status (OPEN, CONFIRMED, REOPENED, RESOLVED, CLOSED).
        resolution: Issue resolution if resolved.
        type: Issue type (BUG, VULNERABILITY, CODE_SMELL).
        effort: Effort to fix the issue.
        debt: Technical debt.
        author: Author of the code.
        tags: Issue tags.
        creation_date: Issue creation date.
        update_date: Issue last update date.
        text_range: Text range in the file.
        flows: Issue flows for complex issues.
        comments: Issue comments.

    Example:
        >>> issue = Issue(
        ...     key="AXoN-12345",
        ...     rule="python:S1234",
        ...     severity="MAJOR",
        ...     component="my-project:src/main.py",
        ...     project="my-project",
        ...     message="Remove this unused variable",
        ... )
    """

    key: str = Field(description="Unique issue key")
    rule: str = Field(description="Rule key")
    severity: Optional[str] = Field(
        default=None,
        description="Issue severity",
    )
    component: str = Field(description="Component key")
    project: str = Field(description="Project key")
    line: Optional[int] = Field(default=None, description="Line number")
    message: Optional[str] = Field(default=None, description="Issue message")
    status: Optional[str] = Field(default=None, description="Issue status")
    resolution: Optional[str] = Field(default=None, description="Issue resolution")
    type: Optional[str] = Field(default=None, description="Issue type")
    effort: Optional[str] = Field(default=None, description="Effort to fix")
    debt: Optional[str] = Field(default=None, description="Technical debt")
    author: Optional[str] = Field(default=None, description="Author")
    tags: Optional[list[str]] = Field(default=None, description="Tags")
    creation_date: Optional[str] = Field(
        default=None,
        alias="creationDate",
        description="Creation date",
    )
    update_date: Optional[str] = Field(
        default=None,
        alias="updateDate",
        description="Last update date",
    )
    close_date: Optional[str] = Field(
        default=None,
        alias="closeDate",
        description="Close date",
    )
    text_range: Optional[TextRange] = Field(
        default=None,
        alias="textRange",
        description="Text range in file",
    )
    flows: Optional[list[IssueFlow]] = Field(default=None, description="Issue flows")
    comments: Optional[list[IssueComment]] = Field(
        default=None,
        description="Issue comments",
    )
    assignee: Optional[str] = Field(default=None, description="Assignee login")
    hash: Optional[str] = Field(default=None, description="Issue hash")
    scope: Optional[str] = Field(default=None, description="Issue scope")
    quick_fix_available: Optional[bool] = Field(
        default=None,
        alias="quickFixAvailable",
        description="Whether quick fix is available",
    )
    rule_description_context_key: Optional[str] = Field(
        default=None,
        alias="ruleDescriptionContextKey",
        description="Rule description context key",
    )
    message_formattings: Optional[list[dict[str, Any]]] = Field(
        default=None,
        alias="messageFormattings",
        description="Message formattings",
    )
    code_variants: Optional[list[str]] = Field(
        default=None,
        alias="codeVariants",
        description="Code variants",
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
        description="Issue impacts",
    )


class IssueSearchResponse(SonarQubeModel):
    """Response from searching issues.

    Attributes:
        paging: Paging information.
        issues: List of issues.
        components: List of components referenced by issues.
        rules: List of rules referenced by issues.
        facets: Facet information for filtering.

    Example:
        >>> response = client.issues.search(project_keys=["my-project"])
        >>> for issue in response.issues:
        ...     print(f"{issue.severity}: {issue.message}")
    """

    paging: Optional[Paging] = Field(default=None, description="Paging information")
    issues: list[Issue] = Field(default_factory=list, description="List of issues")
    components: Optional[list[Component]] = Field(
        default=None,
        description="Referenced components",
    )
    rules: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Referenced rules",
    )
    facets: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Facet information",
    )
    p: Optional[int] = Field(default=None, description="Page number")
    ps: Optional[int] = Field(default=None, description="Page size")
    total: Optional[int] = Field(default=None, description="Total count")
    effort_total: Optional[int] = Field(
        default=None,
        alias="effortTotal",
        description="Total effort",
    )


class IssueChangelogResponse(SonarQubeModel):
    """Response from getting issue changelog.

    Attributes:
        changelog: List of changelog entries.
    """

    changelog: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Changelog entries",
    )


class IssueAuthorsResponse(SonarQubeModel):
    """Response from getting issue authors.

    Attributes:
        authors: List of author names.
    """

    authors: list[str] = Field(
        default_factory=list,
        description="List of authors",
    )


class IssueTagsResponse(SonarQubeModel):
    """Response from getting issue tags.

    Attributes:
        tags: List of tags.
    """

    tags: list[str] = Field(default_factory=list, description="List of tags")
