from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import Client
from ...models.system_info_response import SystemInfoResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/info",
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> SystemInfoResponse | None:
    if response.status_code == 200:
        response_200 = SystemInfoResponse.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[SystemInfoResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
) -> Response[SystemInfoResponse]:
    """Get system info

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SystemInfoResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
) -> SystemInfoResponse | None:
    """Get system info

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SystemInfoResponse
    """

    try:
        return sync_detailed(
            client=client,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    *,
    client: Client,
) -> Response[SystemInfoResponse]:
    """Get system info

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SystemInfoResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
) -> SystemInfoResponse | None:
    """Get system info

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SystemInfoResponse
    """

    try:
        return (
            await asyncio_detailed(
                client=client,
            )
        ).parsed
    except errors.NotFoundException:
        return None
