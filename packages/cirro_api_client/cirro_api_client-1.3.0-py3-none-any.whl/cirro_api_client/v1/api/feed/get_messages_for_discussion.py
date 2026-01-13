from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.paginated_response_message import PaginatedResponseMessage
from ...models.sort_order import SortOrder
from ...types import UNSET, Response, Unset


def _get_kwargs(
    discussion_id: str,
    *,
    next_token: None | str | Unset = UNSET,
    limit: int | Unset = 5000,
    thread_id: None | str | Unset = UNSET,
    order: None | SortOrder | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_next_token: None | str | Unset
    if isinstance(next_token, Unset):
        json_next_token = UNSET
    else:
        json_next_token = next_token
    params["nextToken"] = json_next_token

    params["limit"] = limit

    json_thread_id: None | str | Unset
    if isinstance(thread_id, Unset):
        json_thread_id = UNSET
    else:
        json_thread_id = thread_id
    params["threadId"] = json_thread_id

    json_order: None | str | Unset
    if isinstance(order, Unset):
        json_order = UNSET
    elif isinstance(order, SortOrder):
        json_order = order.value
    else:
        json_order = order
    params["order"] = json_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/discussions/{discussion_id}/messages".format(
            discussion_id=quote(str(discussion_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> PaginatedResponseMessage | None:
    if response.status_code == 200:
        response_200 = PaginatedResponseMessage.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[PaginatedResponseMessage]:
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
    next_token: None | str | Unset = UNSET,
    limit: int | Unset = 5000,
    thread_id: None | str | Unset = UNSET,
    order: None | SortOrder | Unset = UNSET,
) -> Response[PaginatedResponseMessage]:
    """Get messages for a discussion

     Retrieves all messages associated with a specific discussion

    Args:
        discussion_id (str):
        next_token (None | str | Unset):
        limit (int | Unset):  Default: 5000.
        thread_id (None | str | Unset):
        order (None | SortOrder | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedResponseMessage]
    """

    kwargs = _get_kwargs(
        discussion_id=discussion_id,
        next_token=next_token,
        limit=limit,
        thread_id=thread_id,
        order=order,
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
    next_token: None | str | Unset = UNSET,
    limit: int | Unset = 5000,
    thread_id: None | str | Unset = UNSET,
    order: None | SortOrder | Unset = UNSET,
) -> PaginatedResponseMessage | None:
    """Get messages for a discussion

     Retrieves all messages associated with a specific discussion

    Args:
        discussion_id (str):
        next_token (None | str | Unset):
        limit (int | Unset):  Default: 5000.
        thread_id (None | str | Unset):
        order (None | SortOrder | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedResponseMessage
    """

    try:
        return sync_detailed(
            discussion_id=discussion_id,
            client=client,
            next_token=next_token,
            limit=limit,
            thread_id=thread_id,
            order=order,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    discussion_id: str,
    *,
    client: Client,
    next_token: None | str | Unset = UNSET,
    limit: int | Unset = 5000,
    thread_id: None | str | Unset = UNSET,
    order: None | SortOrder | Unset = UNSET,
) -> Response[PaginatedResponseMessage]:
    """Get messages for a discussion

     Retrieves all messages associated with a specific discussion

    Args:
        discussion_id (str):
        next_token (None | str | Unset):
        limit (int | Unset):  Default: 5000.
        thread_id (None | str | Unset):
        order (None | SortOrder | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedResponseMessage]
    """

    kwargs = _get_kwargs(
        discussion_id=discussion_id,
        next_token=next_token,
        limit=limit,
        thread_id=thread_id,
        order=order,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    discussion_id: str,
    *,
    client: Client,
    next_token: None | str | Unset = UNSET,
    limit: int | Unset = 5000,
    thread_id: None | str | Unset = UNSET,
    order: None | SortOrder | Unset = UNSET,
) -> PaginatedResponseMessage | None:
    """Get messages for a discussion

     Retrieves all messages associated with a specific discussion

    Args:
        discussion_id (str):
        next_token (None | str | Unset):
        limit (int | Unset):  Default: 5000.
        thread_id (None | str | Unset):
        order (None | SortOrder | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedResponseMessage
    """

    try:
        return (
            await asyncio_detailed(
                discussion_id=discussion_id,
                client=client,
                next_token=next_token,
                limit=limit,
                thread_id=thread_id,
                order=order,
            )
        ).parsed
    except errors.NotFoundException:
        return None
