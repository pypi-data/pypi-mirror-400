from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AWSCredentials")


@_attrs_define
class AWSCredentials:
    """
    Attributes:
        access_key_id (str):
        secret_access_key (str):
        session_token (str):
        expiration (datetime.datetime):
        region (str | Unset): Region of requested resource (i.e., S3 Bucket)
    """

    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: datetime.datetime
    region: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_key_id = self.access_key_id

        secret_access_key = self.secret_access_key

        session_token = self.session_token

        expiration = self.expiration.isoformat()

        region = self.region

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accessKeyId": access_key_id,
                "secretAccessKey": secret_access_key,
                "sessionToken": session_token,
                "expiration": expiration,
            }
        )
        if region is not UNSET:
            field_dict["region"] = region

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_key_id = d.pop("accessKeyId")

        secret_access_key = d.pop("secretAccessKey")

        session_token = d.pop("sessionToken")

        expiration = isoparse(d.pop("expiration"))

        region = d.pop("region", UNSET)

        aws_credentials = cls(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            expiration=expiration,
            region=region,
        )

        aws_credentials.additional_properties = d
        return aws_credentials

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
