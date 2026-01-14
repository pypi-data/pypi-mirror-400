from unittest.mock import AsyncMock, Mock, patch

import pytest

from wriftai.model_versions import CreateModelVersionParams, ModelVersions
from wriftai.pagination import PaginationOptions


def test_get() -> None:
    mock_api = Mock()

    model_version = ModelVersions(api=mock_api)
    model_owner = "deepseek-ai"
    model_name = "deepseek-r1"
    number = 1

    result = model_version.get(
        model_owner=model_owner, model_name=model_name, number=number
    )

    mock_api.request.assert_called_once_with(
        "GET",
        f"{model_version._MODELS_API_PREFIX}/{model_owner}/{model_name}{model_version._MODEL_VERSIONS_PATH}/{number}",
    )
    assert result == mock_api.request.return_value


@pytest.mark.asyncio
async def test_async_get() -> None:
    mock_api = Mock()
    mock_api.async_request = AsyncMock()

    model_version = ModelVersions(api=mock_api)
    model_owner = "deepseek-ai"
    model_name = "deepseek-r1"
    number = 1

    result = await model_version.async_get(
        model_owner=model_owner, model_name=model_name, number=number
    )

    mock_api.async_request.assert_called_once_with(
        "GET",
        f"{model_version._MODELS_API_PREFIX}/{model_owner}/{model_name}{model_version._MODEL_VERSIONS_PATH}/{number}",
    )
    assert result == mock_api.async_request.return_value


@patch("wriftai.model_versions.PaginatedResponse")
def test_list(mock_paginated_response: Mock) -> None:
    mock_api = Mock()
    test_response = {"key": "value"}
    mock_api.request.return_value = test_response

    versions = ModelVersions(api=mock_api)
    pagination_options = PaginationOptions({"cursor": "abc123", "page_size": 50})
    model_owner = "abc"
    model_name = "textgenerator"

    result = versions.list(
        model_owner=model_owner,
        model_name=model_name,
        pagination_options=pagination_options,
    )
    path = (
        f"{versions._MODELS_API_PREFIX}/{model_owner}"
        f"/{model_name}{versions._MODEL_VERSIONS_PATH}"
    )
    mock_api.request.assert_called_once_with(
        method="GET", path=path, params=pagination_options
    )
    mock_paginated_response.assert_called_once_with(**test_response)
    assert result == mock_paginated_response.return_value


@patch("wriftai.model_versions.PaginatedResponse")
@pytest.mark.asyncio
async def test_async_list(mock_paginated_response: Mock) -> None:
    mock_api = AsyncMock()
    test_response = {"key": "value"}
    mock_api.async_request.return_value = test_response

    versions = ModelVersions(api=mock_api)
    pagination_options = PaginationOptions({"cursor": "abc123", "page_size": 50})
    model_owner = "abc"
    model_name = "textgenerator"

    result = await versions.async_list(
        model_owner=model_owner,
        model_name=model_name,
        pagination_options=pagination_options,
    )

    path = (
        f"{versions._MODELS_API_PREFIX}/{model_owner}"
        f"/{model_name}{versions._MODEL_VERSIONS_PATH}"
    )
    mock_api.async_request.assert_called_once_with(
        method="GET", path=path, params=pagination_options
    )
    mock_paginated_response.assert_called_once_with(**test_response)
    assert result == mock_paginated_response.return_value


def test_delete() -> None:
    mock_api = Mock()

    model_version = ModelVersions(api=mock_api)
    model_owner = "deepseek-ai"
    model_name = "deepseek-r1"
    number = 1

    model_version.delete(model_owner=model_owner, model_name=model_name, number=number)

    mock_api.request.assert_called_once_with(
        "DELETE",
        f"{model_version._MODELS_API_PREFIX}/{model_owner}/{model_name}{model_version._MODEL_VERSIONS_PATH}/{number}",
    )


@pytest.mark.asyncio
async def test_async_delete() -> None:
    mock_api = Mock()
    mock_api.async_request = AsyncMock()

    model_version = ModelVersions(api=mock_api)
    model_owner = "deepseek-ai"
    model_name = "deepseek-r1"
    number = 1

    await model_version.async_delete(
        model_owner=model_owner, model_name=model_name, number=number
    )

    mock_api.async_request.assert_called_once_with(
        "DELETE",
        f"{model_version._MODELS_API_PREFIX}/{model_owner}/{model_name}{model_version._MODEL_VERSIONS_PATH}/{number}",
    )


def test_create() -> None:
    mock_api = Mock()

    model = ModelVersions(api=mock_api)

    model_owner = "abc"
    model_name = "textgenerator"
    options: CreateModelVersionParams = {
        "release_notes": "Initial release with basic features",
        "container_image_digest": "sha256:" + "a" * 64,
        "schemas": {
            "prediction": {
                "input": {"key1": "value1", "key2": 123},
                "output": {"result": True, "message": "Success"},
            }
        },
    }

    result = model.create(
        model_owner=model_owner,
        model_name=model_name,
        options=options,
    )
    path = (
        f"{model._MODELS_API_PREFIX}/{model_owner}"
        f"/{model_name}{model._MODEL_VERSIONS_PATH}"
    )
    mock_api.request.assert_called_once_with(
        "POST",
        path,
        body=options,
    )

    assert result == mock_api.request.return_value


@pytest.mark.asyncio
async def test_async_create() -> None:
    mock_api = Mock()
    mock_api.async_request = AsyncMock()

    model = ModelVersions(api=mock_api)

    model_owner = "abc"
    model_name = "textgenerator"
    options: CreateModelVersionParams = {
        "release_notes": "Initial release with basic features",
        "container_image_digest": "sha256:" + "a" * 64,
        "schemas": {
            "prediction": {
                "input": {"key1": "value1", "key2": 123},
                "output": {"result": True, "message": "Success"},
            }
        },
    }

    result = await model.async_create(
        model_owner=model_owner,
        model_name=model_name,
        options=options,
    )

    path = (
        f"{model._MODELS_API_PREFIX}/{model_owner}"
        f"/{model_name}{model._MODEL_VERSIONS_PATH}"
    )

    mock_api.async_request.assert_called_once_with(
        "POST",
        path,
        body=options,
    )

    assert result == mock_api.async_request.return_value
