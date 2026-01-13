from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.sample import Sample
from ...models.sample_request import SampleRequest
from ...types import Response


def _get_kwargs(
    project_id: str,
    sample_id: str,
    *,
    body: SampleRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/projects/{project_id}/samples/{sample_id}".format(
            project_id=quote(str(project_id), safe=""),
            sample_id=quote(str(sample_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: SampleRequest,
) -> Response[Sample]:
    """Update sample

     Updates metadata on a sample

    Args:
        project_id (str):
        sample_id (str):
        body (SampleRequest):
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
        body=body,
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
    body: SampleRequest,
) -> Sample | None:
    """Update sample

     Updates metadata on a sample

    Args:
        project_id (str):
        sample_id (str):
        body (SampleRequest):
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
            body=body,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    project_id: str,
    sample_id: str,
    *,
    client: Client,
    body: SampleRequest,
) -> Response[Sample]:
    """Update sample

     Updates metadata on a sample

    Args:
        project_id (str):
        sample_id (str):
        body (SampleRequest):
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
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: str,
    sample_id: str,
    *,
    client: Client,
    body: SampleRequest,
) -> Sample | None:
    """Update sample

     Updates metadata on a sample

    Args:
        project_id (str):
        sample_id (str):
        body (SampleRequest):
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
                body=body,
            )
        ).parsed
    except errors.NotFoundException:
        return None
