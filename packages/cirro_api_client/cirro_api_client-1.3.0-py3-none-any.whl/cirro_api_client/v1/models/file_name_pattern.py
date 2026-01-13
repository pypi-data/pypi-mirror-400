from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileNamePattern")


@_attrs_define
class FileNamePattern:
    """
    Attributes:
        example_name (str): User-readable name for the file type used for display.
        sample_matching_pattern (str): File name pattern, formatted as a valid regex, to extract sample name and other
            metadata.
        description (None | str | Unset): File description.
    """

    example_name: str
    sample_matching_pattern: str
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        example_name = self.example_name

        sample_matching_pattern = self.sample_matching_pattern

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exampleName": example_name,
                "sampleMatchingPattern": sample_matching_pattern,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        example_name = d.pop("exampleName")

        sample_matching_pattern = d.pop("sampleMatchingPattern")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        file_name_pattern = cls(
            example_name=example_name,
            sample_matching_pattern=sample_matching_pattern,
            description=description,
        )

        file_name_pattern.additional_properties = d
        return file_name_pattern

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
