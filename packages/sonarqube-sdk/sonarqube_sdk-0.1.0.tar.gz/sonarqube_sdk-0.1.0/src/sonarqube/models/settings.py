"""Pydantic models for Settings API.

This module provides models for the /api/settings endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from sonarqube.models.base import SonarQubeModel


class Setting(SonarQubeModel):
    """A setting/property.

    Attributes:
        key: Setting key.
        value: Setting value.
        values: Setting values (for multi-value settings).
        fields_values: Field values (for property sets).
        inherited: Whether the setting is inherited.
        parent_value: Parent value.
        parent_values: Parent values.
    """

    key: str = Field(description="Setting key")
    value: Optional[str] = Field(default=None, description="Setting value")
    values: Optional[list[str]] = Field(default=None, description="Setting values")
    fields_values: Optional[list[dict[str, Any]]] = Field(
        default=None,
        alias="fieldValues",
        description="Field values",
    )
    inherited: Optional[bool] = Field(
        default=None,
        description="Whether the setting is inherited",
    )
    parent_value: Optional[str] = Field(
        default=None,
        alias="parentValue",
        description="Parent value",
    )
    parent_values: Optional[list[str]] = Field(
        default=None,
        alias="parentValues",
        description="Parent values",
    )


class SettingDefinition(SonarQubeModel):
    """A setting definition.

    Attributes:
        key: Setting key.
        name: Setting name.
        description: Setting description.
        category: Setting category.
        sub_category: Setting sub-category.
        type: Setting type.
        default_value: Default value.
        multi_values: Whether multi-values are supported.
        options: Setting options.
        fields: Setting fields (for property sets).
    """

    key: str = Field(description="Setting key")
    name: Optional[str] = Field(default=None, description="Setting name")
    description: Optional[str] = Field(default=None, description="Description")
    category: Optional[str] = Field(default=None, description="Category")
    sub_category: Optional[str] = Field(
        default=None,
        alias="subCategory",
        description="Sub-category",
    )
    type: Optional[str] = Field(default=None, description="Type")
    default_value: Optional[str] = Field(
        default=None,
        alias="defaultValue",
        description="Default value",
    )
    multi_values: Optional[bool] = Field(
        default=None,
        alias="multiValues",
        description="Whether multi-values are supported",
    )
    options: Optional[list[str]] = Field(default=None, description="Options")
    fields: Optional[list[dict[str, Any]]] = Field(default=None, description="Fields")


class SettingsListResponse(SonarQubeModel):
    """Response from listing settings definitions.

    Attributes:
        definitions: List of setting definitions.
    """

    definitions: list[SettingDefinition] = Field(
        default_factory=list,
        description="Setting definitions",
    )


class SettingsValuesResponse(SonarQubeModel):
    """Response from getting settings values.

    Attributes:
        settings: List of settings.
        set_secured_settings: List of secured settings that are set.
    """

    settings: list[Setting] = Field(default_factory=list, description="Settings")
    set_secured_settings: Optional[list[str]] = Field(
        default=None,
        alias="setSecuredSettings",
        description="Secured settings that are set",
    )
