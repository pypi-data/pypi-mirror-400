from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status

if TYPE_CHECKING:
    from ..models.tag import Tag


T = TypeVar("T", bound="Dataset")


@_attrs_define
class Dataset:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        project_id (str):
        process_id (str):
        source_dataset_ids (list[str]):
        status (Status):
        tags (list[Tag]):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    name: str
    description: str
    project_id: str
    process_id: str
    source_dataset_ids: list[str]
    status: Status
    tags: list[Tag]
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        project_id = self.project_id

        process_id = self.process_id

        source_dataset_ids = self.source_dataset_ids

        status = self.status.value

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "projectId": project_id,
                "processId": process_id,
                "sourceDatasetIds": source_dataset_ids,
                "status": status,
                "tags": tags,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag import Tag

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        project_id = d.pop("projectId")

        process_id = d.pop("processId")

        source_dataset_ids = cast(list[str], d.pop("sourceDatasetIds"))

        status = Status(d.pop("status"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        dataset = cls(
            id=id,
            name=name,
            description=description,
            project_id=project_id,
            process_id=process_id,
            source_dataset_ids=source_dataset_ids,
            status=status,
            tags=tags,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
        )

        dataset.additional_properties = d
        return dataset

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
