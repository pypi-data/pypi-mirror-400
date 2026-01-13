from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RequirementFulfillmentInput")


@_attrs_define
class RequirementFulfillmentInput:
    """
    Attributes:
        file (None | str | Unset):
        completed_on (datetime.datetime | None | Unset): If not provided, defaults to the current instant
    """

    file: None | str | Unset = UNSET
    completed_on: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file: None | str | Unset
        if isinstance(self.file, Unset):
            file = UNSET
        else:
            file = self.file

        completed_on: None | str | Unset
        if isinstance(self.completed_on, Unset):
            completed_on = UNSET
        elif isinstance(self.completed_on, datetime.datetime):
            completed_on = self.completed_on.isoformat()
        else:
            completed_on = self.completed_on

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file is not UNSET:
            field_dict["file"] = file
        if completed_on is not UNSET:
            field_dict["completedOn"] = completed_on

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_file(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file = _parse_file(d.pop("file", UNSET))

        def _parse_completed_on(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_on_type_0 = isoparse(data)

                return completed_on_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        completed_on = _parse_completed_on(d.pop("completedOn", UNSET))

        requirement_fulfillment_input = cls(
            file=file,
            completed_on=completed_on,
        )

        requirement_fulfillment_input.additional_properties = d
        return requirement_fulfillment_input

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
