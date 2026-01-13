from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.allowed_data_type import AllowedDataType


T = TypeVar("T", bound="FileRequirements")


@_attrs_define
class FileRequirements:
    """
    Attributes:
        files (list[str]):
        error_msg (str):
        allowed_data_types (list[AllowedDataType]):
    """

    files: list[str]
    error_msg: str
    allowed_data_types: list[AllowedDataType]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = self.files

        error_msg = self.error_msg

        allowed_data_types = []
        for allowed_data_types_item_data in self.allowed_data_types:
            allowed_data_types_item = allowed_data_types_item_data.to_dict()
            allowed_data_types.append(allowed_data_types_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
                "errorMsg": error_msg,
                "allowedDataTypes": allowed_data_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.allowed_data_type import AllowedDataType

        d = dict(src_dict)
        files = cast(list[str], d.pop("files"))

        error_msg = d.pop("errorMsg")

        allowed_data_types = []
        _allowed_data_types = d.pop("allowedDataTypes")
        for allowed_data_types_item_data in _allowed_data_types:
            allowed_data_types_item = AllowedDataType.from_dict(allowed_data_types_item_data)

            allowed_data_types.append(allowed_data_types_item)

        file_requirements = cls(
            files=files,
            error_msg=error_msg,
            allowed_data_types=allowed_data_types,
        )

        file_requirements.additional_properties = d
        return file_requirements

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
