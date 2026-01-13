from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageInput")


@_attrs_define
class MessageInput:
    """
    Attributes:
        message (str):
        parent_message_id (None | str | Unset):
    """

    message: str
    parent_message_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        parent_message_id: None | str | Unset
        if isinstance(self.parent_message_id, Unset):
            parent_message_id = UNSET
        else:
            parent_message_id = self.parent_message_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
            }
        )
        if parent_message_id is not UNSET:
            field_dict["parentMessageId"] = parent_message_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message")

        def _parse_parent_message_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_message_id = _parse_parent_message_id(d.pop("parentMessageId", UNSET))

        message_input = cls(
            message=message,
            parent_message_id=parent_message_id,
        )

        message_input.additional_properties = d
        return message_input

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
