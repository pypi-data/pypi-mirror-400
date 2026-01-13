from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateNotebookInstanceRequest")


@_attrs_define
class CreateNotebookInstanceRequest:
    """
    Attributes:
        name (str):
        instance_type (str): AWS EC2 Instance Type (see list of available options) Example: ml.t3.medium.
        accelerator_types (list[str]):
        volume_size_gb (int):
        git_repositories (list[str] | None | Unset): List of public git repositories to clone into the notebook
            instance.
        is_shared_with_project (bool | Unset): Whether the notebook is shared with the project Default: False.
    """

    name: str
    instance_type: str
    accelerator_types: list[str]
    volume_size_gb: int
    git_repositories: list[str] | None | Unset = UNSET
    is_shared_with_project: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        instance_type = self.instance_type

        accelerator_types = self.accelerator_types

        volume_size_gb = self.volume_size_gb

        git_repositories: list[str] | None | Unset
        if isinstance(self.git_repositories, Unset):
            git_repositories = UNSET
        elif isinstance(self.git_repositories, list):
            git_repositories = self.git_repositories

        else:
            git_repositories = self.git_repositories

        is_shared_with_project = self.is_shared_with_project

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "instanceType": instance_type,
                "acceleratorTypes": accelerator_types,
                "volumeSizeGB": volume_size_gb,
            }
        )
        if git_repositories is not UNSET:
            field_dict["gitRepositories"] = git_repositories
        if is_shared_with_project is not UNSET:
            field_dict["isSharedWithProject"] = is_shared_with_project

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        instance_type = d.pop("instanceType")

        accelerator_types = cast(list[str], d.pop("acceleratorTypes"))

        volume_size_gb = d.pop("volumeSizeGB")

        def _parse_git_repositories(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                git_repositories_type_0 = cast(list[str], data)

                return git_repositories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        git_repositories = _parse_git_repositories(d.pop("gitRepositories", UNSET))

        is_shared_with_project = d.pop("isSharedWithProject", UNSET)

        create_notebook_instance_request = cls(
            name=name,
            instance_type=instance_type,
            accelerator_types=accelerator_types,
            volume_size_gb=volume_size_gb,
            git_repositories=git_repositories,
            is_shared_with_project=is_shared_with_project,
        )

        create_notebook_instance_request.additional_properties = d
        return create_notebook_instance_request

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
