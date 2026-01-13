from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.governance_file_type import GovernanceFileType

T = TypeVar("T", bound="GovernanceFileInput")


@_attrs_define
class GovernanceFileInput:
    """
    Attributes:
        name (str):
        description (str):
        src (str):
        type_ (GovernanceFileType): The options for supplementals for governance requirements
    """

    name: str
    description: str
    src: str
    type_: GovernanceFileType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        src = self.src

        type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "src": src,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        src = d.pop("src")

        type_ = GovernanceFileType(d.pop("type"))

        governance_file_input = cls(
            name=name,
            description=description,
            src=src,
            type_=type_,
        )

        governance_file_input.additional_properties = d
        return governance_file_input

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
