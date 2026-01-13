from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AuthInfo")


@_attrs_define
class AuthInfo:
    """
    Attributes:
        user_pool_id (str):
        sdk_app_id (str):
        ui_app_id (str):
        drive_app_id (str):
        endpoint (str):
    """

    user_pool_id: str
    sdk_app_id: str
    ui_app_id: str
    drive_app_id: str
    endpoint: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_pool_id = self.user_pool_id

        sdk_app_id = self.sdk_app_id

        ui_app_id = self.ui_app_id

        drive_app_id = self.drive_app_id

        endpoint = self.endpoint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userPoolId": user_pool_id,
                "sdkAppId": sdk_app_id,
                "uiAppId": ui_app_id,
                "driveAppId": drive_app_id,
                "endpoint": endpoint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_pool_id = d.pop("userPoolId")

        sdk_app_id = d.pop("sdkAppId")

        ui_app_id = d.pop("uiAppId")

        drive_app_id = d.pop("driveAppId")

        endpoint = d.pop("endpoint")

        auth_info = cls(
            user_pool_id=user_pool_id,
            sdk_app_id=sdk_app_id,
            ui_app_id=ui_app_id,
            drive_app_id=drive_app_id,
            endpoint=endpoint,
        )

        auth_info.additional_properties = d
        return auth_info

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
