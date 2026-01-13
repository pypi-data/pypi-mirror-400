from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compute_environment_configuration_input_properties import (
        ComputeEnvironmentConfigurationInputProperties,
    )


T = TypeVar("T", bound="ComputeEnvironmentConfigurationInput")


@_attrs_define
class ComputeEnvironmentConfigurationInput:
    """
    Attributes:
        name (str):
        agent_id (None | str | Unset):
        properties (ComputeEnvironmentConfigurationInputProperties | None | Unset):
    """

    name: str
    agent_id: None | str | Unset = UNSET
    properties: ComputeEnvironmentConfigurationInputProperties | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.compute_environment_configuration_input_properties import (
            ComputeEnvironmentConfigurationInputProperties,
        )

        name = self.name

        agent_id: None | str | Unset
        if isinstance(self.agent_id, Unset):
            agent_id = UNSET
        else:
            agent_id = self.agent_id

        properties: dict[str, Any] | None | Unset
        if isinstance(self.properties, Unset):
            properties = UNSET
        elif isinstance(self.properties, ComputeEnvironmentConfigurationInputProperties):
            properties = self.properties.to_dict()
        else:
            properties = self.properties

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if agent_id is not UNSET:
            field_dict["agentId"] = agent_id
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compute_environment_configuration_input_properties import (
            ComputeEnvironmentConfigurationInputProperties,
        )

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_agent_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        agent_id = _parse_agent_id(d.pop("agentId", UNSET))

        def _parse_properties(data: object) -> ComputeEnvironmentConfigurationInputProperties | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                properties_type_0 = ComputeEnvironmentConfigurationInputProperties.from_dict(data)

                return properties_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ComputeEnvironmentConfigurationInputProperties | None | Unset, data)

        properties = _parse_properties(d.pop("properties", UNSET))

        compute_environment_configuration_input = cls(
            name=name,
            agent_id=agent_id,
            properties=properties,
        )

        compute_environment_configuration_input.additional_properties = d
        return compute_environment_configuration_input

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
