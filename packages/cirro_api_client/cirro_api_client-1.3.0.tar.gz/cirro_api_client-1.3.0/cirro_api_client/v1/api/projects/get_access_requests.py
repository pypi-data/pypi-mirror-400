from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.project_access_request import ProjectAccessRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    *,
    include_closed: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["includeClosed"] = include_closed

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/access-requests".format(
            project_id=quote(str(project_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> list[ProjectAccessRequest] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProjectAccessRequest.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[list[ProjectAccessRequest]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    *,
    client: Client,
    include_closed: bool | Unset = False,
) -> Response[list[ProjectAccessRequest]]:
    """Get access requests

     Gets users who have requested access to the project

    Args:
        project_id (str):
        include_closed (bool | Unset):  Default: False.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ProjectAccessRequest]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        include_closed=include_closed,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    *,
    client: Client,
    include_closed: bool | Unset = False,
) -> list[ProjectAccessRequest] | None:
    """Get access requests

     Gets users who have requested access to the project

    Args:
        project_id (str):
        include_closed (bool | Unset):  Default: False.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ProjectAccessRequest]
    """

    try:
        return sync_detailed(
            project_id=project_id,
            client=client,
            include_closed=include_closed,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    project_id: str,
    *,
    client: Client,
    include_closed: bool | Unset = False,
) -> Response[list[ProjectAccessRequest]]:
    """Get access requests

     Gets users who have requested access to the project

    Args:
        project_id (str):
        include_closed (bool | Unset):  Default: False.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ProjectAccessRequest]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        include_closed=include_closed,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: Client,
    include_closed: bool | Unset = False,
) -> list[ProjectAccessRequest] | None:
    """Get access requests

     Gets users who have requested access to the project

    Args:
        project_id (str):
        include_closed (bool | Unset):  Default: False.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ProjectAccessRequest]
    """

    try:
        return (
            await asyncio_detailed(
                project_id=project_id,
                client=client,
                include_closed=include_closed,
            )
        ).parsed
    except errors.NotFoundException:
        return None
