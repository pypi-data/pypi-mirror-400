from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...types import Response


def _get_kwargs(
    discussion_id: str,
    message_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/discussions/{discussion_id}/messages/{message_id}".format(
            discussion_id=quote(str(discussion_id), safe=""),
            message_id=quote(str(message_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Any | None:
    if response.status_code == 200:
        return None

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    discussion_id: str,
    message_id: str,
    *,
    client: Client,
) -> Response[Any]:
    """Delete a message

     Deletes a message from a discussion

    Args:
        discussion_id (str):
        message_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        discussion_id=discussion_id,
        message_id=message_id,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    discussion_id: str,
    message_id: str,
    *,
    client: Client,
) -> Response[Any]:
    """Delete a message

     Deletes a message from a discussion

    Args:
        discussion_id (str):
        message_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        discussion_id=discussion_id,
        message_id=message_id,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)
