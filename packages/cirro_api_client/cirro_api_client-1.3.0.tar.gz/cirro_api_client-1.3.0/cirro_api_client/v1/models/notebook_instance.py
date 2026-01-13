from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status

T = TypeVar("T", bound="NotebookInstance")


@_attrs_define
class NotebookInstance:
    """
    Attributes:
        id (str):
        name (str):
        status (Status):
        status_message (str):
        instance_type (str):
        accelerator_types (list[str]):
        git_repositories (list[str]):
        volume_size_gb (int):
        is_shared_with_project (bool):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    name: str
    status: Status
    status_message: str
    instance_type: str
    accelerator_types: list[str]
    git_repositories: list[str]
    volume_size_gb: int
    is_shared_with_project: bool
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        status = self.status.value

        status_message = self.status_message

        instance_type = self.instance_type

        accelerator_types = self.accelerator_types

        git_repositories = self.git_repositories

        volume_size_gb = self.volume_size_gb

        is_shared_with_project = self.is_shared_with_project

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "status": status,
                "statusMessage": status_message,
                "instanceType": instance_type,
                "acceleratorTypes": accelerator_types,
                "gitRepositories": git_repositories,
                "volumeSizeGB": volume_size_gb,
                "isSharedWithProject": is_shared_with_project,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        status = Status(d.pop("status"))

        status_message = d.pop("statusMessage")

        instance_type = d.pop("instanceType")

        accelerator_types = cast(list[str], d.pop("acceleratorTypes"))

        git_repositories = cast(list[str], d.pop("gitRepositories"))

        volume_size_gb = d.pop("volumeSizeGB")

        is_shared_with_project = d.pop("isSharedWithProject")

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        notebook_instance = cls(
            id=id,
            name=name,
            status=status,
            status_message=status_message,
            instance_type=instance_type,
            accelerator_types=accelerator_types,
            git_repositories=git_repositories,
            volume_size_gb=volume_size_gb,
            is_shared_with_project=is_shared_with_project,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
        )

        notebook_instance.additional_properties = d
        return notebook_instance

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
