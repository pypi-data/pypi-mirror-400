from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.agent_status import AgentStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_detail_environment_configuration import AgentDetailEnvironmentConfiguration
    from ..models.agent_detail_tags import AgentDetailTags
    from ..models.agent_registration import AgentRegistration


T = TypeVar("T", bound="AgentDetail")


@_attrs_define
class AgentDetail:
    """
    Attributes:
        id (str):
        name (str):
        agent_role_arn (str):
        status (AgentStatus): The status of the agent
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        registration (AgentRegistration | None | Unset):
        tags (AgentDetailTags | None | Unset):
        environment_configuration (AgentDetailEnvironmentConfiguration | None | Unset):
    """

    id: str
    name: str
    agent_role_arn: str
    status: AgentStatus
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    registration: AgentRegistration | None | Unset = UNSET
    tags: AgentDetailTags | None | Unset = UNSET
    environment_configuration: AgentDetailEnvironmentConfiguration | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.agent_detail_environment_configuration import AgentDetailEnvironmentConfiguration
        from ..models.agent_detail_tags import AgentDetailTags
        from ..models.agent_registration import AgentRegistration

        id = self.id

        name = self.name

        agent_role_arn = self.agent_role_arn

        status = self.status.value

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        registration: dict[str, Any] | None | Unset
        if isinstance(self.registration, Unset):
            registration = UNSET
        elif isinstance(self.registration, AgentRegistration):
            registration = self.registration.to_dict()
        else:
            registration = self.registration

        tags: dict[str, Any] | None | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, AgentDetailTags):
            tags = self.tags.to_dict()
        else:
            tags = self.tags

        environment_configuration: dict[str, Any] | None | Unset
        if isinstance(self.environment_configuration, Unset):
            environment_configuration = UNSET
        elif isinstance(self.environment_configuration, AgentDetailEnvironmentConfiguration):
            environment_configuration = self.environment_configuration.to_dict()
        else:
            environment_configuration = self.environment_configuration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "agentRoleArn": agent_role_arn,
                "status": status,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if registration is not UNSET:
            field_dict["registration"] = registration
        if tags is not UNSET:
            field_dict["tags"] = tags
        if environment_configuration is not UNSET:
            field_dict["environmentConfiguration"] = environment_configuration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_detail_environment_configuration import AgentDetailEnvironmentConfiguration
        from ..models.agent_detail_tags import AgentDetailTags
        from ..models.agent_registration import AgentRegistration

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        agent_role_arn = d.pop("agentRoleArn")

        status = AgentStatus(d.pop("status"))

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_registration(data: object) -> AgentRegistration | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                registration_type_1 = AgentRegistration.from_dict(data)

                return registration_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AgentRegistration | None | Unset, data)

        registration = _parse_registration(d.pop("registration", UNSET))

        def _parse_tags(data: object) -> AgentDetailTags | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tags_type_0 = AgentDetailTags.from_dict(data)

                return tags_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AgentDetailTags | None | Unset, data)

        tags = _parse_tags(d.pop("tags", UNSET))

        def _parse_environment_configuration(data: object) -> AgentDetailEnvironmentConfiguration | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                environment_configuration_type_0 = AgentDetailEnvironmentConfiguration.from_dict(data)

                return environment_configuration_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AgentDetailEnvironmentConfiguration | None | Unset, data)

        environment_configuration = _parse_environment_configuration(d.pop("environmentConfiguration", UNSET))

        agent_detail = cls(
            id=id,
            name=name,
            agent_role_arn=agent_role_arn,
            status=status,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            registration=registration,
            tags=tags,
            environment_configuration=environment_configuration,
        )

        agent_detail.additional_properties = d
        return agent_detail

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
