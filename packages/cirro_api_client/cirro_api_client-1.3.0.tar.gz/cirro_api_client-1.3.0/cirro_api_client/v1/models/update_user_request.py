from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_settings import UserSettings


T = TypeVar("T", bound="UpdateUserRequest")


@_attrs_define
class UpdateUserRequest:
    """
    Attributes:
        name (str): Display name of the user
        email (str): Email address of the user
        phone (str | Unset): Phone number of the user
        department (str | Unset): Department or lab the user belongs to
        job_title (str | Unset): Job title or role of the user
        organization (str | Unset): The organization the user belongs to, only editable by administrators
        settings (None | Unset | UserSettings):
        groups (list[str] | Unset): Groups the user belongs to, only editable by administrators
    """

    name: str
    email: str
    phone: str | Unset = UNSET
    department: str | Unset = UNSET
    job_title: str | Unset = UNSET
    organization: str | Unset = UNSET
    settings: None | Unset | UserSettings = UNSET
    groups: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_settings import UserSettings

        name = self.name

        email = self.email

        phone = self.phone

        department = self.department

        job_title = self.job_title

        organization = self.organization

        settings: dict[str, Any] | None | Unset
        if isinstance(self.settings, Unset):
            settings = UNSET
        elif isinstance(self.settings, UserSettings):
            settings = self.settings.to_dict()
        else:
            settings = self.settings

        groups: list[str] | Unset = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "email": email,
            }
        )
        if phone is not UNSET:
            field_dict["phone"] = phone
        if department is not UNSET:
            field_dict["department"] = department
        if job_title is not UNSET:
            field_dict["jobTitle"] = job_title
        if organization is not UNSET:
            field_dict["organization"] = organization
        if settings is not UNSET:
            field_dict["settings"] = settings
        if groups is not UNSET:
            field_dict["groups"] = groups

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_settings import UserSettings

        d = dict(src_dict)
        name = d.pop("name")

        email = d.pop("email")

        phone = d.pop("phone", UNSET)

        department = d.pop("department", UNSET)

        job_title = d.pop("jobTitle", UNSET)

        organization = d.pop("organization", UNSET)

        def _parse_settings(data: object) -> None | Unset | UserSettings:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                settings_type_1 = UserSettings.from_dict(data)

                return settings_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UserSettings, data)

        settings = _parse_settings(d.pop("settings", UNSET))

        groups = cast(list[str], d.pop("groups", UNSET))

        update_user_request = cls(
            name=name,
            email=email,
            phone=phone,
            department=department,
            job_title=job_title,
            organization=organization,
            settings=settings,
            groups=groups,
        )

        update_user_request.additional_properties = d
        return update_user_request

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
