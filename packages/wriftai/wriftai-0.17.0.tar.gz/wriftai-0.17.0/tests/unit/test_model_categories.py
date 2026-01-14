from unittest.mock import AsyncMock, Mock, patch

import pytest

from wriftai.model_categories import ModelCategories
from wriftai.pagination import PaginationOptions


@patch("wriftai.model_categories.PaginatedResponse")
@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_listing(mock_paginated_response: Mock, async_flag: bool) -> None:
    test_response = {"key": "value"}
    pagination_options = PaginationOptions({"cursor": "abc123", "page_size": 50})

    if async_flag:
        mock_api = AsyncMock()
        mock_api.async_request.return_value = test_response
    else:
        mock_api = Mock()
        mock_api.request.return_value = test_response

    model_category = ModelCategories(api=mock_api)

    if async_flag:
        result = await model_category.async_list(pagination_options=pagination_options)
        mock_api.async_request.assert_called_once_with(
            method="GET",
            path="/model_categories",
            params=pagination_options,
        )
    else:
        result = model_category.list(pagination_options=pagination_options)
        mock_api.request.assert_called_once_with(
            method="GET",
            path="/model_categories",
            params=pagination_options,
        )

    mock_paginated_response.assert_called_once_with(**test_response)
    assert result == mock_paginated_response.return_value
