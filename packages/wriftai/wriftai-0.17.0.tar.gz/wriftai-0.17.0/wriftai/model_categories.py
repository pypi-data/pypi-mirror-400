"""Model categories module."""

from typing import Optional

from wriftai._resource import Resource
from wriftai.common_types import ModelCategory
from wriftai.pagination import PaginatedResponse, PaginationOptions


class ModelCategoryWithDetails(ModelCategory):
    """Represents a model category with details."""

    description: str
    """Description of the model category."""


class ModelCategories(Resource):
    """Resource for operations related to model categories."""

    def list(
        self, pagination_options: Optional[PaginationOptions]
    ) -> PaginatedResponse[ModelCategoryWithDetails]:
        """List model categories.

        Args:
            pagination_options: Optional settings to control pagination behavior.

        Returns:
            Paginated response containing model category items and navigation metadata.
        """
        response = self._api.request(
            method="GET", params=pagination_options, path="/model_categories"
        )

        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]

    async def async_list(
        self, pagination_options: Optional[PaginationOptions]
    ) -> PaginatedResponse[ModelCategoryWithDetails]:
        """List model categories.

        Args:
            pagination_options: Optional settings to control pagination behavior.

        Returns:
            Paginated response containing model category items and navigation metadata.
        """
        response = await self._api.async_request(
            method="GET", params=pagination_options, path="/model_categories"
        )

        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]
