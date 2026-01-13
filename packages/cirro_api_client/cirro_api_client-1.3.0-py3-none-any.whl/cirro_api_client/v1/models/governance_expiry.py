from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.governance_expiry_type import GovernanceExpiryType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GovernanceExpiry")


@_attrs_define
class GovernanceExpiry:
    """
    Attributes:
        type_ (GovernanceExpiryType | Unset): The expiry conditions that can be applied to governance requirements.
        days (int | None | Unset): The number of days for a relative expiration
        date (datetime.datetime | None | Unset): The date for an absolute expiration
    """

    type_: GovernanceExpiryType | Unset = UNSET
    days: int | None | Unset = UNSET
    date: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        days: int | None | Unset
        if isinstance(self.days, Unset):
            days = UNSET
        else:
            days = self.days

        date: None | str | Unset
        if isinstance(self.date, Unset):
            date = UNSET
        elif isinstance(self.date, datetime.datetime):
            date = self.date.isoformat()
        else:
            date = self.date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if days is not UNSET:
            field_dict["days"] = days
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: GovernanceExpiryType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = GovernanceExpiryType(_type_)

        def _parse_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        days = _parse_days(d.pop("days", UNSET))

        def _parse_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                date_type_0 = isoparse(data)

                return date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        date = _parse_date(d.pop("date", UNSET))

        governance_expiry = cls(
            type_=type_,
            days=days,
            date=date,
        )

        governance_expiry.additional_properties = d
        return governance_expiry

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
