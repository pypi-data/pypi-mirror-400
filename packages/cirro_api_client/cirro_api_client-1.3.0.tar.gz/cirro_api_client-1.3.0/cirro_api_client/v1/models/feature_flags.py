from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FeatureFlags")


@_attrs_define
class FeatureFlags:
    """
    Attributes:
        sftp_enabled (bool):
        governance_enabled (bool):
        project_requests_enabled (bool):
        workspaces_enabled (bool):
        drive_enabled (bool):
    """

    sftp_enabled: bool
    governance_enabled: bool
    project_requests_enabled: bool
    workspaces_enabled: bool
    drive_enabled: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sftp_enabled = self.sftp_enabled

        governance_enabled = self.governance_enabled

        project_requests_enabled = self.project_requests_enabled

        workspaces_enabled = self.workspaces_enabled

        drive_enabled = self.drive_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sftpEnabled": sftp_enabled,
                "governanceEnabled": governance_enabled,
                "projectRequestsEnabled": project_requests_enabled,
                "workspacesEnabled": workspaces_enabled,
                "driveEnabled": drive_enabled,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sftp_enabled = d.pop("sftpEnabled")

        governance_enabled = d.pop("governanceEnabled")

        project_requests_enabled = d.pop("projectRequestsEnabled")

        workspaces_enabled = d.pop("workspacesEnabled")

        drive_enabled = d.pop("driveEnabled")

        feature_flags = cls(
            sftp_enabled=sftp_enabled,
            governance_enabled=governance_enabled,
            project_requests_enabled=project_requests_enabled,
            workspaces_enabled=workspaces_enabled,
            drive_enabled=drive_enabled,
        )

        feature_flags.additional_properties = d
        return feature_flags

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
