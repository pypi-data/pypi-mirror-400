from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        name (str):
        username (str):
        organization (str):
        department (str):
        job_title (str):
    """

    name: str
    username: str
    organization: str
    department: str
    job_title: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        username = self.username

        organization = self.organization

        department = self.department

        job_title = self.job_title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "username": username,
                "organization": organization,
                "department": department,
                "jobTitle": job_title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        username = d.pop("username")

        organization = d.pop("organization")

        department = d.pop("department")

        job_title = d.pop("jobTitle")

        user = cls(
            name=name,
            username=username,
            organization=organization,
            department=department,
            job_title=job_title,
        )

        user.additional_properties = d
        return user

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
