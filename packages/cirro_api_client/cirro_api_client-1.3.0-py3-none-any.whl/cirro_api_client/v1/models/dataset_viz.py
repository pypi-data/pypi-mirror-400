from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_viz_config import DatasetVizConfig


T = TypeVar("T", bound="DatasetViz")


@_attrs_define
class DatasetViz:
    """
    Attributes:
        path (str | Unset): Path to viz configuration, if applicable
        name (str | Unset): Name of viz
        desc (str | Unset): Description of viz
        type_ (str | Unset): Type of viz Example: vitescce.
        config (DatasetVizConfig | Unset): Config or path to config used to render viz
    """

    path: str | Unset = UNSET
    name: str | Unset = UNSET
    desc: str | Unset = UNSET
    type_: str | Unset = UNSET
    config: DatasetVizConfig | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        name = self.name

        desc = self.desc

        type_ = self.type_

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if path is not UNSET:
            field_dict["path"] = path
        if name is not UNSET:
            field_dict["name"] = name
        if desc is not UNSET:
            field_dict["desc"] = desc
        if type_ is not UNSET:
            field_dict["type"] = type_
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_viz_config import DatasetVizConfig

        d = dict(src_dict)
        path = d.pop("path", UNSET)

        name = d.pop("name", UNSET)

        desc = d.pop("desc", UNSET)

        type_ = d.pop("type", UNSET)

        _config = d.pop("config", UNSET)
        config: DatasetVizConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = DatasetVizConfig.from_dict(_config)

        dataset_viz = cls(
            path=path,
            name=name,
            desc=desc,
            type_=type_,
            config=config,
        )

        dataset_viz.additional_properties = d
        return dataset_viz

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
