from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.governance_file_type import GovernanceFileType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GovernanceFile")


@_attrs_define
class GovernanceFile:
    """
    Attributes:
        name (str | Unset): The title of the resource visible to users
        description (str | Unset): A description of the resource visible to users
        src (str | Unset): The file name without path or the full link path
        type_ (GovernanceFileType | Unset): The options for supplementals for governance requirements
    """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    src: str | Unset = UNSET
    type_: GovernanceFileType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        src = self.src

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if src is not UNSET:
            field_dict["src"] = src
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        src = d.pop("src", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: GovernanceFileType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = GovernanceFileType(_type_)

        governance_file = cls(
            name=name,
            description=description,
            src=src,
            type_=type_,
        )

        governance_file.additional_properties = d
        return governance_file

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
