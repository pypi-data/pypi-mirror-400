from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileNameMatch")


@_attrs_define
class FileNameMatch:
    """
    Attributes:
        file_name (str):
        sample_name (str):
        regex_pattern_match (str):
    """

    file_name: str
    sample_name: str
    regex_pattern_match: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_name = self.file_name

        sample_name = self.sample_name

        regex_pattern_match = self.regex_pattern_match

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fileName": file_name,
                "sampleName": sample_name,
                "regexPatternMatch": regex_pattern_match,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_name = d.pop("fileName")

        sample_name = d.pop("sampleName")

        regex_pattern_match = d.pop("regexPatternMatch")

        file_name_match = cls(
            file_name=file_name,
            sample_name=sample_name,
            regex_pattern_match=regex_pattern_match,
        )

        file_name_match.additional_properties = d
        return file_name_match

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
