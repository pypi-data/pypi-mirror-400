import json
from typing import Callable

import httpx
import pytest
from respx import Router

from tests.integration.conftest import Route
from wriftai import Client, ClientOptions
from wriftai.model_versions import CreateModelVersionParams
from wriftai.pagination import PaginatedResponse, PaginationOptions


@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_get(mock_router: Callable[..., Router], async_flag: bool) -> None:
    model_owner = "deepseek-ai"
    model_name = "deepseek-r1"
    number = 1
    expected_json = {
        "number": 1,
        "release_notes": (
            "Information about changes such as new features,"
            "bug fixes, or optimizations in this version."
        ),
        "created_at": "2025-08-29T11:48:44.371093Z",
        "schemas": {
            "prediction": {
                "input": {"key1": "value1", "key2": 123},
                "output": {"result": True, "message": "Success"},
            }
        },
        "container_image_digest": (
            "94a00394bc5a8ef503fb59db0a7d0ae9e1110866e8aee8ba40cd864cea69ea1a"
        ),
    }

    call_count = 0

    def request_assertions(request: httpx.Request) -> None:
        nonlocal call_count
        call_count += 1

    router = mock_router(
        route=Route(
            method="GET",
            path=f"/models/{model_owner}/{model_name}/versions/{number}",
            status_code=200,
            json=expected_json,
        ),
        callback=request_assertions,
    )

    client = Client(
        client_options=ClientOptions(
            headers={"Authorization": "test-token"},
            timeout=httpx.Timeout(15),
            transport=httpx.MockTransport(router.handler),
        )
    )

    if async_flag:
        response = await client.model_versions.async_get(
            model_owner=model_owner, model_name=model_name, number=number
        )
    else:
        response = client.model_versions.get(
            model_owner=model_owner, model_name=model_name, number=number
        )

    assert response == expected_json
    assert call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_list(mock_router: Callable[..., Router], async_flag: bool) -> None:
    model_owner = "abc"
    model_name = "textgenerator"
    expected_cursor = "abc123"
    expected_page_size = "10"
    expected_json = {
        "items": [
            {
                "number": 1,
                "release_notes": (
                    "Information about changes such as new features,"
                    "bug fixes, or optimizations in this version."
                ),
                "created_at": "2025-08-29T11:48:44.371093Z",
                "container_image_digest": (
                    "94a00394bc5a8ef503fb59db0a7d0ae9e1110866e8aee8ba40cd864cea69ea1a"
                ),
            }
        ],
        "next_cursor": "abc123",
        "previous_cursor": None,
        "next_url": f"/models/{model_owner}/{model_name}/versions?cursor=abc123",
        "previous_url": None,
    }

    call_count = 0

    def request_assertions(request: httpx.Request) -> None:
        nonlocal call_count
        call_count += 1
        assert request.url.params.get("cursor") == expected_cursor
        assert request.url.params.get("page_size") == expected_page_size
        assert set(request.url.params.keys()).issubset({"cursor", "page_size"})

    router = mock_router(
        route=Route(
            method="GET",
            path=f"/models/{model_owner}/{model_name}/versions",
            status_code=200,
            json=expected_json,
        ),
        callback=request_assertions,
    )

    client = Client(
        client_options=ClientOptions(
            headers={"Authorization": "test-token"},
            timeout=httpx.Timeout(15),
            transport=httpx.MockTransport(router.handler),
        )
    )

    pagination_options = PaginationOptions({
        "cursor": expected_cursor,
        "page_size": int(expected_page_size),
    })

    if async_flag:
        response = await client.model_versions.async_list(
            model_owner=model_owner,
            model_name=model_name,
            pagination_options=pagination_options,
        )
    else:
        response = client.model_versions.list(
            model_owner=model_owner,
            model_name=model_name,
            pagination_options=pagination_options,
        )

    # expected_json is a dictionary.
    # Although the structure matches the expected fields, static type checkers like mypy
    # may not be able to verify this due to dynamic typing.
    assert response == PaginatedResponse(**expected_json)  # type:ignore[arg-type]
    assert call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_delete(mock_router: Callable[..., Router], async_flag: bool) -> None:
    model_owner = "deepseek-ai"
    model_name = "deepseek-r1"
    number = 1

    call_count = 0

    def request_assertions(request: httpx.Request) -> None:
        nonlocal call_count
        call_count += 1

    router = mock_router(
        route=Route(
            method="DELETE",
            path=f"/models/{model_owner}/{model_name}/versions/{number}",
            status_code=204,
            json={},
        ),
        callback=request_assertions,
    )

    client = Client(
        client_options=ClientOptions(
            headers={"Authorization": "test-token"},
            timeout=httpx.Timeout(15),
            transport=httpx.MockTransport(router.handler),
        )
    )

    if async_flag:
        await client.model_versions.async_delete(
            model_owner=model_owner, model_name=model_name, number=number
        )
    else:
        client.model_versions.delete(
            model_owner=model_owner, model_name=model_name, number=number
        )
    assert call_count == 1


@pytest.mark.parametrize("async_flag", [True, False])
@pytest.mark.asyncio
async def test_create(mock_router: Callable[..., Router], async_flag: bool) -> None:
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

    expected_json = {
        "number": 1,
        "release_notes": options["release_notes"],
        "created_at": "2025-08-29T11:48:44.371093Z",
        "schemas": options["schemas"],
        "container_image_digest": options["container_image_digest"],
    }

    call_count = 0

    def request_assertions(request: httpx.Request) -> None:
        nonlocal call_count
        call_count += 1
        json_payload = json.loads(request.content.decode())
        assert json_payload == options

    router = mock_router(
        route=Route(
            method="POST",
            path=f"/models/{model_owner}/{model_name}/versions",
            status_code=200,
            json=expected_json,
        ),
        callback=request_assertions,
    )

    client = Client(
        client_options=ClientOptions(
            headers={"Authorization": "test-token"},
            timeout=httpx.Timeout(15),
            transport=httpx.MockTransport(router.handler),
        )
    )

    if async_flag:
        response = await client.model_versions.async_create(
            model_owner=model_owner,
            model_name=model_name,
            options=options,
        )
    else:
        response = client.model_versions.create(
            model_owner=model_owner,
            model_name=model_name,
            options=options,
        )

    assert response == expected_json
    assert call_count == 1
