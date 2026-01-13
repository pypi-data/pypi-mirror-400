from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import Client
from ...models.governance_classification import GovernanceClassification
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/governance/classifications",
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> list[GovernanceClassification] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GovernanceClassification.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[list[GovernanceClassification]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
) -> Response[list[GovernanceClassification]]:
    """Get classifications

     Retrieve a list of data classifications

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[GovernanceClassification]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
) -> list[GovernanceClassification] | None:
    """Get classifications

     Retrieve a list of data classifications

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[GovernanceClassification]
    """

    try:
        return sync_detailed(
            client=client,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    *,
    client: Client,
) -> Response[list[GovernanceClassification]]:
    """Get classifications

     Retrieve a list of data classifications

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[GovernanceClassification]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
) -> list[GovernanceClassification] | None:
    """Get classifications

     Retrieve a list of data classifications

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[GovernanceClassification]
    """

    try:
        return (
            await asyncio_detailed(
                client=client,
            )
        ).parsed
    except errors.NotFoundException:
        return None
