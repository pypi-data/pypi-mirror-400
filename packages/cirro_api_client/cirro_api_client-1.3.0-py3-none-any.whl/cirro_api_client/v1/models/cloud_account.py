from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cloud_account_type import CloudAccountType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CloudAccount")


@_attrs_define
class CloudAccount:
    """
    Attributes:
        account_type (CloudAccountType): Type of cloud account (Hosted by Cirro, or Bring your own account)
        account_id (str | Unset): AWS Account ID
        account_name (str | Unset): Name used to describe the account, useful when the account hosts multiple projects
        region_name (str | Unset): AWS Region Code (defaults to region of Cirro app) Example: us-west-2.
    """

    account_type: CloudAccountType
    account_id: str | Unset = UNSET
    account_name: str | Unset = UNSET
    region_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account_type = self.account_type.value

        account_id = self.account_id

        account_name = self.account_name

        region_name = self.region_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accountType": account_type,
            }
        )
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if region_name is not UNSET:
            field_dict["regionName"] = region_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        account_type = CloudAccountType(d.pop("accountType"))

        account_id = d.pop("accountId", UNSET)

        account_name = d.pop("accountName", UNSET)

        region_name = d.pop("regionName", UNSET)

        cloud_account = cls(
            account_type=account_type,
            account_id=account_id,
            account_name=account_name,
            region_name=region_name,
        )

        cloud_account.additional_properties = d
        return cloud_account

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
