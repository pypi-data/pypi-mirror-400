from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_status import AgentStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_tags import AgentTags


T = TypeVar("T", bound="Agent")


@_attrs_define
class Agent:
    """Details of the agent

    Attributes:
        status (AgentStatus): The status of the agent
        id (str | Unset): The unique ID of the agent
        name (str | Unset): The display name of the agent
        tags (AgentTags | Unset): Tags associated with the agent
    """

    status: AgentStatus
    id: str | Unset = UNSET
    name: str | Unset = UNSET
    tags: AgentTags | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        id = self.id

        name = self.name

        tags: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_tags import AgentTags

        d = dict(src_dict)
        status = AgentStatus(d.pop("status"))

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _tags = d.pop("tags", UNSET)
        tags: AgentTags | Unset
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = AgentTags.from_dict(_tags)

        agent = cls(
            status=status,
            id=id,
            name=name,
            tags=tags,
        )

        agent.additional_properties = d
        return agent

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
