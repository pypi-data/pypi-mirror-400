"""Base Pydantic models for SonarQube SDK.

This module provides the base model class that all other models inherit from,
with common configuration for JSON serialization and validation.

Example:
    Creating a custom model::

        from sonarqube.models.base import SonarQubeModel


        class MyModel(SonarQubeModel):
            name: str
            value: int
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SonarQubeModel(BaseModel):
    """Base model class for all SonarQube API models.

    This class provides common configuration for all models including:
    - Strict validation mode
    - Extra fields are ignored (for forward compatibility)
    - Automatic alias generation from snake_case to camelCase

    All models in the SDK should inherit from this class to ensure
    consistent behavior.

    Example:
        Creating a custom model::

            class Project(SonarQubeModel):
                key: str
                name: str
                visibility: str


            # Create from dict
            project = Project(key="my-project", name="My Project", visibility="public")

            # Serialize to dict
            data = project.model_dump()
    """

    model_config = ConfigDict(
        # Allow population by field name or alias
        populate_by_name=True,
        # Ignore extra fields in response (forward compatibility)
        extra="ignore",
        # Use enum values instead of enum members
        use_enum_values=True,
        # Validate default values
        validate_default=True,
        # Strip whitespace from strings
        str_strip_whitespace=True,
    )
