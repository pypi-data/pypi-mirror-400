from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.file_requirements import FileRequirements
from ...models.validate_file_requirements_request import ValidateFileRequirementsRequest
from ...types import Response


def _get_kwargs(
    process_id: str,
    *,
    body: ValidateFileRequirementsRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/processes/{process_id}/validate-files".format(
            process_id=quote(str(process_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> FileRequirements | None:
    if response.status_code == 200:
        response_200 = FileRequirements.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[FileRequirements]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileRequirementsRequest,
) -> Response[FileRequirements]:
    """Validate file requirements

     Checks the input file names with the expected files for a data type (ingest processes only)

    Args:
        process_id (str):
        body (ValidateFileRequirementsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FileRequirements]
    """

    kwargs = _get_kwargs(
        process_id=process_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileRequirementsRequest,
) -> FileRequirements | None:
    """Validate file requirements

     Checks the input file names with the expected files for a data type (ingest processes only)

    Args:
        process_id (str):
        body (ValidateFileRequirementsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FileRequirements
    """

    try:
        return sync_detailed(
            process_id=process_id,
            client=client,
            body=body,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileRequirementsRequest,
) -> Response[FileRequirements]:
    """Validate file requirements

     Checks the input file names with the expected files for a data type (ingest processes only)

    Args:
        process_id (str):
        body (ValidateFileRequirementsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FileRequirements]
    """

    kwargs = _get_kwargs(
        process_id=process_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    process_id: str,
    *,
    client: Client,
    body: ValidateFileRequirementsRequest,
) -> FileRequirements | None:
    """Validate file requirements

     Checks the input file names with the expected files for a data type (ingest processes only)

    Args:
        process_id (str):
        body (ValidateFileRequirementsRequest):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FileRequirements
    """

    try:
        return (
            await asyncio_detailed(
                process_id=process_id,
                client=client,
                body=body,
            )
        ).parsed
    except errors.NotFoundException:
        return None
