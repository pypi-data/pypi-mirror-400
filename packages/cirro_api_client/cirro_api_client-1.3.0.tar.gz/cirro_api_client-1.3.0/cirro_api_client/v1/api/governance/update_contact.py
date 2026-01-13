from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import Client
from ...models.contact_input import ContactInput
from ...models.governance_contact import GovernanceContact
from ...types import Response


def _get_kwargs(
    contact_id: str,
    *,
    body: ContactInput,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/governance/contacts/{contact_id}".format(
            contact_id=quote(str(contact_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> GovernanceContact | None:
    if response.status_code == 200:
        response_200 = GovernanceContact.from_dict(response.json())

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[GovernanceContact]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    contact_id: str,
    *,
    client: Client,
    body: ContactInput,
) -> Response[GovernanceContact]:
    """Update contact

     Updates a contact

    Args:
        contact_id (str):
        body (ContactInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GovernanceContact]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contact_id: str,
    *,
    client: Client,
    body: ContactInput,
) -> GovernanceContact | None:
    """Update contact

     Updates a contact

    Args:
        contact_id (str):
        body (ContactInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GovernanceContact
    """

    try:
        return sync_detailed(
            contact_id=contact_id,
            client=client,
            body=body,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    contact_id: str,
    *,
    client: Client,
    body: ContactInput,
) -> Response[GovernanceContact]:
    """Update contact

     Updates a contact

    Args:
        contact_id (str):
        body (ContactInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GovernanceContact]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contact_id: str,
    *,
    client: Client,
    body: ContactInput,
) -> GovernanceContact | None:
    """Update contact

     Updates a contact

    Args:
        contact_id (str):
        body (ContactInput):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GovernanceContact
    """

    try:
        return (
            await asyncio_detailed(
                contact_id=contact_id,
                client=client,
                body=body,
            )
        ).parsed
    except errors.NotFoundException:
        return None
