from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.project_requirement import ProjectRequirement
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    *,
    username: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["username"] = username

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/governance/projects/{project_id}/requirements".format(
            project_id=quote(str(project_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> list[ProjectRequirement] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProjectRequirement.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[list[ProjectRequirement]]:
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
    username: str | Unset = UNSET,
) -> Response[list[ProjectRequirement]]:
    """Get project requirements

     Retrieve governance requirements for a project with fulfillment information for the current user

    Args:
        project_id (str):
        username (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ProjectRequirement]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        username=username,
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
    username: str | Unset = UNSET,
) -> list[ProjectRequirement] | None:
    """Get project requirements

     Retrieve governance requirements for a project with fulfillment information for the current user

    Args:
        project_id (str):
        username (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ProjectRequirement]
    """

    try:
        return sync_detailed(
            project_id=project_id,
            client=client,
            username=username,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    project_id: str,
    *,
    client: Client,
    username: str | Unset = UNSET,
) -> Response[list[ProjectRequirement]]:
    """Get project requirements

     Retrieve governance requirements for a project with fulfillment information for the current user

    Args:
        project_id (str):
        username (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ProjectRequirement]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        username=username,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: Client,
    username: str | Unset = UNSET,
) -> list[ProjectRequirement] | None:
    """Get project requirements

     Retrieve governance requirements for a project with fulfillment information for the current user

    Args:
        project_id (str):
        username (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ProjectRequirement]
    """

    try:
        return (
            await asyncio_detailed(
                project_id=project_id,
                client=client,
                username=username,
            )
        ).parsed
    except errors.NotFoundException:
        return None
