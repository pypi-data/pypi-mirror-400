from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_role import ProjectRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="SetUserProjectRoleRequest")


@_attrs_define
class SetUserProjectRoleRequest:
    """
    Attributes:
        username (str):
        role (ProjectRole):
        suppress_notification (bool | Unset):  Default: False.
    """

    username: str
    role: ProjectRole
    suppress_notification: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        role = self.role.value

        suppress_notification = self.suppress_notification

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "role": role,
            }
        )
        if suppress_notification is not UNSET:
            field_dict["suppressNotification"] = suppress_notification

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username")

        role = ProjectRole(d.pop("role"))

        suppress_notification = d.pop("suppressNotification", UNSET)

        set_user_project_role_request = cls(
            username=username,
            role=role,
            suppress_notification=suppress_notification,
        )

        set_user_project_role_request.additional_properties = d
        return set_user_project_role_request

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
