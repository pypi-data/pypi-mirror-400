from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.get_project_summary_response_200 import GetProjectSummaryResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: str,
    *,
    number_of_days: int | Unset = 1,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["numberOfDays"] = number_of_days

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/execution".format(
            project_id=quote(str(project_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> GetProjectSummaryResponse200 | None:
    if response.status_code == 200:
        response_200 = GetProjectSummaryResponse200.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[GetProjectSummaryResponse200]:
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
    number_of_days: int | Unset = 1,
) -> Response[GetProjectSummaryResponse200]:
    """Get execution summary

     Gets an overview of the executions currently running in the project

    Args:
        project_id (str):
        number_of_days (int | Unset):  Default: 1.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectSummaryResponse200]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        number_of_days=number_of_days,
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
    number_of_days: int | Unset = 1,
) -> GetProjectSummaryResponse200 | None:
    """Get execution summary

     Gets an overview of the executions currently running in the project

    Args:
        project_id (str):
        number_of_days (int | Unset):  Default: 1.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectSummaryResponse200
    """

    try:
        return sync_detailed(
            project_id=project_id,
            client=client,
            number_of_days=number_of_days,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    project_id: str,
    *,
    client: Client,
    number_of_days: int | Unset = 1,
) -> Response[GetProjectSummaryResponse200]:
    """Get execution summary

     Gets an overview of the executions currently running in the project

    Args:
        project_id (str):
        number_of_days (int | Unset):  Default: 1.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectSummaryResponse200]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        number_of_days=number_of_days,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    *,
    client: Client,
    number_of_days: int | Unset = 1,
) -> GetProjectSummaryResponse200 | None:
    """Get execution summary

     Gets an overview of the executions currently running in the project

    Args:
        project_id (str):
        number_of_days (int | Unset):  Default: 1.
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectSummaryResponse200
    """

    try:
        return (
            await asyncio_detailed(
                project_id=project_id,
                client=client,
                number_of_days=number_of_days,
            )
        ).parsed
    except errors.NotFoundException:
        return None
