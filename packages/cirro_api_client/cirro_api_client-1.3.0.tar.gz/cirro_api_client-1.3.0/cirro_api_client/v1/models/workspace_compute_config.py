from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.workspace_compute_config_environment_variables import WorkspaceComputeConfigEnvironmentVariables


T = TypeVar("T", bound="WorkspaceComputeConfig")


@_attrs_define
class WorkspaceComputeConfig:
    """Configuration parameters for a containerized workspace compute environment.

    Attributes:
        container_image_uri (str): Fully qualified container image URI (including registry, repository, and tag).
        cpu (int | Unset): Number of vCPU cores allocated to the workspace. Example: 4.
        memory_gi_b (int | Unset): Memory allocated to the workspace container in GiB. Example: 8.
        volume_size_gi_b (int | Unset): Persistent storage volume size allocated to the workspace in GiB. Example: 50.
        gpu (int | Unset): Number of GPUs allocated to the workspace Example: 1.
        environment_variables (None | Unset | WorkspaceComputeConfigEnvironmentVariables): Map of environment variables
            injected into the container at runtime. Keys must be non-blank. Example: {'ENV_MODE': 'production', 'LOG_LEVEL':
            'debug'}.
        local_port (int | Unset): User-facing web server port (http). Example: 8080.
    """

    container_image_uri: str
    cpu: int | Unset = UNSET
    memory_gi_b: int | Unset = UNSET
    volume_size_gi_b: int | Unset = UNSET
    gpu: int | Unset = UNSET
    environment_variables: None | Unset | WorkspaceComputeConfigEnvironmentVariables = UNSET
    local_port: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.workspace_compute_config_environment_variables import WorkspaceComputeConfigEnvironmentVariables

        container_image_uri = self.container_image_uri

        cpu = self.cpu

        memory_gi_b = self.memory_gi_b

        volume_size_gi_b = self.volume_size_gi_b

        gpu = self.gpu

        environment_variables: dict[str, Any] | None | Unset
        if isinstance(self.environment_variables, Unset):
            environment_variables = UNSET
        elif isinstance(self.environment_variables, WorkspaceComputeConfigEnvironmentVariables):
            environment_variables = self.environment_variables.to_dict()
        else:
            environment_variables = self.environment_variables

        local_port = self.local_port

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "containerImageUri": container_image_uri,
            }
        )
        if cpu is not UNSET:
            field_dict["cpu"] = cpu
        if memory_gi_b is not UNSET:
            field_dict["memoryGiB"] = memory_gi_b
        if volume_size_gi_b is not UNSET:
            field_dict["volumeSizeGiB"] = volume_size_gi_b
        if gpu is not UNSET:
            field_dict["gpu"] = gpu
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if local_port is not UNSET:
            field_dict["localPort"] = local_port

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workspace_compute_config_environment_variables import WorkspaceComputeConfigEnvironmentVariables

        d = dict(src_dict)
        container_image_uri = d.pop("containerImageUri")

        cpu = d.pop("cpu", UNSET)

        memory_gi_b = d.pop("memoryGiB", UNSET)

        volume_size_gi_b = d.pop("volumeSizeGiB", UNSET)

        gpu = d.pop("gpu", UNSET)

        def _parse_environment_variables(data: object) -> None | Unset | WorkspaceComputeConfigEnvironmentVariables:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                environment_variables_type_0 = WorkspaceComputeConfigEnvironmentVariables.from_dict(data)

                return environment_variables_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | WorkspaceComputeConfigEnvironmentVariables, data)

        environment_variables = _parse_environment_variables(d.pop("environmentVariables", UNSET))

        local_port = d.pop("localPort", UNSET)

        workspace_compute_config = cls(
            container_image_uri=container_image_uri,
            cpu=cpu,
            memory_gi_b=memory_gi_b,
            volume_size_gi_b=volume_size_gi_b,
            gpu=gpu,
            environment_variables=environment_variables,
            local_port=local_port,
        )

        workspace_compute_config.additional_properties = d
        return workspace_compute_config

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
