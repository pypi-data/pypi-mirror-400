---
title: common_types
description: Common types used across the WriftAI package.
---

# common_types module

Common types used across the WriftAI package.

<a id="wriftai.common_types.JsonValue"></a>

### JsonValue

A JSON-compatible value.

alias of `list`[JsonValue] | `Mapping`[`str`, JsonValue] | `str` | `bool` | `int` | `float` | `None`

<a id="wriftai.common_types.Model"></a>

### *class* Model

Bases: `TypedDict`

Represents a model.

<a id="wriftai.common_types.Model.id"></a>

#### id *: str*

The unique identifier of the model.

<a id="wriftai.common_types.Model.name"></a>

#### name *: str*

The name of the model.

<a id="wriftai.common_types.Model.created_at"></a>

#### created_at *: str*

The time when the model was created.

<a id="wriftai.common_types.Model.visibility"></a>

#### visibility *: [ModelVisibility](#wriftai.common_types.ModelVisibility)*

The visibility of the model.

<a id="wriftai.common_types.Model.description"></a>

#### description *: str | None*

Description of the model.

<a id="wriftai.common_types.Model.updated_at"></a>

#### updated_at *: str | None*

The time when the model was updated.

<a id="wriftai.common_types.Model.source_url"></a>

#### source_url *: str | None*

Source url from where the model’s code can be referenced.

<a id="wriftai.common_types.Model.license_url"></a>

#### license_url *: str | None*

License url where the model’s usage is specified.

<a id="wriftai.common_types.Model.paper_url"></a>

#### paper_url *: str | None*

Paper url from where research info on the model
can be found.

<a id="wriftai.common_types.Model.owner"></a>

#### owner *: [User](#wriftai.common_types.User)*

The details of the owner of the model.

<a id="wriftai.common_types.Model.hardware"></a>

#### hardware *: Hardware*

The hardware used by the model.

<a id="wriftai.common_types.Model.predictions_count"></a>

#### predictions_count *: int*

The total number of predictions created across all versions
of the model.

<a id="wriftai.common_types.Model.categories"></a>

#### categories *: list[[ModelCategory](#wriftai.common_types.ModelCategory)]*

The categories associated with the model.

<a id="wriftai.common_types.ModelCategory"></a>

### *class* ModelCategory

Bases: `TypedDict`

Represents a model category.

<a id="wriftai.common_types.ModelCategory.name"></a>

#### name *: str*

Name of the model category.

<a id="wriftai.common_types.ModelCategory.slug"></a>

#### slug *: str*

Slug of the model category.

<a id="wriftai.common_types.ModelVersion"></a>

### *class* ModelVersion

Bases: `TypedDict`

Represents a model version.

<a id="wriftai.common_types.ModelVersion.number"></a>

#### number *: int*

The number of the model version.

<a id="wriftai.common_types.ModelVersion.release_notes"></a>

#### release_notes *: str*

Information about changes such as new features,bug fixes,
or optimizations in this model version.

<a id="wriftai.common_types.ModelVersion.created_at"></a>

#### created_at *: str*

The time when the model version was created.

<a id="wriftai.common_types.ModelVersion.container_image_digest"></a>

#### container_image_digest *: str*

A sha256 hash digest of the model version’s container image.

<a id="wriftai.common_types.ModelVersionWithDetails"></a>

### *class* ModelVersionWithDetails

Bases: [`ModelVersion`](#wriftai.common_types.ModelVersion)

Represents a model version with details.

<a id="wriftai.common_types.ModelVersionWithDetails.schemas"></a>

#### schemas *: [Schemas](#wriftai.common_types.Schemas)*

The schemas of the model version.

<a id="wriftai.common_types.ModelVersionWithDetails.number"></a>

#### number *: int*

<a id="wriftai.common_types.ModelVersionWithDetails.release_notes"></a>

#### release_notes *: str*

<a id="wriftai.common_types.ModelVersionWithDetails.created_at"></a>

#### created_at *: str*

<a id="wriftai.common_types.ModelVersionWithDetails.container_image_digest"></a>

#### container_image_digest *: str*

<a id="wriftai.common_types.ModelVisibility"></a>

### *class* ModelVisibility(StrEnum)

Bases: [`StrEnum`](#wriftai.common_types.StrEnum)

Model visibility states.

<a id="wriftai.common_types.ModelVisibility.private"></a>

#### private *= 'private'*

<a id="wriftai.common_types.ModelVisibility.public"></a>

#### public *= 'public'*

<a id="wriftai.common_types.SchemaIO"></a>

### *class* SchemaIO

Bases: `TypedDict`

Represents input and output schemas.

<a id="wriftai.common_types.SchemaIO.input"></a>

#### input *: dict[str, Any]*

Schema for input, following JSON Schema Draft 2020-12 standards.

<a id="wriftai.common_types.SchemaIO.output"></a>

#### output *: dict[str, Any]*

Schema for output, following JSON Schema Draft 2020-12 standards.

<a id="wriftai.common_types.Schemas"></a>

### *class* Schemas

Bases: `TypedDict`

Represents schemas of a model version.

<a id="wriftai.common_types.Schemas.prediction"></a>

#### prediction *: [SchemaIO](#wriftai.common_types.SchemaIO)*

The input and output schemas for a prediction.

<a id="wriftai.common_types.SortDirection"></a>

### *class* SortDirection(StrEnum)

Bases: [`StrEnum`](#wriftai.common_types.StrEnum)

Enumeration of possible sorting directions.

<a id="wriftai.common_types.SortDirection.ASC"></a>

#### ASC *= 'asc'*

<a id="wriftai.common_types.SortDirection.DESC"></a>

#### DESC *= 'desc'*

<a id="wriftai.common_types.StrEnum"></a>

### *class* StrEnum(str, Enum)

Bases: `str`, `ReprEnum`

Enum where members are also (and must be) strings

<a id="wriftai.common_types.User"></a>

### *class* User

Bases: `TypedDict`

Represents a user.

<a id="wriftai.common_types.User.id"></a>

#### id *: str*

Unique identifier of the user.

<a id="wriftai.common_types.User.username"></a>

#### username *: str*

The username of the user.

<a id="wriftai.common_types.User.avatar_url"></a>

#### avatar_url *: str*

URL of the user’s avatar.

<a id="wriftai.common_types.UserWithDetails"></a>

### *class* UserWithDetails

Bases: [`User`](#wriftai.common_types.User)

Represents a user with details.

<a id="wriftai.common_types.UserWithDetails.name"></a>

#### name *: str | None*

The name of the user.

<a id="wriftai.common_types.UserWithDetails.bio"></a>

#### bio *: str | None*

The biography of the user.

<a id="wriftai.common_types.UserWithDetails.urls"></a>

#### urls *: list[str] | None*

Personal or professional website URLs.

<a id="wriftai.common_types.UserWithDetails.location"></a>

#### location *: str | None*

Location of the user.

<a id="wriftai.common_types.UserWithDetails.company"></a>

#### company *: str | None*

Company the user is associated with.

<a id="wriftai.common_types.UserWithDetails.created_at"></a>

#### created_at *: str*

Timestamp when the user joined WriftAI.

<a id="wriftai.common_types.UserWithDetails.updated_at"></a>

#### updated_at *: str | None*

Timestamp when the user was last updated.

<a id="wriftai.common_types.UserWithDetails.id"></a>

#### id *: str*

<a id="wriftai.common_types.UserWithDetails.username"></a>

#### username *: str*

<a id="wriftai.common_types.UserWithDetails.avatar_url"></a>

#### avatar_url *: str*