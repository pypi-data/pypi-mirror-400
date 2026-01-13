from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VersionSpecification")


@_attrs_define
class VersionSpecification:
    """
    Attributes:
        version (str):
        is_default (bool):
        is_latest (bool):
    """

    version: str
    is_default: bool
    is_latest: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        is_default = self.is_default

        is_latest = self.is_latest

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "isDefault": is_default,
                "isLatest": is_latest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version = d.pop("version")

        is_default = d.pop("isDefault")

        is_latest = d.pop("isLatest")

        version_specification = cls(
            version=version,
            is_default=is_default,
            is_latest=is_latest,
        )

        version_specification.additional_properties = d
        return version_specification

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
