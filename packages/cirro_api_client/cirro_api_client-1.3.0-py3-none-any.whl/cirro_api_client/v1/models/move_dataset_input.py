from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MoveDatasetInput")


@_attrs_define
class MoveDatasetInput:
    """
    Attributes:
        dataset_id (str):
        source_project_id (str):
        target_project_id (str):
    """

    dataset_id: str
    source_project_id: str
    target_project_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dataset_id = self.dataset_id

        source_project_id = self.source_project_id

        target_project_id = self.target_project_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datasetId": dataset_id,
                "sourceProjectId": source_project_id,
                "targetProjectId": target_project_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dataset_id = d.pop("datasetId")

        source_project_id = d.pop("sourceProjectId")

        target_project_id = d.pop("targetProjectId")

        move_dataset_input = cls(
            dataset_id=dataset_id,
            source_project_id=source_project_id,
            target_project_id=target_project_id,
        )

        move_dataset_input.additional_properties = d
        return move_dataset_input

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
