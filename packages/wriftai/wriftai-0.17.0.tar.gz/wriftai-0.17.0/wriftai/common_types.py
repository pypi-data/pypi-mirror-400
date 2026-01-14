"""Common types used across the WriftAI package."""

import sys
from collections.abc import Mapping
from enum import Enum
from typing import Any, TypeAlias, TypedDict, Union

__all__ = [
    "JsonValue",
    "Model",
    "ModelCategory",
    "ModelVersion",
    "ModelVersionWithDetails",
    "ModelVisibility",
    "NotRequired",
    "SchemaIO",
    "Schemas",
    "SortDirection",
    "StrEnum",
    "User",
    "UserWithDetails",
]

JsonValue: TypeAlias = Union[
    list["JsonValue"],
    Mapping[str, "JsonValue"],
    str,
    bool,
    int,
    float,
    None,
]
"""A JSON-compatible value."""


class _FallbackStrEnum(str, Enum):
    """Fallback StrEnum for python 3.10 version."""

    def __str__(self) -> str:
        """Return the enum value as string."""
        return str(self.value)


if sys.version_info >= (3, 11):
    from enum import StrEnum
    from typing import NotRequired
else:
    from enum import Enum

    from typing_extensions import NotRequired

    StrEnum = _FallbackStrEnum


class User(TypedDict):
    """Represents a user."""

    id: str
    """Unique identifier of the user."""
    username: str
    """The username of the user."""
    avatar_url: str
    """URL of the user's avatar."""


class UserWithDetails(User):
    """Represents a user with details."""

    name: str | None
    """The name of the user."""
    bio: str | None
    """The biography of the user."""
    urls: list[str] | None
    """Personal or professional website URLs."""
    location: str | None
    """Location of the user."""
    company: str | None
    """Company the user is associated with."""
    created_at: str
    """Timestamp when the user joined WriftAI."""
    updated_at: str | None
    """Timestamp when the user was last updated."""


class SchemaIO(TypedDict):
    """Represents input and output schemas."""

    input: dict[str, Any]
    """Schema for input, following JSON Schema Draft 2020-12 standards."""
    output: dict[str, Any]
    """Schema for output, following JSON Schema Draft 2020-12 standards."""


class Schemas(TypedDict):
    """Represents schemas of a model version."""

    prediction: SchemaIO
    """The input and output schemas for a prediction."""


class ModelVersion(TypedDict):
    """Represents a model version."""

    number: int
    """The number of the model version."""
    release_notes: str
    """Information about changes such as new features,bug fixes,
        or optimizations in this model version."""
    created_at: str
    """The time when the model version was created."""
    container_image_digest: str
    """A sha256 hash digest of the model version's container image."""


class ModelVersionWithDetails(ModelVersion):
    """Represents a model version with details."""

    schemas: Schemas
    """The schemas of the model version."""


class Hardware(TypedDict):
    """Represents a hardware item."""

    name: str
    """The name of the hardware."""

    identifier: str
    """The identifier of the hardware."""


class SortDirection(StrEnum):
    """Enumeration of possible sorting directions."""

    ASC = "asc"
    DESC = "desc"


class ModelVisibility(StrEnum):
    """Model visibility states."""

    private = "private"
    public = "public"


class ModelCategory(TypedDict):
    """Represents a model category."""

    name: str
    """Name of the model category."""
    slug: str
    """Slug of the model category."""


class Model(TypedDict):
    """Represents a model."""

    id: str
    """The unique identifier of the model."""
    name: str
    """ The name of the model."""
    created_at: str
    """The time when the model was created."""
    visibility: ModelVisibility
    """The visibility of the model."""
    description: str | None
    """Description of the model."""
    updated_at: str | None
    """The time when the model was updated."""
    source_url: str | None
    """Source url from where the model's code can be referenced."""
    license_url: str | None
    """License url where the model's usage is specified."""
    paper_url: str | None
    """Paper url from where research info on the model
        can be found."""
    owner: User
    """The details of the owner of the model."""
    hardware: Hardware
    """The hardware used by the model."""
    predictions_count: int
    """The total number of predictions created across all versions
        of the model."""
    categories: list[ModelCategory]
    """The categories associated with the model."""
