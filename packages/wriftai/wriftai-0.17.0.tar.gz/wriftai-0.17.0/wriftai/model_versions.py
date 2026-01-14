"""Model Versions module."""

from typing import Optional, TypedDict, cast

from wriftai._resource import Resource
from wriftai.common_types import ModelVersion, ModelVersionWithDetails, Schemas
from wriftai.pagination import PaginatedResponse, PaginationOptions


class CreateModelVersionParams(TypedDict):
    """Parameters for creating a version of a model."""

    release_notes: str
    """Information about changes such as new features, bug fixes, or optimizations
        in this model version."""
    schemas: Schemas
    """Schemas for the model version."""
    container_image_digest: str
    """SHA256 hash digest of the model version's container image."""


class ModelVersions(Resource):
    """Resource for operations related to model versions."""

    def get(
        self, model_owner: str, model_name: str, number: int
    ) -> ModelVersionWithDetails:
        """Get a model version.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            number: The number of the model version.

        Returns:
            The model version.
        """
        response = self._api.request(
            "GET",
            f"{self._MODELS_API_PREFIX}/{model_owner}/{model_name}{self._MODEL_VERSIONS_PATH}/{number}",
        )
        return cast(ModelVersionWithDetails, response)

    async def async_get(
        self, model_owner: str, model_name: str, number: int
    ) -> ModelVersionWithDetails:
        """Get a model version.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            number: The number of the model version.

        Returns:
            The model version.
        """
        response = await self._api.async_request(
            "GET",
            f"{self._MODELS_API_PREFIX}/{model_owner}/{model_name}{self._MODEL_VERSIONS_PATH}/{number}",
        )
        return cast(ModelVersionWithDetails, response)

    def list(
        self,
        model_owner: str,
        model_name: str,
        pagination_options: Optional[PaginationOptions] = None,
    ) -> PaginatedResponse[ModelVersion]:
        """List model versions.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            pagination_options: Optional settings to control pagination behavior.

        Returns:
            Paginated response containing model versions and navigation metadata.
        """
        path = (
            f"{self._MODELS_API_PREFIX}/{model_owner}"
            f"/{model_name}{self._MODEL_VERSIONS_PATH}"
        )
        response = self._api.request(method="GET", params=pagination_options, path=path)

        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]

    async def async_list(
        self,
        model_owner: str,
        model_name: str,
        pagination_options: Optional[PaginationOptions] = None,
    ) -> PaginatedResponse[ModelVersion]:
        """List model versions.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            pagination_options: Optional settings to control pagination behavior.

        Returns:
            Paginated response containing model versions and navigation metadata.
        """
        path = (
            f"{self._MODELS_API_PREFIX}/{model_owner}"
            f"/{model_name}{self._MODEL_VERSIONS_PATH}"
        )
        response = await self._api.async_request(
            method="GET", params=pagination_options, path=path
        )
        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]

    def delete(self, model_owner: str, model_name: str, number: int) -> None:
        """Delete a model version.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            number: The number of the model version.
        """
        self._api.request(
            "DELETE",
            f"{self._MODELS_API_PREFIX}/{model_owner}/{model_name}{self._MODEL_VERSIONS_PATH}/{number}",
        )

    async def async_delete(
        self, model_owner: str, model_name: str, number: int
    ) -> None:
        """Delete a model version.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            number: The number of the model version.
        """
        await self._api.async_request(
            "DELETE",
            f"{self._MODELS_API_PREFIX}/{model_owner}/{model_name}{self._MODEL_VERSIONS_PATH}/{number}",
        )

    def create(
        self,
        model_owner: str,
        model_name: str,
        options: CreateModelVersionParams,
    ) -> ModelVersionWithDetails:
        """Create a version of a model.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            options: Model's version creation parameters.

        Returns:
            The new model version.
        """
        path = (
            f"{self._MODELS_API_PREFIX}/{model_owner}"
            f"/{model_name}{self._MODEL_VERSIONS_PATH}"
        )
        response = self._api.request(
            "POST",
            path,
            # The params matches JsonValue at runtime,
            # but static type checkers may not infer this correctly.
            # Hence, we ignore the argument type warning.
            body=options,  # type:ignore[arg-type]
        )
        return cast(ModelVersionWithDetails, response)

    async def async_create(
        self,
        model_owner: str,
        model_name: str,
        options: CreateModelVersionParams,
    ) -> ModelVersionWithDetails:
        """Create a version of a model.

        Args:
            model_owner: Username of the model's owner.
            model_name: Name of the model.
            options: Model's version creation parameters.

        Returns:
            The new model version.
        """
        path = (
            f"{self._MODELS_API_PREFIX}/{model_owner}"
            f"/{model_name}{self._MODEL_VERSIONS_PATH}"
        )
        response = await self._api.async_request(
            "POST",
            path,
            # The params matches JsonValue at runtime,
            # but static type checkers may not infer this correctly.
            # Hence, we ignore the argument type warning.
            body=options,  # type:ignore[arg-type]
        )
        return cast(ModelVersionWithDetails, response)
