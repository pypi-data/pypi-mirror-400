from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dashboard_dashboard_data import DashboardDashboardData
    from ..models.dashboard_info import DashboardInfo


T = TypeVar("T", bound="Dashboard")


@_attrs_define
class Dashboard:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        process_ids (list[str]):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        dashboard_data (DashboardDashboardData | Unset):
        info (DashboardInfo | Unset):
    """

    id: str
    name: str
    description: str
    process_ids: list[str]
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    dashboard_data: DashboardDashboardData | Unset = UNSET
    info: DashboardInfo | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        process_ids = self.process_ids

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

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
                "id": id,
                "name": name,
                "description": description,
                "processIds": process_ids,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if dashboard_data is not UNSET:
            field_dict["dashboardData"] = dashboard_data
        if info is not UNSET:
            field_dict["info"] = info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dashboard_dashboard_data import DashboardDashboardData
        from ..models.dashboard_info import DashboardInfo

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        process_ids = cast(list[str], d.pop("processIds"))

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        _dashboard_data = d.pop("dashboardData", UNSET)
        dashboard_data: DashboardDashboardData | Unset
        if isinstance(_dashboard_data, Unset):
            dashboard_data = UNSET
        else:
            dashboard_data = DashboardDashboardData.from_dict(_dashboard_data)

        _info = d.pop("info", UNSET)
        info: DashboardInfo | Unset
        if isinstance(_info, Unset):
            info = UNSET
        else:
            info = DashboardInfo.from_dict(_info)

        dashboard = cls(
            id=id,
            name=name,
            description=description,
            process_ids=process_ids,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            dashboard_data=dashboard_data,
            info=info,
        )

        dashboard.additional_properties = d
        return dashboard

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
