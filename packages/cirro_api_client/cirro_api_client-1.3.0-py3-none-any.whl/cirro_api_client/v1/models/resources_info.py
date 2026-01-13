from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ResourcesInfo")


@_attrs_define
class ResourcesInfo:
    """
    Attributes:
        commit (str):
        date (datetime.datetime):
        repository (str):
        source_version (str):
    """

    commit: str
    date: datetime.datetime
    repository: str
    source_version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        commit = self.commit

        date = self.date.isoformat()

        repository = self.repository

        source_version = self.source_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "commit": commit,
                "date": date,
                "repository": repository,
                "sourceVersion": source_version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        commit = d.pop("commit")

        date = isoparse(d.pop("date"))

        repository = d.pop("repository")

        source_version = d.pop("sourceVersion")

        resources_info = cls(
            commit=commit,
            date=date,
            repository=repository,
            source_version=source_version,
        )

        resources_info.additional_properties = d
        return resources_info

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
