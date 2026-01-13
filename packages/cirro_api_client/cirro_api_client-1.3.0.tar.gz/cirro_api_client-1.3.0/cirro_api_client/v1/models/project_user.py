from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_role import ProjectRole

T = TypeVar("T", bound="ProjectUser")


@_attrs_define
class ProjectUser:
    """
    Attributes:
        name (str):
        username (str):
        organization (str):
        department (str):
        email (str):
        job_title (str):
        role (ProjectRole):
    """

    name: str
    username: str
    organization: str
    department: str
    email: str
    job_title: str
    role: ProjectRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        username = self.username

        organization = self.organization

        department = self.department

        email = self.email

        job_title = self.job_title

        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "username": username,
                "organization": organization,
                "department": department,
                "email": email,
                "jobTitle": job_title,
                "role": role,
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

        email = d.pop("email")

        job_title = d.pop("jobTitle")

        role = ProjectRole(d.pop("role"))

        project_user = cls(
            name=name,
            username=username,
            organization=organization,
            department=department,
            email=email,
            job_title=job_title,
            role=role,
        )

        project_user.additional_properties = d
        return project_user

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
