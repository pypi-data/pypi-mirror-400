from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import Client
from ...models.create_response import CreateResponse
from ...models.custom_process_input import CustomProcessInput
from ...models.error_message import ErrorMessage
from ...models.portal_error_response import PortalErrorResponse
from ...types import Response


def _get_kwargs(
    *,
    body: CustomProcessInput,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/processes",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Client, response: httpx.Response
) -> CreateResponse | ErrorMessage | PortalErrorResponse | None:
    if response.status_code == 201:
        response_201 = CreateResponse.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = PortalErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = ErrorMessage.from_dict(response.json())

        return response_401

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[CreateResponse | ErrorMessage | PortalErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    body: CustomProcessInput,
) -> Response[CreateResponse | ErrorMessage | PortalErrorResponse]:
    """Create custom process

     Creates a custom data type or pipeline which you can use in the listed projects.

    Args:
        body (CustomProcessInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateResponse | ErrorMessage | PortalErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    body: CustomProcessInput,
) -> CreateResponse | ErrorMessage | PortalErrorResponse | None:
    """Create custom process

     Creates a custom data type or pipeline which you can use in the listed projects.

    Args:
        body (CustomProcessInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateResponse | ErrorMessage | PortalErrorResponse
    """

    try:
        return sync_detailed(
            client=client,
            body=body,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    *,
    client: Client,
    body: CustomProcessInput,
) -> Response[CreateResponse | ErrorMessage | PortalErrorResponse]:
    """Create custom process

     Creates a custom data type or pipeline which you can use in the listed projects.

    Args:
        body (CustomProcessInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateResponse | ErrorMessage | PortalErrorResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    body: CustomProcessInput,
) -> CreateResponse | ErrorMessage | PortalErrorResponse | None:
    """Create custom process

     Creates a custom data type or pipeline which you can use in the listed projects.

    Args:
        body (CustomProcessInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateResponse | ErrorMessage | PortalErrorResponse
    """

    try:
        return (
            await asyncio_detailed(
                client=client,
                body=body,
            )
        ).parsed
    except errors.NotFoundException:
        return None
