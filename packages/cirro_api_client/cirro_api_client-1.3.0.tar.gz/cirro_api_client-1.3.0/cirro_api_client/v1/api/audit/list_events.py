from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import Client
from ...models.audit_event import AuditEvent
from ...models.list_events_entity_type import ListEventsEntityType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    username: str | Unset = UNSET,
    entity_type: ListEventsEntityType | Unset = UNSET,
    entity_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["username"] = username

    json_entity_type: str | Unset = UNSET
    if not isinstance(entity_type, Unset):
        json_entity_type = entity_type.value

    params["entityType"] = json_entity_type

    params["entityId"] = entity_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/audit-events",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> list[AuditEvent] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuditEvent.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    errors.handle_error_response(response, client.raise_on_unexpected_status)


def _build_response(*, client: Client, response: httpx.Response) -> Response[list[AuditEvent]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    username: str | Unset = UNSET,
    entity_type: ListEventsEntityType | Unset = UNSET,
    entity_id: str | Unset = UNSET,
) -> Response[list[AuditEvent]]:
    """List audit events

     Gets a list of audit events

    Args:
        username (str | Unset):
        entity_type (ListEventsEntityType | Unset):
        entity_id (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[AuditEvent]]
    """

    kwargs = _get_kwargs(
        username=username,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    response = client.get_httpx_client().request(
        auth=client.get_auth(),
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    username: str | Unset = UNSET,
    entity_type: ListEventsEntityType | Unset = UNSET,
    entity_id: str | Unset = UNSET,
) -> list[AuditEvent] | None:
    """List audit events

     Gets a list of audit events

    Args:
        username (str | Unset):
        entity_type (ListEventsEntityType | Unset):
        entity_id (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[AuditEvent]
    """

    try:
        return sync_detailed(
            client=client,
            username=username,
            entity_type=entity_type,
            entity_id=entity_id,
        ).parsed
    except errors.NotFoundException:
        return None


async def asyncio_detailed(
    *,
    client: Client,
    username: str | Unset = UNSET,
    entity_type: ListEventsEntityType | Unset = UNSET,
    entity_id: str | Unset = UNSET,
) -> Response[list[AuditEvent]]:
    """List audit events

     Gets a list of audit events

    Args:
        username (str | Unset):
        entity_type (ListEventsEntityType | Unset):
        entity_id (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[AuditEvent]]
    """

    kwargs = _get_kwargs(
        username=username,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    response = await client.get_async_httpx_client().request(auth=client.get_auth(), **kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    username: str | Unset = UNSET,
    entity_type: ListEventsEntityType | Unset = UNSET,
    entity_id: str | Unset = UNSET,
) -> list[AuditEvent] | None:
    """List audit events

     Gets a list of audit events

    Args:
        username (str | Unset):
        entity_type (ListEventsEntityType | Unset):
        entity_id (str | Unset):
        client (Client): instance of the API client

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[AuditEvent]
    """

    try:
        return (
            await asyncio_detailed(
                client=client,
                username=username,
                entity_type=entity_type,
                entity_id=entity_id,
            )
        ).parsed
    except errors.NotFoundException:
        return None
