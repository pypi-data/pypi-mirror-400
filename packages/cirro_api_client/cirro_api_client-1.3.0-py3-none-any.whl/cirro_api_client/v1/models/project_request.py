from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProjectRequest")


@_attrs_define
class ProjectRequest:
    """
    Attributes:
        name (str):
        description (str):
        classification_ids (list[str]):
        billing_info (str):
        admin_username (str):
        message (str):
    """

    name: str
    description: str
    classification_ids: list[str]
    billing_info: str
    admin_username: str
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        classification_ids = self.classification_ids

        billing_info = self.billing_info

        admin_username = self.admin_username

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "classificationIds": classification_ids,
                "billingInfo": billing_info,
                "adminUsername": admin_username,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        classification_ids = cast(list[str], d.pop("classificationIds"))

        billing_info = d.pop("billingInfo")

        admin_username = d.pop("adminUsername")

        message = d.pop("message")

        project_request = cls(
            name=name,
            description=description,
            classification_ids=classification_ids,
            billing_info=billing_info,
            admin_username=admin_username,
            message=message,
        )

        project_request.additional_properties = d
        return project_request

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
