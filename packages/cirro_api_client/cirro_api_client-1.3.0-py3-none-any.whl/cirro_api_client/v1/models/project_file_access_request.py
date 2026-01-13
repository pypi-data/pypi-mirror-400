from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_access_type import ProjectAccessType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectFileAccessRequest")


@_attrs_define
class ProjectFileAccessRequest:
    """
    Attributes:
        access_type (ProjectAccessType):
        dataset_id (None | str | Unset):
        token_lifetime_hours (int | None | Unset):
    """

    access_type: ProjectAccessType
    dataset_id: None | str | Unset = UNSET
    token_lifetime_hours: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_type = self.access_type.value

        dataset_id: None | str | Unset
        if isinstance(self.dataset_id, Unset):
            dataset_id = UNSET
        else:
            dataset_id = self.dataset_id

        token_lifetime_hours: int | None | Unset
        if isinstance(self.token_lifetime_hours, Unset):
            token_lifetime_hours = UNSET
        else:
            token_lifetime_hours = self.token_lifetime_hours

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accessType": access_type,
            }
        )
        if dataset_id is not UNSET:
            field_dict["datasetId"] = dataset_id
        if token_lifetime_hours is not UNSET:
            field_dict["tokenLifetimeHours"] = token_lifetime_hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_type = ProjectAccessType(d.pop("accessType"))

        def _parse_dataset_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dataset_id = _parse_dataset_id(d.pop("datasetId", UNSET))

        def _parse_token_lifetime_hours(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        token_lifetime_hours = _parse_token_lifetime_hours(d.pop("tokenLifetimeHours", UNSET))

        project_file_access_request = cls(
            access_type=access_type,
            dataset_id=dataset_id,
            token_lifetime_hours=token_lifetime_hours,
        )

        project_file_access_request.additional_properties = d
        return project_file_access_request

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
