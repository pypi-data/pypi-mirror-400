from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_cost import GroupCost
    from ..models.task_cost import TaskCost


T = TypeVar("T", bound="CostResponse")


@_attrs_define
class CostResponse:
    """
    Attributes:
        total_cost (float | Unset): Total cost
        groups (list[GroupCost] | Unset): Costs grouped by the task status
        tasks (list[TaskCost] | Unset): Costs for each workflow task
        is_estimate (bool | Unset): Whether this is an estimated cost
    """

    total_cost: float | Unset = UNSET
    groups: list[GroupCost] | Unset = UNSET
    tasks: list[TaskCost] | Unset = UNSET
    is_estimate: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_cost = self.total_cost

        groups: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)

        tasks: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tasks, Unset):
            tasks = []
            for tasks_item_data in self.tasks:
                tasks_item = tasks_item_data.to_dict()
                tasks.append(tasks_item)

        is_estimate = self.is_estimate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_cost is not UNSET:
            field_dict["totalCost"] = total_cost
        if groups is not UNSET:
            field_dict["groups"] = groups
        if tasks is not UNSET:
            field_dict["tasks"] = tasks
        if is_estimate is not UNSET:
            field_dict["isEstimate"] = is_estimate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_cost import GroupCost
        from ..models.task_cost import TaskCost

        d = dict(src_dict)
        total_cost = d.pop("totalCost", UNSET)

        _groups = d.pop("groups", UNSET)
        groups: list[GroupCost] | Unset = UNSET
        if _groups is not UNSET:
            groups = []
            for groups_item_data in _groups:
                groups_item = GroupCost.from_dict(groups_item_data)

                groups.append(groups_item)

        _tasks = d.pop("tasks", UNSET)
        tasks: list[TaskCost] | Unset = UNSET
        if _tasks is not UNSET:
            tasks = []
            for tasks_item_data in _tasks:
                tasks_item = TaskCost.from_dict(tasks_item_data)

                tasks.append(tasks_item)

        is_estimate = d.pop("isEstimate", UNSET)

        cost_response = cls(
            total_cost=total_cost,
            groups=groups,
            tasks=tasks,
            is_estimate=is_estimate,
        )

        cost_response.additional_properties = d
        return cost_response

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
