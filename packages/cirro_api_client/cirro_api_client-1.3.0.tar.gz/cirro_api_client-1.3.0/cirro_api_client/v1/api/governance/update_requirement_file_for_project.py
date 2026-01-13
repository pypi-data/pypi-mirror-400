from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.governance_file_input import GovernanceFileInput
from ...types import Response


def _get_kwargs(
    requirement_id: str,
    project_id: str,
    *,
    body: GovernanceFileInput,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/governance/requirements/{requirement_id}/projects/{project_id}".format(
            requirement_id=quote(str(requirement_id), safe=""),
            project_id=quote(str(project_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    requirement_id: str,
    project_id: str,
    *,
    client: Client,
    body: GovernanceFileInput,
) -> Response[Any]:
    """Update the project file for a requirement

     Updates the project-specific file for a requirement

    Args:
        requirement_id (str):
        project_id (str):
        body (GovernanceFileInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        requirement_id=requirement_id,
        project_id=project_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    requirement_id: str,
    project_id: str,
    *,
    client: Client,
    body: GovernanceFileInput,
) -> Response[Any]:
    """Update the project file for a requirement

     Updates the project-specific file for a requirement

    Args:
        requirement_id (str):
        project_id (str):
        body (GovernanceFileInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        requirement_id=requirement_id,
        project_id=project_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)
