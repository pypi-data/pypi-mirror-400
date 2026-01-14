---
title: model_categories
description: Model categories module.
---

# model_categories module

Model categories module.

<a id="wriftai.model_categories.ModelCategoryWithDetails"></a>

### *class* ModelCategoryWithDetails

Bases: [`ModelCategory`](wriftai.common_types.md#wriftai.common_types.ModelCategory)

Represents a model category with details.

<a id="wriftai.model_categories.ModelCategoryWithDetails.description"></a>

#### description *: str*

Description of the model category.

<a id="wriftai.model_categories.ModelCategoryWithDetails.name"></a>

#### name *: str*

<a id="wriftai.model_categories.ModelCategoryWithDetails.slug"></a>

#### slug *: str*

<a id="wriftai.model_categories.ModelCategories"></a>

### *class* ModelCategories(api)

Bases: `Resource`

Initializes the Resource with an API instance.

* **Parameters:**
  **api** ([*API*](wriftai.api.md#wriftai.api.API)) – An instance of the API class.

<a id="wriftai.model_categories.ModelCategories.list"></a>

#### list(pagination_options)

List model categories.

* **Parameters:**
  **pagination_options** ([*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *|* *None*) – Optional settings to control pagination behavior.
* **Returns:**
  Paginated response containing model category items and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*ModelCategoryWithDetails*](#wriftai.model_categories.ModelCategoryWithDetails)]

<a id="wriftai.model_categories.ModelCategories.async_list"></a>

#### *async* async_list(pagination_options)

List model categories.

* **Parameters:**
  **pagination_options** ([*PaginationOptions*](wriftai.md#wriftai.PaginationOptions) *|* *None*) – Optional settings to control pagination behavior.
* **Returns:**
  Paginated response containing model category items and navigation metadata.
* **Return type:**
  [*PaginatedResponse*](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)[[*ModelCategoryWithDetails*](#wriftai.model_categories.ModelCategoryWithDetails)]