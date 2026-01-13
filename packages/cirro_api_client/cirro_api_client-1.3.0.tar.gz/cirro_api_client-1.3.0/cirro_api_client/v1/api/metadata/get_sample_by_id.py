from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.sample import Sample
from ...types import Response


def _get_kwargs(
    project_id: str,
    sample_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/samples/{sample_id}".format(
            project_id=quote(str(project_id), safe=""),
            sample_id=quote(str(sample_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Sample | None:
    if response.status_code == 200:
        response_200 = Sample.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[Sample]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    sample_id: str,
    *,
    client: Client,
) -> Response[Sample]:
    """Get sample by ID

     Retrieves a sample by its ID along with its metadata

    Args:
        project_id (str):
        sample_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Sample]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        sample_id=sample_id,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: str,
    sample_id: str,
    *,
    client: Client,
) -> Sample | None:
    """Get sample by ID

     Retrieves a sample by its ID along with its metadata

    Args:
        project_id (str):
        sample_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Sample
    """

    try:
        return sync_detailed(
            project_id=project_id,
            sample_id=sample_id,
            client=client,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    project_id: str,
    sample_id: str,
    *,
    client: Client,
) -> Response[Sample]:
    """Get sample by ID

     Retrieves a sample by its ID along with its metadata

    Args:
        project_id (str):
        sample_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Sample]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        sample_id=sample_id,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    sample_id: str,
    *,
    client: Client,
) -> Sample | None:
    """Get sample by ID

     Retrieves a sample by its ID along with its metadata

    Args:
        project_id (str):
        sample_id (str):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Sample
    """

    try:
        return (
            await asyncio_detailed(
                project_id=project_id,
                sample_id=sample_id,
                client=client,
            )
        ).parsed
    except errors.NotFoundException:
        return None
