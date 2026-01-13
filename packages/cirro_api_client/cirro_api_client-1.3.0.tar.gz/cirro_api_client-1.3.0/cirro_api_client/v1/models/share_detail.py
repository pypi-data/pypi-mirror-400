from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.share_type import ShareType

if TYPE_CHECKING:
    from ..models.dataset_condition import DatasetCondition
    from ..models.named_item import NamedItem


T = TypeVar("T", bound="ShareDetail")


@_attrs_define
class ShareDetail:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        originating_project (NamedItem):
        share_type (ShareType):
        shared_projects (list[NamedItem]):
        conditions (list[DatasetCondition]): The conditions under which the dataset is shared
        keywords (list[str]):
        classification_ids (list[str]):
        is_view_restricted (bool):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    name: str
    description: str
    originating_project: NamedItem
    share_type: ShareType
    shared_projects: list[NamedItem]
    conditions: list[DatasetCondition]
    keywords: list[str]
    classification_ids: list[str]
    is_view_restricted: bool
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        originating_project = self.originating_project.to_dict()

        share_type = self.share_type.value

        shared_projects = []
        for shared_projects_item_data in self.shared_projects:
            shared_projects_item = shared_projects_item_data.to_dict()
            shared_projects.append(shared_projects_item)

        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        keywords = self.keywords

        classification_ids = self.classification_ids

        is_view_restricted = self.is_view_restricted

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
                "originatingProject": originating_project,
                "shareType": share_type,
                "sharedProjects": shared_projects,
                "conditions": conditions,
                "keywords": keywords,
                "classificationIds": classification_ids,
                "isViewRestricted": is_view_restricted,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_condition import DatasetCondition
        from ..models.named_item import NamedItem

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        originating_project = NamedItem.from_dict(d.pop("originatingProject"))

        share_type = ShareType(d.pop("shareType"))

        shared_projects = []
        _shared_projects = d.pop("sharedProjects")
        for shared_projects_item_data in _shared_projects:
            shared_projects_item = NamedItem.from_dict(shared_projects_item_data)

            shared_projects.append(shared_projects_item)

        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = DatasetCondition.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        keywords = cast(list[str], d.pop("keywords"))

        classification_ids = cast(list[str], d.pop("classificationIds"))

        is_view_restricted = d.pop("isViewRestricted")

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        share_detail = cls(
            id=id,
            name=name,
            description=description,
            originating_project=originating_project,
            share_type=share_type,
            shared_projects=shared_projects,
            conditions=conditions,
            keywords=keywords,
            classification_ids=classification_ids,
            is_view_restricted=is_view_restricted,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
        )

        share_detail.additional_properties = d
        return share_detail

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
