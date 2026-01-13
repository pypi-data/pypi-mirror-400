from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...types import Response


def _get_kwargs(
    project_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_id}/workspaces/{workspace_id}:start".format(
            project_id=quote(str(project_id), safe=""),
            workspace_id=quote(str(workspace_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Any | None:
    if response.status_code == 202:
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
    project_id: str,
    workspace_id: str,
    *,
    client: Client,
) -> Response[Any]:
    """Start workspace

     Starts a workspace instance

    Args:
        project_id (str):
        workspace_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        workspace_id=workspace_id,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    project_id: str,
    workspace_id: str,
    *,
    client: Client,
) -> Response[Any]:
    """Start workspace

     Starts a workspace instance

    Args:
        project_id (str):
        workspace_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        workspace_id=workspace_id,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)
