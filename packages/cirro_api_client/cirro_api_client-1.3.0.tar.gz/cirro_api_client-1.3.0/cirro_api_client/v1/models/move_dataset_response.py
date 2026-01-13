from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MoveDatasetResponse")


@_attrs_define
class MoveDatasetResponse:
    """
    Attributes:
        s_3_copy_command (str):
        s_3_delete_command (str):
        samples_not_moved (list[str]):
    """

    s_3_copy_command: str
    s_3_delete_command: str
    samples_not_moved: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        s_3_copy_command = self.s_3_copy_command

        s_3_delete_command = self.s_3_delete_command

        samples_not_moved = self.samples_not_moved

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "s3CopyCommand": s_3_copy_command,
                "s3DeleteCommand": s_3_delete_command,
                "samplesNotMoved": samples_not_moved,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        s_3_copy_command = d.pop("s3CopyCommand")

        s_3_delete_command = d.pop("s3DeleteCommand")

        samples_not_moved = cast(list[str], d.pop("samplesNotMoved"))

        move_dataset_response = cls(
            s_3_copy_command=s_3_copy_command,
            s_3_delete_command=s_3_delete_command,
            samples_not_moved=samples_not_moved,
        )

        move_dataset_response.additional_properties = d
        return move_dataset_response

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
