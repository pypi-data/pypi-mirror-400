from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.discussion_type import DiscussionType

if TYPE_CHECKING:
    from ..models.entity import Entity


T = TypeVar("T", bound="DiscussionInput")


@_attrs_define
class DiscussionInput:
    """
    Attributes:
        name (str):
        description (str):
        entity (Entity):
        type_ (DiscussionType):
        project_id (str):
    """

    name: str
    description: str
    entity: Entity
    type_: DiscussionType
    project_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        entity = self.entity.to_dict()

        type_ = self.type_.value

        project_id = self.project_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "entity": entity,
                "type": type_,
                "projectId": project_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity import Entity

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        entity = Entity.from_dict(d.pop("entity"))

        type_ = DiscussionType(d.pop("type"))

        project_id = d.pop("projectId")

        discussion_input = cls(
            name=name,
            description=description,
            entity=entity,
            type_=type_,
            project_id=project_id,
        )

        discussion_input.additional_properties = d
        return discussion_input

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
