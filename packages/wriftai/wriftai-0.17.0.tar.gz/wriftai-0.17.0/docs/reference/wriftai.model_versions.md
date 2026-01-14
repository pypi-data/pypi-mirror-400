---
title: model_versions
description: Model Versions module.
---

# model_versions module

Model Versions module.

<a id="wriftai.model_versions.CreateModelVersionParams"></a>

### *class* CreateModelVersionParams

Bases: `TypedDict`

Parameters for creating a version of a model.

<a id="wriftai.model_versions.CreateModelVersionParams.release_notes"></a>

#### release_notes *: str*

Information about changes such as new features, bug fixes, or optimizations
in this model version.

<a id="wriftai.model_versions.CreateModelVersionParams.schemas"></a>

#### schemas *: [Schemas](wriftai.common_types.md#wriftai.common_types.Schemas)*

Schemas for the model version.

<a id="wriftai.model_versions.CreateModelVersionParams.container_image_digest"></a>

#### container_image_digest *: str*

SHA256 hash digest of the model version’s container image.

<a id="wriftai.model_versions.ModelVersions"></a>

### *class* ModelVersions(api)

Bases: `Resource`

Initializes the Resource with an API instance.

* **Parameters:**
  **api** ([*API*](wriftai.api.md#wriftai.api.API)) – An instance of the API class.

<a id="wriftai.model_versions.ModelVersions.get"></a>

#### get(model_owner, model_name, number)

Get a model version.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **number** (*int*) – The number of the model version.
* **Returns:**
  The model version.
* **Return type:**
  [*ModelVersionWithDetails*](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails)

<a id="wriftai.model_versions.ModelVersions.async_get"></a>

#### *async* async_get(model_owner, model_name, number)

Get a model version.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **number** (*int*) – The number of the model version.
* **Returns:**
  The model version.
* **Return type:**
  [*ModelVersionWithDetails*](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails)

<a id="wriftai.model_versions.ModelVersions.list"></a>

#### list(model_owner, model_name, pagination_options=None)

List model versions.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **pagination_options** ([*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *|* *None*) – Optional settings to control pagination behavior.
* **Returns:**
  Paginated response containing model versions and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*ModelVersion*](wriftai.common_types.md#wriftai.common_types.ModelVersion)]

<a id="wriftai.model_versions.ModelVersions.async_list"></a>

#### *async* async_list(model_owner, model_name, pagination_options=None)

List model versions.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **pagination_options** ([*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *|* *None*) – Optional settings to control pagination behavior.
* **Returns:**
  Paginated response containing model versions and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*ModelVersion*](wriftai.common_types.md#wriftai.common_types.ModelVersion)]

<a id="wriftai.model_versions.ModelVersions.delete"></a>

#### delete(model_owner, model_name, number)

Delete a model version.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **number** (*int*) – The number of the model version.
* **Return type:**
  None

<a id="wriftai.model_versions.ModelVersions.async_delete"></a>

#### *async* async_delete(model_owner, model_name, number)

Delete a model version.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **number** (*int*) – The number of the model version.
* **Return type:**
  None

<a id="wriftai.model_versions.ModelVersions.create"></a>

#### create(model_owner, model_name, options)

Create a version of a model.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **options** ([*CreateModelVersionParams*](#wriftai.model_versions.CreateModelVersionParams)) – Model’s version creation parameters.
* **Returns:**
  The new model version.
* **Return type:**
  [*ModelVersionWithDetails*](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails)

<a id="wriftai.model_versions.ModelVersions.async_create"></a>

#### *async* async_create(model_owner, model_name, options)

Create a version of a model.

* **Parameters:**
  * **model_owner** (*str*) – Username of the model’s owner.
  * **model_name** (*str*) – Name of the model.
  * **options** ([*CreateModelVersionParams*](#wriftai.model_versions.CreateModelVersionParams)) – Model’s version creation parameters.
* **Returns:**
  The new model version.
* **Return type:**
  [*ModelVersionWithDetails*](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails)