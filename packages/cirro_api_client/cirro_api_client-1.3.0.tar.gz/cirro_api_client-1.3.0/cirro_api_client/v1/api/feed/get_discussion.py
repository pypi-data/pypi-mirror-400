from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.discussion import Discussion
from ...types import Response


def _get_kwargs(
    discussion_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/discussions/{discussion_id}".format(
            discussion_id=quote(str(discussion_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Discussion | None:
    if response.status_code == 200:
        response_200 = Discussion.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[Discussion]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    discussion_id: str,
    *,
    client: Client,
) -> Response[Discussion]:
    """Get a discussion

     Retrieves a discussion by its ID

    Args:
        discussion_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Discussion]
    """

    kwargs = _get_kwargs(
        discussion_id=discussion_id,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    discussion_id: str,
    *,
    client: Client,
) -> Discussion | None:
    """Get a discussion

     Retrieves a discussion by its ID

    Args:
        discussion_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Discussion
    """

    try:
        return sync_detailed(
            discussion_id=discussion_id,
            client=client,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    discussion_id: str,
    *,
    client: Client,
) -> Response[Discussion]:
    """Get a discussion

     Retrieves a discussion by its ID

    Args:
        discussion_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Discussion]
    """

    kwargs = _get_kwargs(
        discussion_id=discussion_id,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    discussion_id: str,
    *,
    client: Client,
) -> Discussion | None:
    """Get a discussion

     Retrieves a discussion by its ID

    Args:
        discussion_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Discussion
    """

    try:
        return (
            await asyncio_detailed(
                discussion_id=discussion_id,
                client=client,
            )
        ).parsed
    except errors.NotFoundException:
        return None
