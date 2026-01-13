from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.repository_type import RepositoryType
from ..models.sync_status import SyncStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomPipelineSettings")


@_attrs_define
class CustomPipelineSettings:
    """Used to describe the location of the process definition dependencies

    Attributes:
        repository (str): GitHub repository that contains the process definition Example: CirroBio/my-pipeline.
        branch (str | Unset): Branch, tag, or commit hash of the repo that contains the process definition Default:
            'main'.
        folder (str | Unset): Folder within the repo that contains the process definition Default: '.cirro'.
        repository_type (None | RepositoryType | Unset):
        last_sync (datetime.datetime | None | Unset): Time of last sync
        sync_status (None | SyncStatus | Unset):
        commit_hash (None | str | Unset): Commit hash of the last successful sync
        is_authorized (bool | Unset): Whether we are authorized to access the repository Default: False.
    """

    repository: str
    branch: str | Unset = "main"
    folder: str | Unset = ".cirro"
    repository_type: None | RepositoryType | Unset = UNSET
    last_sync: datetime.datetime | None | Unset = UNSET
    sync_status: None | SyncStatus | Unset = UNSET
    commit_hash: None | str | Unset = UNSET
    is_authorized: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository = self.repository

        branch = self.branch

        folder = self.folder

        repository_type: None | str | Unset
        if isinstance(self.repository_type, Unset):
            repository_type = UNSET
        elif isinstance(self.repository_type, RepositoryType):
            repository_type = self.repository_type.value
        else:
            repository_type = self.repository_type

        last_sync: None | str | Unset
        if isinstance(self.last_sync, Unset):
            last_sync = UNSET
        elif isinstance(self.last_sync, datetime.datetime):
            last_sync = self.last_sync.isoformat()
        else:
            last_sync = self.last_sync

        sync_status: None | str | Unset
        if isinstance(self.sync_status, Unset):
            sync_status = UNSET
        elif isinstance(self.sync_status, SyncStatus):
            sync_status = self.sync_status.value
        else:
            sync_status = self.sync_status

        commit_hash: None | str | Unset
        if isinstance(self.commit_hash, Unset):
            commit_hash = UNSET
        else:
            commit_hash = self.commit_hash

        is_authorized = self.is_authorized

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository": repository,
            }
        )
        if branch is not UNSET:
            field_dict["branch"] = branch
        if folder is not UNSET:
            field_dict["folder"] = folder
        if repository_type is not UNSET:
            field_dict["repositoryType"] = repository_type
        if last_sync is not UNSET:
            field_dict["lastSync"] = last_sync
        if sync_status is not UNSET:
            field_dict["syncStatus"] = sync_status
        if commit_hash is not UNSET:
            field_dict["commitHash"] = commit_hash
        if is_authorized is not UNSET:
            field_dict["isAuthorized"] = is_authorized

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repository = d.pop("repository")

        branch = d.pop("branch", UNSET)

        folder = d.pop("folder", UNSET)

        def _parse_repository_type(data: object) -> None | RepositoryType | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                repository_type_type_1 = RepositoryType(data)

                return repository_type_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RepositoryType | Unset, data)

        repository_type = _parse_repository_type(d.pop("repositoryType", UNSET))

        def _parse_last_sync(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_sync_type_0 = isoparse(data)

                return last_sync_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_sync = _parse_last_sync(d.pop("lastSync", UNSET))

        def _parse_sync_status(data: object) -> None | SyncStatus | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                sync_status_type_1 = SyncStatus(data)

                return sync_status_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SyncStatus | Unset, data)

        sync_status = _parse_sync_status(d.pop("syncStatus", UNSET))

        def _parse_commit_hash(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_hash = _parse_commit_hash(d.pop("commitHash", UNSET))

        is_authorized = d.pop("isAuthorized", UNSET)

        custom_pipeline_settings = cls(
            repository=repository,
            branch=branch,
            folder=folder,
            repository_type=repository_type,
            last_sync=last_sync,
            sync_status=sync_status,
            commit_hash=commit_hash,
            is_authorized=is_authorized,
        )

        custom_pipeline_settings.additional_properties = d
        return custom_pipeline_settings

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
