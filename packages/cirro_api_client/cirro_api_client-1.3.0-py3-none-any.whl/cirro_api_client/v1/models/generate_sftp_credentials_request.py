from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GenerateSftpCredentialsRequest")


@_attrs_define
class GenerateSftpCredentialsRequest:
    """
    Attributes:
        lifetime_days (int | Unset): Number of days the credentials are valid for Default: 1.
    """

    lifetime_days: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        lifetime_days = self.lifetime_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if lifetime_days is not UNSET:
            field_dict["lifetimeDays"] = lifetime_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        lifetime_days = d.pop("lifetimeDays", UNSET)

        generate_sftp_credentials_request = cls(
            lifetime_days=lifetime_days,
        )

        generate_sftp_credentials_request.additional_properties = d
        return generate_sftp_credentials_request

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
