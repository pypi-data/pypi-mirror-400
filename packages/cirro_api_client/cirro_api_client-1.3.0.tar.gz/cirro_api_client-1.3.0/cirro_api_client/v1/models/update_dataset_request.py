from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tag import Tag


T = TypeVar("T", bound="UpdateDatasetRequest")


@_attrs_define
class UpdateDatasetRequest:
    """
    Attributes:
        name (str):
        description (str):
        process_id (str):
        tags (list[Tag]):
    """

    name: str
    description: str
    process_id: str
    tags: list[Tag]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        process_id = self.process_id

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "processId": process_id,
                "tags": tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag import Tag

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        process_id = d.pop("processId")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        update_dataset_request = cls(
            name=name,
            description=description,
            process_id=process_id,
            tags=tags,
        )

        update_dataset_request.additional_properties = d
        return update_dataset_request

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
