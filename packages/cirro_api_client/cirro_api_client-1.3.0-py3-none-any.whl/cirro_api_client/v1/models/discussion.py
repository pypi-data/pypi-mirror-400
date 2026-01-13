from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.discussion_type import DiscussionType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity import Entity


T = TypeVar("T", bound="Discussion")


@_attrs_define
class Discussion:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        entity (Entity):
        type_ (DiscussionType):
        project_id (str):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        last_message_time (datetime.datetime | None | Unset):
    """

    id: str
    name: str
    description: str
    entity: Entity
    type_: DiscussionType
    project_id: str
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    last_message_time: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        entity = self.entity.to_dict()

        type_ = self.type_.value

        project_id = self.project_id

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        last_message_time: None | str | Unset
        if isinstance(self.last_message_time, Unset):
            last_message_time = UNSET
        elif isinstance(self.last_message_time, datetime.datetime):
            last_message_time = self.last_message_time.isoformat()
        else:
            last_message_time = self.last_message_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "entity": entity,
                "type": type_,
                "projectId": project_id,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if last_message_time is not UNSET:
            field_dict["lastMessageTime"] = last_message_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity import Entity

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        entity = Entity.from_dict(d.pop("entity"))

        type_ = DiscussionType(d.pop("type"))

        project_id = d.pop("projectId")

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_last_message_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_message_time_type_0 = isoparse(data)

                return last_message_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_message_time = _parse_last_message_time(d.pop("lastMessageTime", UNSET))

        discussion = cls(
            id=id,
            name=name,
            description=description,
            entity=entity,
            type_=type_,
            project_id=project_id,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            last_message_time=last_message_time,
        )

        discussion.additional_properties = d
        return discussion

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
