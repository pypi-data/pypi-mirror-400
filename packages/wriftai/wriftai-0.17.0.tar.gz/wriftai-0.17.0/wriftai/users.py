"""User module."""

from typing import Optional, cast

from wriftai._resource import Resource
from wriftai.common_types import (
    NotRequired,
    SortDirection,
    StrEnum,
    UserWithDetails,
)
from wriftai.pagination import PaginatedResponse, PaginationOptions


class UsersSortBy(StrEnum):
    """Enumeration of possible sorting options for querying users."""

    CREATED_AT = "created_at"


class UserPaginationOptions(PaginationOptions):
    """Pagination options for querying users."""

    sort_by: NotRequired[UsersSortBy]
    """The sorting criteria."""

    sort_direction: NotRequired[SortDirection]
    """The sorting direction."""


class UsersResource(Resource):
    """Resource for operations related to users."""

    _API_PREFIX = "/users"
    _SEARCH_USERS_SUFFIX = "/users"

    def get(self, username: str) -> UserWithDetails:
        """Fetch a user by their username.

        Args:
            username: The username of the user.

        Returns:
            The user object.
        """
        response = self._api.request("GET", f"{self._API_PREFIX}/{username}")
        return cast(UserWithDetails, response)

    async def async_get(self, username: str) -> UserWithDetails:
        """Fetch a user by their username.

        Args:
            username: The username of the user.

        Returns:
            The user object.
        """
        response = await self._api.async_request(
            "GET", f"{self._API_PREFIX}/{username}"
        )
        return cast(UserWithDetails, response)

    def list(
        self, pagination_options: Optional[UserPaginationOptions] = None
    ) -> PaginatedResponse[UserWithDetails]:
        """List users.

        Args:
            pagination_options: Optional settings to control pagination behavior.

        Returns:
            Paginated response containing users and navigation metadata.
        """
        response = self._api.request(
            method="GET", params=pagination_options, path=self._API_PREFIX
        )

        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]

    async def async_list(
        self, pagination_options: Optional[UserPaginationOptions] = None
    ) -> PaginatedResponse[UserWithDetails]:
        """List users.

        Args:
            pagination_options: Optional settings to control pagination behavior.

        Returns:
            Paginated response containing users and navigation metadata.
        """
        response = await self._api.async_request(
            method="GET", params=pagination_options, path=self._API_PREFIX
        )
        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]

    def search(
        self, q: str, pagination_options: Optional[PaginationOptions] = None
    ) -> PaginatedResponse[UserWithDetails]:
        """Search users.

        Args:
            q: The search query.
            pagination_options: Optional settings to control pagination behavior.

        Returns:
            Paginated response containing users and navigation metadata.
        """
        params = self._build_search_params(q, pagination_options)

        response = self._api.request(
            method="GET",
            params=params,
            path=f"{self._SEARCH_API_PREFIX}{self._SEARCH_USERS_SUFFIX}",
        )
        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]

    async def async_search(
        self, q: str, pagination_options: Optional[PaginationOptions] = None
    ) -> PaginatedResponse[UserWithDetails]:
        """Search Users.

        Args:
            q: The search query.
            pagination_options: Optional settings to control pagintation behavior.

        Returns:
            Paginated response containing users and navigation metadata.
        """
        params = self._build_search_params(q, pagination_options)

        response = await self._api.async_request(
            method="GET",
            params=params,
            path=f"{self._SEARCH_API_PREFIX}{self._SEARCH_USERS_SUFFIX}",
        )
        # The response will always match the PaginatedResponse structure,
        # but static type checkers may not infer this correctly.
        # Hence, we ignore the argument type warning.
        return PaginatedResponse(**response)  # type:ignore[arg-type]
