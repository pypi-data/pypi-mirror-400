from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StopExecutionResponse")


@_attrs_define
class StopExecutionResponse:
    """
    Attributes:
        success (list[str] | Unset): List of job IDs that were successful in termination
        failed (list[str] | Unset): List of job IDs that were not successful in termination
    """

    success: list[str] | Unset = UNSET
    failed: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success: list[str] | Unset = UNSET
        if not isinstance(self.success, Unset):
            success = self.success

        failed: list[str] | Unset = UNSET
        if not isinstance(self.failed, Unset):
            failed = self.failed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if failed is not UNSET:
            field_dict["failed"] = failed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = cast(list[str], d.pop("success", UNSET))

        failed = cast(list[str], d.pop("failed", UNSET))

        stop_execution_response = cls(
            success=success,
            failed=failed,
        )

        stop_execution_response.additional_properties = d
        return stop_execution_response

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
