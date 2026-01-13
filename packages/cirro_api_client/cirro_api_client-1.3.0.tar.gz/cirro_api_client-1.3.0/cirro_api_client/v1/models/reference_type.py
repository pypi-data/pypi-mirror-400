from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.reference_type_validation_item import ReferenceTypeValidationItem


T = TypeVar("T", bound="ReferenceType")


@_attrs_define
class ReferenceType:
    """
    Attributes:
        name (str):
        description (str):
        directory (str):
        validation (list[ReferenceTypeValidationItem]):
    """

    name: str
    description: str
    directory: str
    validation: list[ReferenceTypeValidationItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        directory = self.directory

        validation = []
        for validation_item_data in self.validation:
            validation_item = validation_item_data.to_dict()
            validation.append(validation_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "directory": directory,
                "validation": validation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reference_type_validation_item import ReferenceTypeValidationItem

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        directory = d.pop("directory")

        validation = []
        _validation = d.pop("validation")
        for validation_item_data in _validation:
            validation_item = ReferenceTypeValidationItem.from_dict(validation_item_data)

            validation.append(validation_item)

        reference_type = cls(
            name=name,
            description=description,
            directory=directory,
            validation=validation,
        )

        reference_type.additional_properties = d
        return reference_type

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
