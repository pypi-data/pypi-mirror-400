from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.message_type import MessageType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity import Entity


T = TypeVar("T", bound="Message")


@_attrs_define
class Message:
    """
    Attributes:
        message_type (MessageType):
        id (str):
        message (str):
        links (list[Entity]):
        has_replies (bool):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        parent_message_id (None | str | Unset):
    """

    message_type: MessageType
    id: str
    message: str
    links: list[Entity]
    has_replies: bool
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    parent_message_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message_type = self.message_type.value

        id = self.id

        message = self.message

        links = []
        for links_item_data in self.links:
            links_item = links_item_data.to_dict()
            links.append(links_item)

        has_replies = self.has_replies

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        parent_message_id: None | str | Unset
        if isinstance(self.parent_message_id, Unset):
            parent_message_id = UNSET
        else:
            parent_message_id = self.parent_message_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messageType": message_type,
                "id": id,
                "message": message,
                "links": links,
                "hasReplies": has_replies,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if parent_message_id is not UNSET:
            field_dict["parentMessageId"] = parent_message_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity import Entity

        d = dict(src_dict)
        message_type = MessageType(d.pop("messageType"))

        id = d.pop("id")

        message = d.pop("message")

        links = []
        _links = d.pop("links")
        for links_item_data in _links:
            links_item = Entity.from_dict(links_item_data)

            links.append(links_item)

        has_replies = d.pop("hasReplies")

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_parent_message_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_message_id = _parse_parent_message_id(d.pop("parentMessageId", UNSET))

        message = cls(
            message_type=message_type,
            id=id,
            message=message,
            links=links,
            has_replies=has_replies,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            parent_message_id=parent_message_id,
        )

        message.additional_properties = d
        return message

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
