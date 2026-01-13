from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Task")


@_attrs_define
class Task:
    """
    Attributes:
        name (str):
        status (str):
        native_job_id (None | str | Unset):
        requested_at (datetime.datetime | None | Unset):
        started_at (datetime.datetime | None | Unset):
        stopped_at (datetime.datetime | None | Unset):
        container_image (None | str | Unset):
        command_line (None | str | Unset):
        log_location (None | str | Unset):
    """

    name: str
    status: str
    native_job_id: None | str | Unset = UNSET
    requested_at: datetime.datetime | None | Unset = UNSET
    started_at: datetime.datetime | None | Unset = UNSET
    stopped_at: datetime.datetime | None | Unset = UNSET
    container_image: None | str | Unset = UNSET
    command_line: None | str | Unset = UNSET
    log_location: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        status = self.status

        native_job_id: None | str | Unset
        if isinstance(self.native_job_id, Unset):
            native_job_id = UNSET
        else:
            native_job_id = self.native_job_id

        requested_at: None | str | Unset
        if isinstance(self.requested_at, Unset):
            requested_at = UNSET
        elif isinstance(self.requested_at, datetime.datetime):
            requested_at = self.requested_at.isoformat()
        else:
            requested_at = self.requested_at

        started_at: None | str | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        stopped_at: None | str | Unset
        if isinstance(self.stopped_at, Unset):
            stopped_at = UNSET
        elif isinstance(self.stopped_at, datetime.datetime):
            stopped_at = self.stopped_at.isoformat()
        else:
            stopped_at = self.stopped_at

        container_image: None | str | Unset
        if isinstance(self.container_image, Unset):
            container_image = UNSET
        else:
            container_image = self.container_image

        command_line: None | str | Unset
        if isinstance(self.command_line, Unset):
            command_line = UNSET
        else:
            command_line = self.command_line

        log_location: None | str | Unset
        if isinstance(self.log_location, Unset):
            log_location = UNSET
        else:
            log_location = self.log_location

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "status": status,
            }
        )
        if native_job_id is not UNSET:
            field_dict["nativeJobId"] = native_job_id
        if requested_at is not UNSET:
            field_dict["requestedAt"] = requested_at
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if stopped_at is not UNSET:
            field_dict["stoppedAt"] = stopped_at
        if container_image is not UNSET:
            field_dict["containerImage"] = container_image
        if command_line is not UNSET:
            field_dict["commandLine"] = command_line
        if log_location is not UNSET:
            field_dict["logLocation"] = log_location

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        status = d.pop("status")

        def _parse_native_job_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        native_job_id = _parse_native_job_id(d.pop("nativeJobId", UNSET))

        def _parse_requested_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                requested_at_type_0 = isoparse(data)

                return requested_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        requested_at = _parse_requested_at(d.pop("requestedAt", UNSET))

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

        def _parse_stopped_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stopped_at_type_0 = isoparse(data)

                return stopped_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        stopped_at = _parse_stopped_at(d.pop("stoppedAt", UNSET))

        def _parse_container_image(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        container_image = _parse_container_image(d.pop("containerImage", UNSET))

        def _parse_command_line(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        command_line = _parse_command_line(d.pop("commandLine", UNSET))

        def _parse_log_location(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        log_location = _parse_log_location(d.pop("logLocation", UNSET))

        task = cls(
            name=name,
            status=status,
            native_job_id=native_job_id,
            requested_at=requested_at,
            started_at=started_at,
            stopped_at=stopped_at,
            container_image=container_image,
            command_line=command_line,
            log_location=log_location,
        )

        task.additional_properties = d
        return task

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
