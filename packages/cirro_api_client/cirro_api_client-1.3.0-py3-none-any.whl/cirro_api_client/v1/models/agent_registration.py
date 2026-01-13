from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AgentRegistration")


@_attrs_define
class AgentRegistration:
    """
    Attributes:
        local_ip (str):
        remote_ip (str):
        agent_version (str):
        hostname (str):
        os (str):
    """

    local_ip: str
    remote_ip: str
    agent_version: str
    hostname: str
    os: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        local_ip = self.local_ip

        remote_ip = self.remote_ip

        agent_version = self.agent_version

        hostname = self.hostname

        os = self.os

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "localIp": local_ip,
                "remoteIp": remote_ip,
                "agentVersion": agent_version,
                "hostname": hostname,
                "os": os,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        local_ip = d.pop("localIp")

        remote_ip = d.pop("remoteIp")

        agent_version = d.pop("agentVersion")

        hostname = d.pop("hostname")

        os = d.pop("os")

        agent_registration = cls(
            local_ip=local_ip,
            remote_ip=remote_ip,
            agent_version=agent_version,
            hostname=hostname,
            os=os,
        )

        agent_registration.additional_properties = d
        return agent_registration

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
