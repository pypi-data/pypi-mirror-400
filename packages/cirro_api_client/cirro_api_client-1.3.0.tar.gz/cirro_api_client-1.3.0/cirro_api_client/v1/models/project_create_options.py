from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cloud_account_type import CloudAccountType

T = TypeVar("T", bound="ProjectCreateOptions")


@_attrs_define
class ProjectCreateOptions:
    """
    Attributes:
        enabled_account_types (list[CloudAccountType]):
        portal_account_id (str):
        portal_region (str):
        template_url (str):
        wizard_url (str):
    """

    enabled_account_types: list[CloudAccountType]
    portal_account_id: str
    portal_region: str
    template_url: str
    wizard_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled_account_types = []
        for enabled_account_types_item_data in self.enabled_account_types:
            enabled_account_types_item = enabled_account_types_item_data.value
            enabled_account_types.append(enabled_account_types_item)

        portal_account_id = self.portal_account_id

        portal_region = self.portal_region

        template_url = self.template_url

        wizard_url = self.wizard_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enabledAccountTypes": enabled_account_types,
                "portalAccountId": portal_account_id,
                "portalRegion": portal_region,
                "templateUrl": template_url,
                "wizardUrl": wizard_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled_account_types = []
        _enabled_account_types = d.pop("enabledAccountTypes")
        for enabled_account_types_item_data in _enabled_account_types:
            enabled_account_types_item = CloudAccountType(enabled_account_types_item_data)

            enabled_account_types.append(enabled_account_types_item)

        portal_account_id = d.pop("portalAccountId")

        portal_region = d.pop("portalRegion")

        template_url = d.pop("templateUrl")

        wizard_url = d.pop("wizardUrl")

        project_create_options = cls(
            enabled_account_types=enabled_account_types,
            portal_account_id=portal_account_id,
            portal_region=portal_region,
            template_url=template_url,
            wizard_url=wizard_url,
        )

        project_create_options.additional_properties = d
        return project_create_options

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
