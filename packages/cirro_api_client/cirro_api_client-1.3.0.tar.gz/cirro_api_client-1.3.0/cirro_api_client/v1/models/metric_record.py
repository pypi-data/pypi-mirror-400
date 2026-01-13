from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.metric_record_services import MetricRecordServices


T = TypeVar("T", bound="MetricRecord")


@_attrs_define
class MetricRecord:
    """
    Attributes:
        unit (str):
        date (datetime.date | Unset): Date in ISO 8601 format
        services (MetricRecordServices | Unset): Map of service names to metric value Example: {'Amazon Simple Storage
            Service': 24.91}.
    """

    unit: str
    date: datetime.date | Unset = UNSET
    services: MetricRecordServices | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        unit = self.unit

        date: str | Unset = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        services: dict[str, Any] | Unset = UNSET
        if not isinstance(self.services, Unset):
            services = self.services.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "unit": unit,
            }
        )
        if date is not UNSET:
            field_dict["date"] = date
        if services is not UNSET:
            field_dict["services"] = services

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metric_record_services import MetricRecordServices

        d = dict(src_dict)
        unit = d.pop("unit")

        _date = d.pop("date", UNSET)
        date: datetime.date | Unset
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date).date()

        _services = d.pop("services", UNSET)
        services: MetricRecordServices | Unset
        if isinstance(_services, Unset):
            services = UNSET
        else:
            services = MetricRecordServices.from_dict(_services)

        metric_record = cls(
            unit=unit,
            date=date,
            services=services,
        )

        metric_record.additional_properties = d
        return metric_record

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
