from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateReferenceRequest")


@_attrs_define
class CreateReferenceRequest:
    """
    Attributes:
        name (str):
        description (str):
        type_ (str):
        expected_files (list[str]):
    """

    name: str
    description: str
    type_: str
    expected_files: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        type_ = self.type_

        expected_files = self.expected_files

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "type": type_,
                "expectedFiles": expected_files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        type_ = d.pop("type")

        expected_files = cast(list[str], d.pop("expectedFiles"))

        create_reference_request = cls(
            name=name,
            description=description,
            type_=type_,
            expected_files=expected_files,
        )

        create_reference_request.additional_properties = d
        return create_reference_request

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
