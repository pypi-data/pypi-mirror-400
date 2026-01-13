from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dashboard_request_dashboard_data import DashboardRequestDashboardData
    from ..models.dashboard_request_info import DashboardRequestInfo


T = TypeVar("T", bound="DashboardRequest")


@_attrs_define
class DashboardRequest:
    """
    Attributes:
        name (str):
        description (str):
        process_ids (list[str]):
        dashboard_data (DashboardRequestDashboardData | Unset):
        info (DashboardRequestInfo | Unset):
    """

    name: str
    description: str
    process_ids: list[str]
    dashboard_data: DashboardRequestDashboardData | Unset = UNSET
    info: DashboardRequestInfo | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        process_ids = self.process_ids

        dashboard_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dashboard_data, Unset):
            dashboard_data = self.dashboard_data.to_dict()

        info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.info, Unset):
            info = self.info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "processIds": process_ids,
            }
        )
        if dashboard_data is not UNSET:
            field_dict["dashboardData"] = dashboard_data
        if info is not UNSET:
            field_dict["info"] = info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dashboard_request_dashboard_data import DashboardRequestDashboardData
        from ..models.dashboard_request_info import DashboardRequestInfo

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        process_ids = cast(list[str], d.pop("processIds"))

        _dashboard_data = d.pop("dashboardData", UNSET)
        dashboard_data: DashboardRequestDashboardData | Unset
        if isinstance(_dashboard_data, Unset):
            dashboard_data = UNSET
        else:
            dashboard_data = DashboardRequestDashboardData.from_dict(_dashboard_data)

        _info = d.pop("info", UNSET)
        info: DashboardRequestInfo | Unset
        if isinstance(_info, Unset):
            info = UNSET
        else:
            info = DashboardRequestInfo.from_dict(_info)

        dashboard_request = cls(
            name=name,
            description=description,
            process_ids=process_ids,
            dashboard_data=dashboard_data,
            info=info,
        )

        dashboard_request.additional_properties = d
        return dashboard_request

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
