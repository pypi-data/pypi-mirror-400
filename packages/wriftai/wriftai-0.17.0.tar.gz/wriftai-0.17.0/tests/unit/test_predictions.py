from copy import copy
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from wriftai.predictions import (
    AsyncWaitOptions,
    CreatePredictionParams,
    PredictionModel,
    Predictions,
    PredictionWithIO,
    Status,
    WaitOptions,
)


def test_get() -> None:
    test_prediction_id = "test_id"
    mock_api = Mock()
    mock_api.request = Mock()

    predictions = Predictions(api=mock_api)

    result = predictions.get(test_prediction_id)

    mock_api.request.assert_called_once_with(
        method="GET", path=f"{predictions._API_PREFIX}/{test_prediction_id}"
    )

    assert result == mock_api.request.return_value


@pytest.mark.asyncio
async def test_async_get() -> None:
    test_prediction_id = "test_id"
    mock_api = Mock()
    mock_api.async_request = AsyncMock()

    predictions = Predictions(api=mock_api)

    result = await predictions.async_get(test_prediction_id)

    mock_api.async_request.assert_awaited_once_with(
        method="GET", path=f"{predictions._API_PREFIX}/{test_prediction_id}"
    )

    assert result == mock_api.async_request.return_value


@pytest.mark.parametrize("validate_input", [True, False])
@pytest.mark.parametrize("wait", [True, False])
def test_create(validate_input: bool, wait: bool) -> None:
    mock_api = Mock()
    predictions = Predictions(api=mock_api)

    params: CreatePredictionParams = {
        "input": {"key": "value"},
        "webhook": {
            "url": "https://example.com/webhook",
            "secret": "some webhook secret",
        },
    }

    if validate_input:
        params["validate_input"] = validate_input

    path = "/models/test_owner/test_model/predictions"
    mock_prediction = {"id": "pred-123", "status": "succeeded"}
    wait_options = WaitOptions(poll_interval=2)

    with (
        patch.object(predictions, "wait", return_value=mock_prediction) as mock_wait,
    ):
        mock_api.request.return_value = mock_prediction

        result = predictions.create(
            model="test_owner/test_model",
            params=params,
            wait=wait,
            wait_options=wait_options,
        )

        headers = {"Validate-Input": "true"} if validate_input else None

        mock_api.request.assert_called_once_with(
            method="POST",
            path=path,
            body={"input": params["input"], "webhook": params["webhook"]},
            headers=headers,
        )

        if wait:
            mock_wait.assert_called_once_with(
                mock_prediction["id"], options=wait_options
            )
        else:
            mock_wait.assert_not_called()

        assert result == mock_api.request.return_value


@pytest.mark.asyncio
@pytest.mark.parametrize("validate_input", [True, False])
@pytest.mark.parametrize("wait", [True, False])
async def test_async_create(validate_input: bool, wait: bool) -> None:
    mock_api = Mock()
    mock_api.async_request = AsyncMock()
    predictions = Predictions(api=mock_api)

    params: CreatePredictionParams = {
        "input": {"key": "value"},
        "webhook": {
            "url": "https://example.com/webhook",
            "secret": "some webhook secret",
        },
    }
    if validate_input:
        params["validate_input"] = validate_input

    model = "owner/name:1"
    path = "/models/owner/name/versions/1/predictions"
    mock_prediction = {"id": "pred-123", "status": "succeeded"}
    wait_options = AsyncWaitOptions(poll_interval=2)

    with (
        patch.object(
            predictions, "async_wait", return_value=mock_prediction
        ) as mock_wait,
    ):
        mock_api.async_request.return_value = mock_prediction

        result = await predictions.async_create(
            model=model, params=params, wait=wait, wait_options=wait_options
        )

        headers = {"Validate-Input": "true"} if validate_input else None

        mock_api.async_request.assert_awaited_once_with(
            method="POST",
            path=path,
            body={"input": params["input"], "webhook": params["webhook"]},
            headers=headers,
        )

        if wait:
            mock_wait.assert_called_once_with(
                mock_prediction["id"], options=wait_options
            )
        else:
            mock_wait.assert_not_called()

        assert result == mock_api.async_request.return_value


@pytest.mark.parametrize(
    "status_sequence, expected_calls",
    [
        ([Status.pending, Status.started, Status.succeeded], 3),
        ([Status.succeeded], 1),
        ([Status.failed], 1),
    ],
)
@patch("time.sleep", return_value=None)
def test_wait(
    mock_sleep: Mock,
    status_sequence: list[Status],
    expected_calls: int,
) -> None:
    options = WaitOptions(poll_interval=2)
    base_prediction = PredictionWithIO(
        url="https://example.com",
        id="test_id",
        created_at="2025-08-15T14:30:00Z",
        status=status_sequence[0],
        updated_at="2025-08-15T14:30:00Z",
        setup_time=None,
        execution_time=None,
        error=None,
        input={},
        output={},
        logs=None,
        setup_logs=None,
        model=PredictionModel(
            owner="model owner",
            name="model name",
            version_number=1,
        ),
    )

    predictions = Predictions(api=Mock())

    responses = []
    for status in status_sequence:
        p = copy(base_prediction)
        p["status"] = status
        responses.append(p)

    with patch.object(predictions, "get", side_effect=responses) as mock_get:
        result = predictions.wait(base_prediction["id"], options=options)

    assert result["status"] == status_sequence[-1]
    assert mock_get.call_count == expected_calls
    assert mock_sleep.call_count == max(0, expected_calls - 1)
    mock_sleep.assert_has_calls(
        [call(options.poll_interval)] * max(0, expected_calls - 1)
    )


