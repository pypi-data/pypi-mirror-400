"""Pydantic models for Sources API.

This module provides models for the /api/sources endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel


class SourceLine(SonarQubeModel):
    """A line of source code.

    Attributes:
        line: Line number.
        code: Source code.
        scm_revision: SCM revision.
        scm_author: SCM author.
        scm_date: SCM date.
        duplicated: Whether the line is duplicated.
        is_new: Whether the line is new.
    """

    line: int = Field(description="Line number")
    code: Optional[str] = Field(default=None, description="Source code")
    scm_revision: Optional[str] = Field(
        default=None,
        alias="scmRevision",
        description="SCM revision",
    )
    scm_author: Optional[str] = Field(
        default=None,
        alias="scmAuthor",
        description="SCM author",
    )
    scm_date: Optional[str] = Field(
        default=None,
        alias="scmDate",
        description="SCM date",
    )
    duplicated: Optional[bool] = Field(
        default=None,
        description="Whether the line is duplicated",
    )
    is_new: Optional[bool] = Field(
        default=None,
        alias="isNew",
        description="Whether the line is new",
    )


class SourcesResponse(SonarQubeModel):
    """Response from getting sources.

    Attributes:
        sources: List of source lines.
    """

    sources: list[SourceLine] = Field(
        default_factory=list,
        description="Source lines",
    )


class ScmResponse(SonarQubeModel):
    """Response from getting SCM information.

    Attributes:
        scm: SCM information by line.
    """

    scm: Optional[list[list[Any]]] = Field(default=None, description="SCM information")
