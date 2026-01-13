from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.sharing_type import SharingType
from ..models.status import Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mounted_dataset import MountedDataset
    from ..models.workspace_compute_config import WorkspaceComputeConfig
    from ..models.workspace_session import WorkspaceSession


T = TypeVar("T", bound="Workspace")


@_attrs_define
class Workspace:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        project_id (str):
        status (Status):
        status_message (str):
        environment_id (str):
        mounted_datasets (list[MountedDataset]):
        compute_config (WorkspaceComputeConfig): Configuration parameters for a containerized workspace compute
            environment.
        sharing_type (SharingType):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        auto_stop_timeout (int | None | Unset):
        sessions (list[WorkspaceSession] | None | Unset):
        started_at (datetime.datetime | None | Unset):
        auto_stop_time (datetime.datetime | None | Unset):
    """

    id: str
    name: str
    description: str
    project_id: str
    status: Status
    status_message: str
    environment_id: str
    mounted_datasets: list[MountedDataset]
    compute_config: WorkspaceComputeConfig
    sharing_type: SharingType
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    auto_stop_timeout: int | None | Unset = UNSET
    sessions: list[WorkspaceSession] | None | Unset = UNSET
    started_at: datetime.datetime | None | Unset = UNSET
    auto_stop_time: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        project_id = self.project_id

        status = self.status.value

        status_message = self.status_message

        environment_id = self.environment_id

        mounted_datasets = []
        for mounted_datasets_item_data in self.mounted_datasets:
            mounted_datasets_item = mounted_datasets_item_data.to_dict()
            mounted_datasets.append(mounted_datasets_item)

        compute_config = self.compute_config.to_dict()

        sharing_type = self.sharing_type.value

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        auto_stop_timeout: int | None | Unset
        if isinstance(self.auto_stop_timeout, Unset):
            auto_stop_timeout = UNSET
        else:
            auto_stop_timeout = self.auto_stop_timeout

        sessions: list[dict[str, Any]] | None | Unset
        if isinstance(self.sessions, Unset):
            sessions = UNSET
        elif isinstance(self.sessions, list):
            sessions = []
            for sessions_type_0_item_data in self.sessions:
                sessions_type_0_item = sessions_type_0_item_data.to_dict()
                sessions.append(sessions_type_0_item)

        else:
            sessions = self.sessions

        started_at: None | str | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        auto_stop_time: None | str | Unset
        if isinstance(self.auto_stop_time, Unset):
            auto_stop_time = UNSET
        elif isinstance(self.auto_stop_time, datetime.datetime):
            auto_stop_time = self.auto_stop_time.isoformat()
        else:
            auto_stop_time = self.auto_stop_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "projectId": project_id,
                "status": status,
                "statusMessage": status_message,
                "environmentId": environment_id,
                "mountedDatasets": mounted_datasets,
                "computeConfig": compute_config,
                "sharingType": sharing_type,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if auto_stop_timeout is not UNSET:
            field_dict["autoStopTimeout"] = auto_stop_timeout
        if sessions is not UNSET:
            field_dict["sessions"] = sessions
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if auto_stop_time is not UNSET:
            field_dict["autoStopTime"] = auto_stop_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mounted_dataset import MountedDataset
        from ..models.workspace_compute_config import WorkspaceComputeConfig
        from ..models.workspace_session import WorkspaceSession

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        project_id = d.pop("projectId")

        status = Status(d.pop("status"))

        status_message = d.pop("statusMessage")

        environment_id = d.pop("environmentId")

        mounted_datasets = []
        _mounted_datasets = d.pop("mountedDatasets")
        for mounted_datasets_item_data in _mounted_datasets:
            mounted_datasets_item = MountedDataset.from_dict(mounted_datasets_item_data)

            mounted_datasets.append(mounted_datasets_item)

        compute_config = WorkspaceComputeConfig.from_dict(d.pop("computeConfig"))

        sharing_type = SharingType(d.pop("sharingType"))

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_auto_stop_timeout(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        auto_stop_timeout = _parse_auto_stop_timeout(d.pop("autoStopTimeout", UNSET))

        def _parse_sessions(data: object) -> list[WorkspaceSession] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sessions_type_0 = []
                _sessions_type_0 = data
                for sessions_type_0_item_data in _sessions_type_0:
                    sessions_type_0_item = WorkspaceSession.from_dict(sessions_type_0_item_data)

                    sessions_type_0.append(sessions_type_0_item)

                return sessions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[WorkspaceSession] | None | Unset, data)

        sessions = _parse_sessions(d.pop("sessions", UNSET))

        def _parse_started_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        started_at = _parse_started_at(d.pop("startedAt", UNSET))

        def _parse_auto_stop_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                auto_stop_time_type_0 = isoparse(data)

                return auto_stop_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        auto_stop_time = _parse_auto_stop_time(d.pop("autoStopTime", UNSET))

        workspace = cls(
            id=id,
            name=name,
            description=description,
            project_id=project_id,
            status=status,
            status_message=status_message,
            environment_id=environment_id,
            mounted_datasets=mounted_datasets,
            compute_config=compute_config,
            sharing_type=sharing_type,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            auto_stop_timeout=auto_stop_timeout,
            sessions=sessions,
            started_at=started_at,
            auto_stop_time=auto_stop_time,
        )

        workspace.additional_properties = d
        return workspace

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
