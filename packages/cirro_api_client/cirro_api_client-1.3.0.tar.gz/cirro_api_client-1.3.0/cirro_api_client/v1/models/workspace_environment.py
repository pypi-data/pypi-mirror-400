from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.version_specification import VersionSpecification
    from ..models.workspace_compute_config import WorkspaceComputeConfig


T = TypeVar("T", bound="WorkspaceEnvironment")


@_attrs_define
class WorkspaceEnvironment:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        category (str):
        default_compute_config (WorkspaceComputeConfig): Configuration parameters for a containerized workspace compute
            environment.
        versions (list[VersionSpecification]):
        owner (str):
    """

    id: str
    name: str
    description: str
    category: str
    default_compute_config: WorkspaceComputeConfig
    versions: list[VersionSpecification]
    owner: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        category = self.category

        default_compute_config = self.default_compute_config.to_dict()

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        owner = self.owner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "category": category,
                "defaultComputeConfig": default_compute_config,
                "versions": versions,
                "owner": owner,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.version_specification import VersionSpecification
        from ..models.workspace_compute_config import WorkspaceComputeConfig

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        category = d.pop("category")

        default_compute_config = WorkspaceComputeConfig.from_dict(d.pop("defaultComputeConfig"))

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = VersionSpecification.from_dict(versions_item_data)

            versions.append(versions_item)

        owner = d.pop("owner")

        workspace_environment = cls(
            id=id,
            name=name,
            description=description,
            category=category,
            default_compute_config=default_compute_config,
            versions=versions,
            owner=owner,
        )

        workspace_environment.additional_properties = d
        return workspace_environment

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