@pytest.mark.parametrize(
    "status_sequence, expected_calls",
    [
        ([Status.pending, Status.started, Status.succeeded], 3),
        ([Status.succeeded], 1),
        ([Status.failed], 1),
    ],
)
@patch("asyncio.sleep", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_wait(
    mock_sleep: AsyncMock,
    status_sequence: list[Status],
    expected_calls: int,
) -> None:
    options = AsyncWaitOptions(poll_interval=2)
    base_prediction = PredictionWithIO(
        url="https://example.com",
        id="test_id",
        created_at="2025-08-15T14:30:00Z",
        status=status_sequence[0],
        updated_at="2025-08-15T14:30:00Z",
        setup_time=None,
        execution_time=None,
        error=None,
        input={},
        output={},
        logs=None,
        setup_logs=None,
        model=PredictionModel(
            owner="model owner",
            name="model name",
            version_number=1,
        ),
    )

    predictions = Predictions(api=Mock())

    responses = []
    for status in status_sequence:
        p = copy(base_prediction)
        p["status"] = status
        responses.append(p)

    with patch.object(predictions, "async_get", side_effect=responses) as mock_get:
        result = await predictions.async_wait(base_prediction["id"], options=options)

    assert result["status"] == status_sequence[-1]
    assert mock_get.call_count == expected_calls
    assert mock_sleep.await_count == max(0, expected_calls - 1)
    mock_sleep.assert_has_awaits(
        [call(options.poll_interval)] * max(0, expected_calls - 1)
    )


@patch("time.sleep", return_value=None)
def test_on_poll_called(mock_sleep: Mock) -> None:
    statuses = [Status.pending, Status.started, Status.succeeded]
    expected_calls = 3

    base_prediction = PredictionWithIO(
        url="https://example.com",
        id="test_id",
        created_at="2025-08-15T14:30:00Z",
        status=Status.pending,
        updated_at="2025-08-15T14:30:00Z",
        setup_time=None,
        execution_time=None,
        error=None,
        input={},
        output={},
        logs=None,
        setup_logs=None,
        model=PredictionModel(
            owner="model owner",
            name="model name",
            version_number=1,
        ),
    )

    predictions = Predictions(api=Mock())

    responses = []
    for status in statuses:
        p = copy(base_prediction)
        p["status"] = status
        responses.append(p)

    received_predictions = []

    def on_poll(prediction: PredictionWithIO) -> None:
        received_predictions.append(prediction)

    options = WaitOptions(poll_interval=0.5, on_poll=on_poll)

    with patch.object(predictions, "get", side_effect=responses) as mock_get:
        result = predictions.wait(base_prediction["id"], options=options)

    assert result["status"] == statuses[-1]
    assert mock_get.call_count == expected_calls
    assert len(received_predictions) == expected_calls
    for i, prediction in enumerate(received_predictions):
        assert prediction["status"] == statuses[i]


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_async_on_poll_called(mock_sleep: AsyncMock) -> None:
    statuses = [Status.pending, Status.started, Status.succeeded]
    expected_calls = 3

    base_prediction = PredictionWithIO(
        url="https://example.com",
        id="test_id",
        created_at="2025-08-15T14:30:00Z",
        status=Status.pending,
        updated_at="2025-08-15T14:30:00Z",
        setup_time=None,
        execution_time=None,
        error=None,
        input={},
        output={},
        logs=None,
        setup_logs=None,
        model=PredictionModel(
            owner="model owner",
            name="model name",
            version_number=1,
        ),
    )

    predictions = Predictions(api=Mock())

    responses = []
    for status in statuses:
        p = copy(base_prediction)
        p["status"] = status
        responses.append(p)

    received_predictions = []

    async def on_poll(prediction: PredictionWithIO) -> None:
        received_predictions.append(prediction)

    options = AsyncWaitOptions(poll_interval=0.5, on_poll=on_poll)

    with patch.object(predictions, "async_get", side_effect=responses) as mock_get:
        result = await predictions.async_wait(base_prediction["id"], options=options)

    assert result["status"] == statuses[-1]
    assert mock_get.call_count == expected_calls
    assert len(received_predictions) == expected_calls
    for i, prediction in enumerate(received_predictions):
        assert prediction["status"] == statuses[i]


@pytest.mark.parametrize(
    "invalid_model",
    ["invalidformat", "/modelname", "owner/", "owner/name:"],
)
def test_parse_model_raises_erro(invalid_model: str) -> None:
    mock_api = Mock()
    prediction = Predictions(api=mock_api)

    with pytest.raises(ValueError) as e:
        prediction._parse_model(model=invalid_model)

    assert str(e.value) == prediction._ERROR_MSG_INVALID_MODEL
