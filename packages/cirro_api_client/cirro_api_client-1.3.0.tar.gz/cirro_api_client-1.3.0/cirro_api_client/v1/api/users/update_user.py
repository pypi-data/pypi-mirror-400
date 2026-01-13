from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.update_user_request import UpdateUserRequest
from ...models.user import User
from ...types import Response


def _get_kwargs(
    username: str,
    *,
    body: UpdateUserRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/users/{username}".format(
            username=quote(str(username), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> User | None:
    if response.status_code == 200:
        response_200 = User.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[User]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    username: str,
    *,
    client: Client,
    body: UpdateUserRequest,
) -> Response[User]:
    """Update user

     Update user information

    Args:
        username (str):
        body (UpdateUserRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[User]
    """

    kwargs = _get_kwargs(
        username=username,
        body=body,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    username: str,
    *,
    client: Client,
    body: UpdateUserRequest,
) -> User | None:
    """Update user

     Update user information

    Args:
        username (str):
        body (UpdateUserRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        User
    """

    try:
        return sync_detailed(
            username=username,
            client=client,
            body=body,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    username: str,
    *,
    client: Client,
    body: UpdateUserRequest,
) -> Response[User]:
    """Update user

     Update user information

    Args:
        username (str):
        body (UpdateUserRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[User]
    """

    kwargs = _get_kwargs(
        username=username,
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    username: str,
    *,
    client: Client,
    body: UpdateUserRequest,
) -> User | None:
    """Update user

     Update user information

    Args:
        username (str):
        body (UpdateUserRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        User
    """

    try:
        return (
            await asyncio_detailed(
                username=username,
                client=client,
                body=body,
            )
        ).parsed
    except errors.NotFoundException:
        return None
