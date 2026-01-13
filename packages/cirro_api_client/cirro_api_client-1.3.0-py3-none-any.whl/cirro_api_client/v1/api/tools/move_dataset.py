from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import Client
from ...models.move_dataset_input import MoveDatasetInput
from ...models.move_dataset_response import MoveDatasetResponse
from ...types import Response


def _get_kwargs(
    *,
    body: MoveDatasetInput,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/tools/move-dataset",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> MoveDatasetResponse | None:
    if response.status_code == 200:
        response_200 = MoveDatasetResponse.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[MoveDatasetResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    body: MoveDatasetInput,
) -> Response[MoveDatasetResponse]:
    """Move a dataset to a different project

     Moves a dataset to a different project. The underlying S3 data is not transferred and will need to
    be done manually. It is expected the user will also transfer all datasets in the lineage.

    Args:
        body (MoveDatasetInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MoveDatasetResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    body: MoveDatasetInput,
) -> MoveDatasetResponse | None:
    """Move a dataset to a different project

     Moves a dataset to a different project. The underlying S3 data is not transferred and will need to
    be done manually. It is expected the user will also transfer all datasets in the lineage.

    Args:
        body (MoveDatasetInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MoveDatasetResponse
    """

    try:
        return sync_detailed(
            client=client,
            body=body,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    *,
    client: Client,
    body: MoveDatasetInput,
) -> Response[MoveDatasetResponse]:
    """Move a dataset to a different project

     Moves a dataset to a different project. The underlying S3 data is not transferred and will need to
    be done manually. It is expected the user will also transfer all datasets in the lineage.

    Args:
        body (MoveDatasetInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[MoveDatasetResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    body: MoveDatasetInput,
) -> MoveDatasetResponse | None:
    """Move a dataset to a different project

     Moves a dataset to a different project. The underlying S3 data is not transferred and will need to
    be done manually. It is expected the user will also transfer all datasets in the lineage.

    Args:
        body (MoveDatasetInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        MoveDatasetResponse
    """

    try:
        return (
            await asyncio_detailed(
                client=client,
                body=body,
            )
        ).parsed
    except errors.NotFoundException:
        return None
