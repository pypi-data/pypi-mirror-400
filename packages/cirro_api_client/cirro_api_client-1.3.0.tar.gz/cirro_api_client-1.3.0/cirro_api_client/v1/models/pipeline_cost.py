from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PipelineCost")


@_attrs_define
class PipelineCost:
    """
    Attributes:
        total_cost (float | None | Unset): The total cost of running the pipeline
        is_estimate (bool | Unset): Is this an estimate of the cost?
        description (str | Unset): Description of the cost calculation
    """

    total_cost: float | None | Unset = UNSET
    is_estimate: bool | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_cost: float | None | Unset
        if isinstance(self.total_cost, Unset):
            total_cost = UNSET
        else:
            total_cost = self.total_cost

        is_estimate = self.is_estimate

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_cost is not UNSET:
            field_dict["totalCost"] = total_cost
        if is_estimate is not UNSET:
            field_dict["isEstimate"] = is_estimate
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_total_cost(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        total_cost = _parse_total_cost(d.pop("totalCost", UNSET))

        is_estimate = d.pop("isEstimate", UNSET)

        description = d.pop("description", UNSET)

        pipeline_cost = cls(
            total_cost=total_cost,
            is_estimate=is_estimate,
            description=description,
        )

        pipeline_cost.additional_properties = d
        return pipeline_cost

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
