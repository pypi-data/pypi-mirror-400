from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sharing_type import SharingType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mounted_dataset import MountedDataset
    from ..models.workspace_compute_config import WorkspaceComputeConfig


T = TypeVar("T", bound="WorkspaceInput")


@_attrs_define
class WorkspaceInput:
    """
    Attributes:
        name (str): Name of the workspace. Example: my-workspace.
        mounted_datasets (list[MountedDataset]): List of datasets to mount into the workspace.
        compute_config (WorkspaceComputeConfig): Configuration parameters for a containerized workspace compute
            environment.
        sharing_type (SharingType):
        description (str | Unset): Description of the workspace.
        environment_id (None | str | Unset): ID of the predefined workspace environment to use.
        auto_stop_timeout (int | None | Unset): Time period (in hours) to automatically stop the workspace if running
    """

    name: str
    mounted_datasets: list[MountedDataset]
    compute_config: WorkspaceComputeConfig
    sharing_type: SharingType
    description: str | Unset = UNSET
    environment_id: None | str | Unset = UNSET
    auto_stop_timeout: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        mounted_datasets = []
        for mounted_datasets_item_data in self.mounted_datasets:
            mounted_datasets_item = mounted_datasets_item_data.to_dict()
            mounted_datasets.append(mounted_datasets_item)

        compute_config = self.compute_config.to_dict()

        sharing_type = self.sharing_type.value

        description = self.description

        environment_id: None | str | Unset
        if isinstance(self.environment_id, Unset):
            environment_id = UNSET
        else:
            environment_id = self.environment_id

        auto_stop_timeout: int | None | Unset
        if isinstance(self.auto_stop_timeout, Unset):
            auto_stop_timeout = UNSET
        else:
            auto_stop_timeout = self.auto_stop_timeout

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "mountedDatasets": mounted_datasets,
                "computeConfig": compute_config,
                "sharingType": sharing_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if environment_id is not UNSET:
            field_dict["environmentId"] = environment_id
        if auto_stop_timeout is not UNSET:
            field_dict["autoStopTimeout"] = auto_stop_timeout

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mounted_dataset import MountedDataset
        from ..models.workspace_compute_config import WorkspaceComputeConfig

        d = dict(src_dict)
        name = d.pop("name")

        mounted_datasets = []
        _mounted_datasets = d.pop("mountedDatasets")
        for mounted_datasets_item_data in _mounted_datasets:
            mounted_datasets_item = MountedDataset.from_dict(mounted_datasets_item_data)

            mounted_datasets.append(mounted_datasets_item)

        compute_config = WorkspaceComputeConfig.from_dict(d.pop("computeConfig"))

        sharing_type = SharingType(d.pop("sharingType"))

        description = d.pop("description", UNSET)

        def _parse_environment_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        environment_id = _parse_environment_id(d.pop("environmentId", UNSET))

        def _parse_auto_stop_timeout(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        auto_stop_timeout = _parse_auto_stop_timeout(d.pop("autoStopTimeout", UNSET))

        workspace_input = cls(
            name=name,
            mounted_datasets=mounted_datasets,
            compute_config=compute_config,
            sharing_type=sharing_type,
            description=description,
            environment_id=environment_id,
            auto_stop_timeout=auto_stop_timeout,
        )

        workspace_input.additional_properties = d
        return workspace_input

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
