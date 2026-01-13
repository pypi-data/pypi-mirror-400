from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.column_definition import ColumnDefinition


T = TypeVar("T", bound="Table")


@_attrs_define
class Table:
    """
    Attributes:
        desc (str):
        name (str | Unset): User-friendly name of asset
        type_ (str | Unset): Type of file Example: parquet.
        rows (int | Unset): Number of rows in table
        path (str | Unset): Relative path to asset
        cols (list[ColumnDefinition] | None | Unset):
    """

    desc: str
    name: str | Unset = UNSET
    type_: str | Unset = UNSET
    rows: int | Unset = UNSET
    path: str | Unset = UNSET
    cols: list[ColumnDefinition] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        desc = self.desc

        name = self.name

        type_ = self.type_

        rows = self.rows

        path = self.path

        cols: list[dict[str, Any]] | None | Unset
        if isinstance(self.cols, Unset):
            cols = UNSET
        elif isinstance(self.cols, list):
            cols = []
            for cols_type_0_item_data in self.cols:
                cols_type_0_item = cols_type_0_item_data.to_dict()
                cols.append(cols_type_0_item)

        else:
            cols = self.cols

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "desc": desc,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if rows is not UNSET:
            field_dict["rows"] = rows
        if path is not UNSET:
            field_dict["path"] = path
        if cols is not UNSET:
            field_dict["cols"] = cols

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.column_definition import ColumnDefinition

        d = dict(src_dict)
        desc = d.pop("desc")

        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        rows = d.pop("rows", UNSET)

        path = d.pop("path", UNSET)

        def _parse_cols(data: object) -> list[ColumnDefinition] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                cols_type_0 = []
                _cols_type_0 = data
                for cols_type_0_item_data in _cols_type_0:
                    cols_type_0_item = ColumnDefinition.from_dict(cols_type_0_item_data)

                    cols_type_0.append(cols_type_0_item)

                return cols_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ColumnDefinition] | None | Unset, data)

        cols = _parse_cols(d.pop("cols", UNSET))

        table = cls(
            desc=desc,
            name=name,
            type_=type_,
            rows=rows,
            path=path,
            cols=cols,
        )

        table.additional_properties = d
        return table

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
