---
title: wriftai
description: Package initializer for WriftAI Python Client.
---

# wriftai package

## Submodules

* [api module](wriftai.api.md)
  * [`API`](wriftai.api.md#wriftai.api.API)
    * [`API.request()`](wriftai.api.md#wriftai.api.API.request)
    * [`API.async_request()`](wriftai.api.md#wriftai.api.API.async_request)
* [authenticated_user module](wriftai.authenticated_user.md)
  * [`UpdateUserParams`](wriftai.authenticated_user.md#wriftai.authenticated_user.UpdateUserParams)
    * [`UpdateUserParams.username`](wriftai.authenticated_user.md#wriftai.authenticated_user.UpdateUserParams.username)
    * [`UpdateUserParams.name`](wriftai.authenticated_user.md#wriftai.authenticated_user.UpdateUserParams.name)
    * [`UpdateUserParams.bio`](wriftai.authenticated_user.md#wriftai.authenticated_user.UpdateUserParams.bio)
    * [`UpdateUserParams.urls`](wriftai.authenticated_user.md#wriftai.authenticated_user.UpdateUserParams.urls)
    * [`UpdateUserParams.company`](wriftai.authenticated_user.md#wriftai.authenticated_user.UpdateUserParams.company)
    * [`UpdateUserParams.location`](wriftai.authenticated_user.md#wriftai.authenticated_user.UpdateUserParams.location)
  * [`AuthenticatedUser`](wriftai.authenticated_user.md#wriftai.authenticated_user.AuthenticatedUser)
    * [`AuthenticatedUser.get()`](wriftai.authenticated_user.md#wriftai.authenticated_user.AuthenticatedUser.get)
    * [`AuthenticatedUser.async_get()`](wriftai.authenticated_user.md#wriftai.authenticated_user.AuthenticatedUser.async_get)
    * [`AuthenticatedUser.models()`](wriftai.authenticated_user.md#wriftai.authenticated_user.AuthenticatedUser.models)
    * [`AuthenticatedUser.async_models()`](wriftai.authenticated_user.md#wriftai.authenticated_user.AuthenticatedUser.async_models)
    * [`AuthenticatedUser.update()`](wriftai.authenticated_user.md#wriftai.authenticated_user.AuthenticatedUser.update)
    * [`AuthenticatedUser.async_update()`](wriftai.authenticated_user.md#wriftai.authenticated_user.AuthenticatedUser.async_update)
* [common_types module](wriftai.common_types.md)
  * [`JsonValue`](wriftai.common_types.md#wriftai.common_types.JsonValue)
  * [`Model`](wriftai.common_types.md#wriftai.common_types.Model)
    * [`Model.id`](wriftai.common_types.md#wriftai.common_types.Model.id)
    * [`Model.name`](wriftai.common_types.md#wriftai.common_types.Model.name)
    * [`Model.created_at`](wriftai.common_types.md#wriftai.common_types.Model.created_at)
    * [`Model.visibility`](wriftai.common_types.md#wriftai.common_types.Model.visibility)
    * [`Model.description`](wriftai.common_types.md#wriftai.common_types.Model.description)
    * [`Model.updated_at`](wriftai.common_types.md#wriftai.common_types.Model.updated_at)
    * [`Model.source_url`](wriftai.common_types.md#wriftai.common_types.Model.source_url)
    * [`Model.license_url`](wriftai.common_types.md#wriftai.common_types.Model.license_url)
    * [`Model.paper_url`](wriftai.common_types.md#wriftai.common_types.Model.paper_url)
    * [`Model.owner`](wriftai.common_types.md#wriftai.common_types.Model.owner)
    * [`Model.hardware`](wriftai.common_types.md#wriftai.common_types.Model.hardware)
    * [`Model.predictions_count`](wriftai.common_types.md#wriftai.common_types.Model.predictions_count)
    * [`Model.categories`](wriftai.common_types.md#wriftai.common_types.Model.categories)
  * [`ModelCategory`](wriftai.common_types.md#wriftai.common_types.ModelCategory)
    * [`ModelCategory.name`](wriftai.common_types.md#wriftai.common_types.ModelCategory.name)
    * [`ModelCategory.slug`](wriftai.common_types.md#wriftai.common_types.ModelCategory.slug)
  * [`ModelVersion`](wriftai.common_types.md#wriftai.common_types.ModelVersion)
    * [`ModelVersion.number`](wriftai.common_types.md#wriftai.common_types.ModelVersion.number)
    * [`ModelVersion.release_notes`](wriftai.common_types.md#wriftai.common_types.ModelVersion.release_notes)
    * [`ModelVersion.created_at`](wriftai.common_types.md#wriftai.common_types.ModelVersion.created_at)
    * [`ModelVersion.container_image_digest`](wriftai.common_types.md#wriftai.common_types.ModelVersion.container_image_digest)
  * [`ModelVersionWithDetails`](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails)
    * [`ModelVersionWithDetails.schemas`](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails.schemas)
    * [`ModelVersionWithDetails.number`](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails.number)
    * [`ModelVersionWithDetails.release_notes`](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails.release_notes)
    * [`ModelVersionWithDetails.created_at`](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails.created_at)
    * [`ModelVersionWithDetails.container_image_digest`](wriftai.common_types.md#wriftai.common_types.ModelVersionWithDetails.container_image_digest)
  * [`ModelVisibility`](wriftai.common_types.md#wriftai.common_types.ModelVisibility)
    * [`ModelVisibility.private`](wriftai.common_types.md#wriftai.common_types.ModelVisibility.private)
    * [`ModelVisibility.public`](wriftai.common_types.md#wriftai.common_types.ModelVisibility.public)
  * [`SchemaIO`](wriftai.common_types.md#wriftai.common_types.SchemaIO)
    * [`SchemaIO.input`](wriftai.common_types.md#wriftai.common_types.SchemaIO.input)
    * [`SchemaIO.output`](wriftai.common_types.md#wriftai.common_types.SchemaIO.output)
  * [`Schemas`](wriftai.common_types.md#wriftai.common_types.Schemas)
    * [`Schemas.prediction`](wriftai.common_types.md#wriftai.common_types.Schemas.prediction)
  * [`SortDirection`](wriftai.common_types.md#wriftai.common_types.SortDirection)
    * [`SortDirection.ASC`](wriftai.common_types.md#wriftai.common_types.SortDirection.ASC)
    * [`SortDirection.DESC`](wriftai.common_types.md#wriftai.common_types.SortDirection.DESC)
  * [`StrEnum`](wriftai.common_types.md#wriftai.common_types.StrEnum)
  * [`User`](wriftai.common_types.md#wriftai.common_types.User)
    * [`User.id`](wriftai.common_types.md#wriftai.common_types.User.id)
    * [`User.username`](wriftai.common_types.md#wriftai.common_types.User.username)
    * [`User.avatar_url`](wriftai.common_types.md#wriftai.common_types.User.avatar_url)
  * [`UserWithDetails`](wriftai.common_types.md#wriftai.common_types.UserWithDetails)
    * [`UserWithDetails.name`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.name)
    * [`UserWithDetails.bio`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.bio)
    * [`UserWithDetails.urls`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.urls)
    * [`UserWithDetails.location`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.location)
    * [`UserWithDetails.company`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.company)
    * [`UserWithDetails.created_at`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.created_at)
    * [`UserWithDetails.updated_at`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.updated_at)
    * [`UserWithDetails.id`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.id)
    * [`UserWithDetails.username`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.username)
    * [`UserWithDetails.avatar_url`](wriftai.common_types.md#wriftai.common_types.UserWithDetails.avatar_url)
* [hardware module](wriftai.hardware.md)
  * [`HardwareWithDetails`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails)
    * [`HardwareWithDetails.gpus`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails.gpus)
    * [`HardwareWithDetails.cpus`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails.cpus)
    * [`HardwareWithDetails.ram_per_gpu_gb`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails.ram_per_gpu_gb)
    * [`HardwareWithDetails.ram_gb`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails.ram_gb)
    * [`HardwareWithDetails.name`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails.name)
    * [`HardwareWithDetails.identifier`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails.identifier)
    * [`HardwareWithDetails.created_at`](wriftai.hardware.md#wriftai.hardware.HardwareWithDetails.created_at)
  * [`HardwareResource`](wriftai.hardware.md#wriftai.hardware.HardwareResource)
    * [`HardwareResource.list()`](wriftai.hardware.md#wriftai.hardware.HardwareResource.list)
    * [`HardwareResource.async_list()`](wriftai.hardware.md#wriftai.hardware.HardwareResource.async_list)
* [model_categories module](wriftai.model_categories.md)
  * [`ModelCategoryWithDetails`](wriftai.model_categories.md#wriftai.model_categories.ModelCategoryWithDetails)
    * [`ModelCategoryWithDetails.description`](wriftai.model_categories.md#wriftai.model_categories.ModelCategoryWithDetails.description)
    * [`ModelCategoryWithDetails.name`](wriftai.model_categories.md#wriftai.model_categories.ModelCategoryWithDetails.name)
    * [`ModelCategoryWithDetails.slug`](wriftai.model_categories.md#wriftai.model_categories.ModelCategoryWithDetails.slug)
  * [`ModelCategories`](wriftai.model_categories.md#wriftai.model_categories.ModelCategories)
    * [`ModelCategories.list()`](wriftai.model_categories.md#wriftai.model_categories.ModelCategories.list)
    * [`ModelCategories.async_list()`](wriftai.model_categories.md#wriftai.model_categories.ModelCategories.async_list)
* [model_versions module](wriftai.model_versions.md)
  * [`CreateModelVersionParams`](wriftai.model_versions.md#wriftai.model_versions.CreateModelVersionParams)
    * [`CreateModelVersionParams.release_notes`](wriftai.model_versions.md#wriftai.model_versions.CreateModelVersionParams.release_notes)
    * [`CreateModelVersionParams.schemas`](wriftai.model_versions.md#wriftai.model_versions.CreateModelVersionParams.schemas)
    * [`CreateModelVersionParams.container_image_digest`](wriftai.model_versions.md#wriftai.model_versions.CreateModelVersionParams.container_image_digest)
  * [`ModelVersions`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions)
    * [`ModelVersions.get()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.get)
    * [`ModelVersions.async_get()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.async_get)
    * [`ModelVersions.list()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.list)
    * [`ModelVersions.async_list()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.async_list)
    * [`ModelVersions.delete()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.delete)
    * [`ModelVersions.async_delete()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.async_delete)
    * [`ModelVersions.create()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.create)
    * [`ModelVersions.async_create()`](wriftai.model_versions.md#wriftai.model_versions.ModelVersions.async_create)
* [models module](wriftai.models.md)
  * [`ModelWithDetails`](wriftai.models.md#wriftai.models.ModelWithDetails)
    * [`ModelWithDetails.overview`](wriftai.models.md#wriftai.models.ModelWithDetails.overview)
    * [`ModelWithDetails.latest_version`](wriftai.models.md#wriftai.models.ModelWithDetails.latest_version)
    * [`ModelWithDetails.id`](wriftai.models.md#wriftai.models.ModelWithDetails.id)
    * [`ModelWithDetails.name`](wriftai.models.md#wriftai.models.ModelWithDetails.name)
    * [`ModelWithDetails.created_at`](wriftai.models.md#wriftai.models.ModelWithDetails.created_at)
    * [`ModelWithDetails.visibility`](wriftai.models.md#wriftai.models.ModelWithDetails.visibility)
    * [`ModelWithDetails.description`](wriftai.models.md#wriftai.models.ModelWithDetails.description)
    * [`ModelWithDetails.updated_at`](wriftai.models.md#wriftai.models.ModelWithDetails.updated_at)
    * [`ModelWithDetails.source_url`](wriftai.models.md#wriftai.models.ModelWithDetails.source_url)
    * [`ModelWithDetails.license_url`](wriftai.models.md#wriftai.models.ModelWithDetails.license_url)
    * [`ModelWithDetails.paper_url`](wriftai.models.md#wriftai.models.ModelWithDetails.paper_url)
    * [`ModelWithDetails.owner`](wriftai.models.md#wriftai.models.ModelWithDetails.owner)
    * [`ModelWithDetails.hardware`](wriftai.models.md#wriftai.models.ModelWithDetails.hardware)
    * [`ModelWithDetails.predictions_count`](wriftai.models.md#wriftai.models.ModelWithDetails.predictions_count)
    * [`ModelWithDetails.categories`](wriftai.models.md#wriftai.models.ModelWithDetails.categories)
  * [`ModelsSortBy`](wriftai.models.md#wriftai.models.ModelsSortBy)
    * [`ModelsSortBy.CREATED_AT`](wriftai.models.md#wriftai.models.ModelsSortBy.CREATED_AT)
    * [`ModelsSortBy.PREDICTION_COUNT`](wriftai.models.md#wriftai.models.ModelsSortBy.PREDICTION_COUNT)
  * [`ModelPaginationOptions`](wriftai.models.md#wriftai.models.ModelPaginationOptions)
    * [`ModelPaginationOptions.sort_by`](wriftai.models.md#wriftai.models.ModelPaginationOptions.sort_by)
    * [`ModelPaginationOptions.sort_direction`](wriftai.models.md#wriftai.models.ModelPaginationOptions.sort_direction)
    * [`ModelPaginationOptions.category_slugs`](wriftai.models.md#wriftai.models.ModelPaginationOptions.category_slugs)
    * [`ModelPaginationOptions.cursor`](wriftai.models.md#wriftai.models.ModelPaginationOptions.cursor)
    * [`ModelPaginationOptions.page_size`](wriftai.models.md#wriftai.models.ModelPaginationOptions.page_size)
  * [`UpdateModelParams`](wriftai.models.md#wriftai.models.UpdateModelParams)
    * [`UpdateModelParams.name`](wriftai.models.md#wriftai.models.UpdateModelParams.name)
    * [`UpdateModelParams.description`](wriftai.models.md#wriftai.models.UpdateModelParams.description)
    * [`UpdateModelParams.visibility`](wriftai.models.md#wriftai.models.UpdateModelParams.visibility)
    * [`UpdateModelParams.hardware_identifier`](wriftai.models.md#wriftai.models.UpdateModelParams.hardware_identifier)
    * [`UpdateModelParams.source_url`](wriftai.models.md#wriftai.models.UpdateModelParams.source_url)
    * [`UpdateModelParams.license_url`](wriftai.models.md#wriftai.models.UpdateModelParams.license_url)
    * [`UpdateModelParams.paper_url`](wriftai.models.md#wriftai.models.UpdateModelParams.paper_url)
    * [`UpdateModelParams.overview`](wriftai.models.md#wriftai.models.UpdateModelParams.overview)
    * [`UpdateModelParams.category_slugs`](wriftai.models.md#wriftai.models.UpdateModelParams.category_slugs)
  * [`CreateModelParams`](wriftai.models.md#wriftai.models.CreateModelParams)
    * [`CreateModelParams.name`](wriftai.models.md#wriftai.models.CreateModelParams.name)
    * [`CreateModelParams.hardware_identifier`](wriftai.models.md#wriftai.models.CreateModelParams.hardware_identifier)
    * [`CreateModelParams.visibility`](wriftai.models.md#wriftai.models.CreateModelParams.visibility)
    * [`CreateModelParams.description`](wriftai.models.md#wriftai.models.CreateModelParams.description)
    * [`CreateModelParams.source_url`](wriftai.models.md#wriftai.models.CreateModelParams.source_url)
    * [`CreateModelParams.license_url`](wriftai.models.md#wriftai.models.CreateModelParams.license_url)
    * [`CreateModelParams.paper_url`](wriftai.models.md#wriftai.models.CreateModelParams.paper_url)
    * [`CreateModelParams.overview`](wriftai.models.md#wriftai.models.CreateModelParams.overview)
    * [`CreateModelParams.category_slugs`](wriftai.models.md#wriftai.models.CreateModelParams.category_slugs)
  * [`ModelsResource`](wriftai.models.md#wriftai.models.ModelsResource)
    * [`ModelsResource.delete()`](wriftai.models.md#wriftai.models.ModelsResource.delete)
    * [`ModelsResource.async_delete()`](wriftai.models.md#wriftai.models.ModelsResource.async_delete)
    * [`ModelsResource.list()`](wriftai.models.md#wriftai.models.ModelsResource.list)
    * [`ModelsResource.async_list()`](wriftai.models.md#wriftai.models.ModelsResource.async_list)
    * [`ModelsResource.get()`](wriftai.models.md#wriftai.models.ModelsResource.get)
    * [`ModelsResource.async_get()`](wriftai.models.md#wriftai.models.ModelsResource.async_get)
    * [`ModelsResource.create()`](wriftai.models.md#wriftai.models.ModelsResource.create)
    * [`ModelsResource.async_create()`](wriftai.models.md#wriftai.models.ModelsResource.async_create)
    * [`ModelsResource.update()`](wriftai.models.md#wriftai.models.ModelsResource.update)
    * [`ModelsResource.async_update()`](wriftai.models.md#wriftai.models.ModelsResource.async_update)
    * [`ModelsResource.search()`](wriftai.models.md#wriftai.models.ModelsResource.search)
    * [`ModelsResource.async_search()`](wriftai.models.md#wriftai.models.ModelsResource.async_search)
* [pagination module](wriftai.pagination.md)
  * [`PaginatedResponse`](wriftai.pagination.md#wriftai.pagination.PaginatedResponse)
    * [`PaginatedResponse.items`](wriftai.pagination.md#wriftai.pagination.PaginatedResponse.items)
    * [`PaginatedResponse.next_cursor`](wriftai.pagination.md#wriftai.pagination.PaginatedResponse.next_cursor)
    * [`PaginatedResponse.previous_cursor`](wriftai.pagination.md#wriftai.pagination.PaginatedResponse.previous_cursor)
    * [`PaginatedResponse.next_url`](wriftai.pagination.md#wriftai.pagination.PaginatedResponse.next_url)
    * [`PaginatedResponse.previous_url`](wriftai.pagination.md#wriftai.pagination.PaginatedResponse.previous_url)
* [predictions module](wriftai.predictions.md)
  * [`ErrorSource`](wriftai.predictions.md#wriftai.predictions.ErrorSource)
    * [`ErrorSource.internal`](wriftai.predictions.md#wriftai.predictions.ErrorSource.internal)
    * [`ErrorSource.external`](wriftai.predictions.md#wriftai.predictions.ErrorSource.external)
  * [`Status`](wriftai.predictions.md#wriftai.predictions.Status)
    * [`Status.pending`](wriftai.predictions.md#wriftai.predictions.Status.pending)
    * [`Status.started`](wriftai.predictions.md#wriftai.predictions.Status.started)
    * [`Status.failed`](wriftai.predictions.md#wriftai.predictions.Status.failed)
    * [`Status.succeeded`](wriftai.predictions.md#wriftai.predictions.Status.succeeded)
  * [`TaskError`](wriftai.predictions.md#wriftai.predictions.TaskError)
    * [`TaskError.source`](wriftai.predictions.md#wriftai.predictions.TaskError.source)
    * [`TaskError.message`](wriftai.predictions.md#wriftai.predictions.TaskError.message)
    * [`TaskError.detail`](wriftai.predictions.md#wriftai.predictions.TaskError.detail)
  * [`PredictionModel`](wriftai.predictions.md#wriftai.predictions.PredictionModel)
    * [`PredictionModel.owner`](wriftai.predictions.md#wriftai.predictions.PredictionModel.owner)
    * [`PredictionModel.name`](wriftai.predictions.md#wriftai.predictions.PredictionModel.name)
    * [`PredictionModel.version_number`](wriftai.predictions.md#wriftai.predictions.PredictionModel.version_number)
  * [`Prediction`](wriftai.predictions.md#wriftai.predictions.Prediction)
    * [`Prediction.url`](wriftai.predictions.md#wriftai.predictions.Prediction.url)
    * [`Prediction.id`](wriftai.predictions.md#wriftai.predictions.Prediction.id)
    * [`Prediction.created_at`](wriftai.predictions.md#wriftai.predictions.Prediction.created_at)
    * [`Prediction.status`](wriftai.predictions.md#wriftai.predictions.Prediction.status)
    * [`Prediction.updated_at`](wriftai.predictions.md#wriftai.predictions.Prediction.updated_at)
    * [`Prediction.setup_time`](wriftai.predictions.md#wriftai.predictions.Prediction.setup_time)
    * [`Prediction.execution_time`](wriftai.predictions.md#wriftai.predictions.Prediction.execution_time)
    * [`Prediction.model`](wriftai.predictions.md#wriftai.predictions.Prediction.model)
  * [`PredictionWithIO`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO)
    * [`PredictionWithIO.input`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.input)
    * [`PredictionWithIO.output`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.output)
    * [`PredictionWithIO.logs`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.logs)
    * [`PredictionWithIO.setup_logs`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.setup_logs)
    * [`PredictionWithIO.error`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.error)
    * [`PredictionWithIO.url`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.url)
    * [`PredictionWithIO.id`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.id)
    * [`PredictionWithIO.created_at`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.created_at)
    * [`PredictionWithIO.status`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.status)
    * [`PredictionWithIO.updated_at`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.updated_at)
    * [`PredictionWithIO.setup_time`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.setup_time)
    * [`PredictionWithIO.execution_time`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.execution_time)
    * [`PredictionWithIO.model`](wriftai.predictions.md#wriftai.predictions.PredictionWithIO.model)
  * [`Webhook`](wriftai.predictions.md#wriftai.predictions.Webhook)
    * [`Webhook.url`](wriftai.predictions.md#wriftai.predictions.Webhook.url)
    * [`Webhook.secret`](wriftai.predictions.md#wriftai.predictions.Webhook.secret)
  * [`CreatePredictionParams`](wriftai.predictions.md#wriftai.predictions.CreatePredictionParams)
    * [`CreatePredictionParams.input`](wriftai.predictions.md#wriftai.predictions.CreatePredictionParams.input)
    * [`CreatePredictionParams.webhook`](wriftai.predictions.md#wriftai.predictions.CreatePredictionParams.webhook)
    * [`CreatePredictionParams.validate_input`](wriftai.predictions.md#wriftai.predictions.CreatePredictionParams.validate_input)
  * [`WaitOptions`](wriftai.predictions.md#wriftai.predictions.WaitOptions)
    * [`WaitOptions.on_poll`](wriftai.predictions.md#wriftai.predictions.WaitOptions.on_poll)
  * [`AsyncWaitOptions`](wriftai.predictions.md#wriftai.predictions.AsyncWaitOptions)
    * [`AsyncWaitOptions.on_poll`](wriftai.predictions.md#wriftai.predictions.AsyncWaitOptions.on_poll)
  * [`DEFAULT_WAIT_OPTIONS`](wriftai.predictions.md#wriftai.predictions.DEFAULT_WAIT_OPTIONS)
  * [`DEFAULT_ASYNC_WAIT_OPTIONS`](wriftai.predictions.md#wriftai.predictions.DEFAULT_ASYNC_WAIT_OPTIONS)
  * [`Predictions`](wriftai.predictions.md#wriftai.predictions.Predictions)
    * [`Predictions.get()`](wriftai.predictions.md#wriftai.predictions.Predictions.get)
    * [`Predictions.async_get()`](wriftai.predictions.md#wriftai.predictions.Predictions.async_get)
    * [`Predictions.list()`](wriftai.predictions.md#wriftai.predictions.Predictions.list)
    * [`Predictions.async_list()`](wriftai.predictions.md#wriftai.predictions.Predictions.async_list)
    * [`Predictions.create()`](wriftai.predictions.md#wriftai.predictions.Predictions.create)
    * [`Predictions.async_create()`](wriftai.predictions.md#wriftai.predictions.Predictions.async_create)
    * [`Predictions.wait()`](wriftai.predictions.md#wriftai.predictions.Predictions.wait)
    * [`Predictions.async_wait()`](wriftai.predictions.md#wriftai.predictions.Predictions.async_wait)
* [users module](wriftai.users.md)
  * [`UsersSortBy`](wriftai.users.md#wriftai.users.UsersSortBy)
    * [`UsersSortBy.CREATED_AT`](wriftai.users.md#wriftai.users.UsersSortBy.CREATED_AT)
  * [`UserPaginationOptions`](wriftai.users.md#wriftai.users.UserPaginationOptions)
    * [`UserPaginationOptions.sort_by`](wriftai.users.md#wriftai.users.UserPaginationOptions.sort_by)
    * [`UserPaginationOptions.sort_direction`](wriftai.users.md#wriftai.users.UserPaginationOptions.sort_direction)
    * [`UserPaginationOptions.cursor`](wriftai.users.md#wriftai.users.UserPaginationOptions.cursor)
    * [`UserPaginationOptions.page_size`](wriftai.users.md#wriftai.users.UserPaginationOptions.page_size)
  * [`UsersResource`](wriftai.users.md#wriftai.users.UsersResource)
    * [`UsersResource.get()`](wriftai.users.md#wriftai.users.UsersResource.get)
    * [`UsersResource.async_get()`](wriftai.users.md#wriftai.users.UsersResource.async_get)
    * [`UsersResource.list()`](wriftai.users.md#wriftai.users.UsersResource.list)
    * [`UsersResource.async_list()`](wriftai.users.md#wriftai.users.UsersResource.async_list)
    * [`UsersResource.search()`](wriftai.users.md#wriftai.users.UsersResource.search)
    * [`UsersResource.async_search()`](wriftai.users.md#wriftai.users.UsersResource.async_search)
* [webhook module](wriftai.webhook.md)
  * [`NoSignatureError`](wriftai.webhook.md#wriftai.webhook.NoSignatureError)
  * [`NoTimestampError`](wriftai.webhook.md#wriftai.webhook.NoTimestampError)
  * [`SignatureMismatchError`](wriftai.webhook.md#wriftai.webhook.SignatureMismatchError)
  * [`SignatureVerificationError`](wriftai.webhook.md#wriftai.webhook.SignatureVerificationError)
  * [`TimestampOutsideToleranceError`](wriftai.webhook.md#wriftai.webhook.TimestampOutsideToleranceError)

## Module contents

Package initializer for WriftAI Python Client.

<a id="wriftai.Client"></a>

### *class* Client(api_base_url=None, access_token=None, client_options=None)

Bases: `object`

Initializes a new instance of the Client class.

* **Parameters:**
  * **api_base_url** (*str* *|* *None*) – The base URL for the API. If not provided, it falls back to
    the environment variable WRIFTAI_API_BASE_URL or the default api
    base url.
  * **access_token** (*str* *|* *None*) – Bearer token for authorization. If not provided it falls back
    to the environment variable WRIFTAI_ACCESS_TOKEN.
  * **client_options** ([*ClientOptions*](#wriftai.ClientOptions) *|* *None*) – Additional options such as custom headers and timeout.
    Timeout defaults to 10s on all operations if not specified.

<a id="wriftai.ClientOptions"></a>

### *class* ClientOptions

Bases: `TypedDict`

Typed dictionary for specifying additional client options.

<a id="wriftai.ClientOptions.headers"></a>

#### headers *: dict[str, Any]*

Optional HTTP headers to include in requests.

<a id="wriftai.ClientOptions.timeout"></a>

#### timeout *: Timeout*

Timeout configuration for requests.This should be an instance of
httpx.Timeout.

<a id="wriftai.ClientOptions.transport"></a>

#### transport *: BaseTransport | None*

Optional custom transport for managing HTTP behavior.

<a id="wriftai.PaginationOptions"></a>

### *class* PaginationOptions

Bases: `TypedDict`

Options for pagination.

<a id="wriftai.PaginationOptions.cursor"></a>

#### cursor *: NotRequired[str]*

Cursor for pagination.

<a id="wriftai.PaginationOptions.page_size"></a>

#### page_size *: NotRequired[int]*

Number of items per page.

<a id="wriftai.verify_webhook"></a>

### verify_webhook(payload, signature_header, secret, tolerance=300, scheme='v1')

Verify webhook signature.

* **Parameters:**
  * **payload** (*bytes*) – Payload bytes from the webhook request body.
  * **signature_header** (*str*) – The signature header.
  * **secret** (*str*) – The webhook secret.
  * **tolerance** (*int*) – Maximum allowed age of the timestamp in seconds. Defaults to 300.
  * **scheme** (*str*) – Key for the signatures in signature header. Defaults to “v1”.
* **Raises:**
  * [**NoTimestampError**](wriftai.webhook.md#wriftai.webhook.NoTimestampError) – Error raised when the timestamp is missing from signature
        header.
  * [**NoSignatureError**](wriftai.webhook.md#wriftai.webhook.NoSignatureError) – Error raised when the signatures are missing from signature
        header.
  * [**SignatureMismatchError**](wriftai.webhook.md#wriftai.webhook.SignatureMismatchError) – Error raised when the computed signature does not match
        signatures in header.
  * [**TimestampOutsideToleranceError**](wriftai.webhook.md#wriftai.webhook.TimestampOutsideToleranceError) – Error raised when timestamp is outside the
        tolerance window.
* **Return type:**
  None