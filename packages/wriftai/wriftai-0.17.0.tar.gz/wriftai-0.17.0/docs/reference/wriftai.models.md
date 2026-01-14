---
title: models
description: Models module.
---

# models module

Models module.

<a id="wriftai.models.ModelWithDetails"></a>

### *class* ModelWithDetails

Bases: [`Model`](wriftai.common_types.md#wriftai.common_types.Model)

Represents a model with details.

<a id="wriftai.models.ModelWithDetails.overview"></a>

#### overview *: str | None*

The overview of the model.

<a id="wriftai.models.ModelWithDetails.latest_version"></a>

#### latest_version *: [ModelVersionWithDetails](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails) | None*

The details of the latest version of the model.

<a id="wriftai.models.ModelWithDetails.id"></a>

#### id *: str*

<a id="wriftai.models.ModelWithDetails.name"></a>

#### name *: str*

<a id="wriftai.models.ModelWithDetails.created_at"></a>

#### created_at *: str*

<a id="wriftai.models.ModelWithDetails.visibility"></a>

#### visibility *: [ModelVisibility](wriftai.common_types.md#wriftai.common_types.ModelVisibility)*

<a id="wriftai.models.ModelWithDetails.description"></a>

#### description *: str | None*

<a id="wriftai.models.ModelWithDetails.updated_at"></a>

#### updated_at *: str | None*

<a id="wriftai.models.ModelWithDetails.source_url"></a>

#### source_url *: str | None*

<a id="wriftai.models.ModelWithDetails.license_url"></a>

#### license_url *: str | None*

<a id="wriftai.models.ModelWithDetails.paper_url"></a>

#### paper_url *: str | None*

<a id="wriftai.models.ModelWithDetails.owner"></a>

#### owner *: [User](wriftai.common_types.md#wriftai.common_types.User)*

<a id="wriftai.models.ModelWithDetails.hardware"></a>

#### hardware *: Hardware*

<a id="wriftai.models.ModelWithDetails.predictions_count"></a>

#### predictions_count *: int*

<a id="wriftai.models.ModelWithDetails.categories"></a>

#### categories *: list[[ModelCategory](wriftai.common_types.md#wriftai.common_types.ModelCategory)]*

<a id="wriftai.models.ModelsSortBy"></a>

### *class* ModelsSortBy(StrEnum)

Bases: [`StrEnum`](wriftai.common_types.md#wriftai.common_types.StrEnum)

Enumeration of possible sorting options for querying models.

<a id="wriftai.models.ModelsSortBy.CREATED_AT"></a>

#### CREATED_AT *= 'created_at'*

<a id="wriftai.models.ModelsSortBy.PREDICTION_COUNT"></a>

#### PREDICTION_COUNT *= 'prediction_count'*

<a id="wriftai.models.ModelPaginationOptions"></a>

### *class* ModelPaginationOptions

Bases: [`PaginationOptions`](wriftai.md#wriftai.PaginationOptions)

Pagination options for querying models.

<a id="wriftai.models.ModelPaginationOptions.sort_by"></a>

#### sort_by *: NotRequired[[ModelsSortBy](#wriftai.models.ModelsSortBy)]*

The sorting criteria.

<a id="wriftai.models.ModelPaginationOptions.sort_direction"></a>

#### sort_direction *: NotRequired[[SortDirection](wriftai.common_types.md#wriftai.common_types.SortDirection)]*

The sorting direction.

<a id="wriftai.models.ModelPaginationOptions.category_slugs"></a>

#### category_slugs *: NotRequired[list[str]]*

The list of category slugs to filter models.

<a id="wriftai.models.ModelPaginationOptions.cursor"></a>

#### cursor *: NotRequired[str]*

<a id="wriftai.models.ModelPaginationOptions.page_size"></a>

#### page_size *: NotRequired[int]*

<a id="wriftai.models.UpdateModelParams"></a>

### *class* UpdateModelParams

Bases: `TypedDict`

Parameters for updating a model.

<a id="wriftai.models.UpdateModelParams.name"></a>

#### name *: NotRequired[str]*

The name of the model.

<a id="wriftai.models.UpdateModelParams.description"></a>

#### description *: NotRequired[str | None]*

Description of the model.

<a id="wriftai.models.UpdateModelParams.visibility"></a>

#### visibility *: NotRequired[[ModelVisibility](wriftai.common_types.md#wriftai.common_types.ModelVisibility)]*

The visibility of the model.

<a id="wriftai.models.UpdateModelParams.hardware_identifier"></a>

#### hardware_identifier *: NotRequired[str]*

The identifier of the hardware used by the model.

<a id="wriftai.models.UpdateModelParams.source_url"></a>

#### source_url *: NotRequired[str | None]*

Source url from where the model’s code can be referenced.

<a id="wriftai.models.UpdateModelParams.license_url"></a>

#### license_url *: NotRequired[str | None]*

License url where the model’s usage is specified.

<a id="wriftai.models.UpdateModelParams.paper_url"></a>

#### paper_url *: NotRequired[str | None]*

Paper url from where research info on the model can be
found.

<a id="wriftai.models.UpdateModelParams.overview"></a>

#### overview *: NotRequired[str | None]*

The overview of the model.

<a id="wriftai.models.UpdateModelParams.category_slugs"></a>

#### category_slugs *: NotRequired[list[str]]*

List of model category slugs.

<a id="wriftai.models.CreateModelParams"></a>

### *class* CreateModelParams

Bases: `TypedDict`

Parameters for creating a model.

<a id="wriftai.models.CreateModelParams.name"></a>

#### name *: str*

The name of the model.

<a id="wriftai.models.CreateModelParams.hardware_identifier"></a>

#### hardware_identifier *: str*

The identifier of the hardware used by the model.

<a id="wriftai.models.CreateModelParams.visibility"></a>

#### visibility *: NotRequired[[ModelVisibility](wriftai.common_types.md#wriftai.common_types.ModelVisibility)]*

The visibility of the model.

<a id="wriftai.models.CreateModelParams.description"></a>

#### description *: NotRequired[str | None]*

Description of the model.

<a id="wriftai.models.CreateModelParams.source_url"></a>

#### source_url *: NotRequired[str | None]*

Source url from where the model’s code can be referenced.

<a id="wriftai.models.CreateModelParams.license_url"></a>

#### license_url *: NotRequired[str | None]*

License url where the model’s usage is specified.

<a id="wriftai.models.CreateModelParams.paper_url"></a>

#### paper_url *: NotRequired[str | None]*

Paper url from where research info on the model can be
found.

<a id="wriftai.models.CreateModelParams.overview"></a>

#### overview *: NotRequired[str | None]*

The overview of the model.

<a id="wriftai.models.CreateModelParams.category_slugs"></a>

#### category_slugs *: NotRequired[list[str]]*

List of model category slugs.

<a id="wriftai.models.ModelsResource"></a>

### *class* ModelsResource(api)

Bases: `Resource`

Initializes the Resource with an API instance.

* **Parameters:**
  **api** ([*API*](wriftai.api.md#wriftai.api.API)) – An instance of the API class.

<a id="wriftai.models.ModelsResource.delete"></a>

#### delete(owner, name)

Delete a model.

* **Parameters:**
  * **owner** (*str*) – Username of the model’s owner.
  * **name** (*str*) – Name of the model.
* **Return type:**
  None

<a id="wriftai.models.ModelsResource.async_delete"></a>

#### *async* async_delete(owner, name)

Delete a model.

* **Parameters:**
  * **owner** (*str*) – Username of the model’s owner.
  * **name** (*str*) – Name of the model.
* **Return type:**
  None

<a id="wriftai.models.ModelsResource.list"></a>

#### list(pagination_options=None, owner=None)

List models.

* **Parameters:**
  * **pagination_options** ([*ModelPaginationOptions*](#wriftai.models.ModelPaginationOptions) *|* *None*) – Optional settings to control pagination behavior.
  * **owner** (*str* *|* *None*) – Username of the model’s owner to fetch models for. If None, all
    models are fetched.
* **Returns:**
  Paginated response containing models and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*Model*](wriftai.common_types.md#wriftai.common_types.Model)]

<a id="wriftai.models.ModelsResource.async_list"></a>

#### *async* async_list(pagination_options=None, owner=None)

List models.

* **Parameters:**
  * **pagination_options** ([*ModelPaginationOptions*](#wriftai.models.ModelPaginationOptions) *|* *None*) – Optional settings to control pagination behavior.
  * **owner** (*str* *|* *None*) – Username of the model’s owner to fetch models for. If None, all
    models are fetched.
* **Returns:**
  Paginated response containing models and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*Model*](wriftai.common_types.md#wriftai.common_types.Model)]

<a id="wriftai.models.ModelsResource.get"></a>

#### get(owner, name)

Get a model.

* **Parameters:**
  * **owner** (*str*) – Username of the model’s owner.
  * **name** (*str*) – Name of the model.
* **Returns:**
  A model object.
* **Return type:**
  [*ModelWithDetails*](#wriftai.models.ModelWithDetails)

<a id="wriftai.models.ModelsResource.async_get"></a>

#### *async* async_get(owner, name)

Get a model.

* **Parameters:**
  * **owner** (*str*) – Username of the model’s owner.
  * **name** (*str*) – Name of the model.
* **Returns:**
  A model object.
* **Return type:**
  [*ModelWithDetails*](#wriftai.models.ModelWithDetails)

<a id="wriftai.models.ModelsResource.create"></a>

#### create(params)

Create a model.

* **Parameters:**
  **params** ([*CreateModelParams*](#wriftai.models.CreateModelParams)) – Model creation parameters.
* **Returns:**
  The new model.
* **Return type:**
  [*ModelWithDetails*](#wriftai.models.ModelWithDetails)

<a id="wriftai.models.ModelsResource.async_create"></a>

#### *async* async_create(params)

Create a model.

* **Parameters:**
  **params** ([*CreateModelParams*](#wriftai.models.CreateModelParams)) – Model creation parameters.
* **Returns:**
  The new model.
* **Return type:**
  [*ModelWithDetails*](#wriftai.models.ModelWithDetails)

<a id="wriftai.models.ModelsResource.update"></a>

#### update(owner, name, params)

Update a model.

* **Parameters:**
  * **owner** (*str*) – Username of the model’s owner.
  * **name** (*str*) – Name of the model.
  * **params** ([*UpdateModelParams*](#wriftai.models.UpdateModelParams)) – The fields to update.
* **Returns:**
  The updated model.
* **Return type:**
  [*ModelWithDetails*](#wriftai.models.ModelWithDetails)

<a id="wriftai.models.ModelsResource.async_update"></a>

#### *async* async_update(owner, name, params)

Update a model.

* **Parameters:**
  * **owner** (*str*) – Username of the model’s owner.
  * **name** (*str*) – Name of the model.
  * **params** ([*UpdateModelParams*](#wriftai.models.UpdateModelParams)) – The fields to update.
* **Returns:**
  The updated model.
* **Return type:**
  [*ModelWithDetails*](#wriftai.models.ModelWithDetails)

<a id="wriftai.models.ModelsResource.search"></a>

#### search(q, pagination_options=None)

Search models.

* **Parameters:**
  * **q** (*str*) – The search query.
  * **pagination_options** ([*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *|* *None*) – Optional settings to control pagination behavior.
* **Returns:**
  Paginated response containing models and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*Model*](wriftai.common_types.md#wriftai.common_types.Model)]

<a id="wriftai.models.ModelsResource.async_search"></a>

#### *async* async_search(q, pagination_options=None)

Search models.

* **Parameters:**
  * **q** (*str*) – The search query.
  * **pagination_options** ([*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *|* *None*) – Optional settings to control pagintation behavior.
* **Returns:**
  Paginated response containing models and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*Model*](wriftai.common_types.md#wriftai.common_types.Model)]