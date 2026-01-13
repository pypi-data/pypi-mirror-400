from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import Client
from ...models.project_create_options import ProjectCreateOptions
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/options",
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> ProjectCreateOptions | None:
    if response.status_code == 200:
        response_200 = ProjectCreateOptions.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[ProjectCreateOptions]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
) -> Response[ProjectCreateOptions]:
    """Get project create options

     Get allowed options for creating a project

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProjectCreateOptions]
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
) -> ProjectCreateOptions | None:
    """Get project create options

     Get allowed options for creating a project

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProjectCreateOptions
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
) -> Response[ProjectCreateOptions]:
    """Get project create options

     Get allowed options for creating a project

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProjectCreateOptions]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
) -> ProjectCreateOptions | None:
    """Get project create options

     Get allowed options for creating a project

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProjectCreateOptions
    """

    try:
        return (
            await asyncio_detailed(
                client=client,
            )
        ).parsed
    except errors.NotFoundException:
        return None
