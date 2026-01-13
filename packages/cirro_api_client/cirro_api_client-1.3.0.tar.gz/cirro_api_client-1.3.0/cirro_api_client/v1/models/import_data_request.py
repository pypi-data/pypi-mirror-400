from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.import_data_request_download_method import ImportDataRequestDownloadMethod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tag import Tag


T = TypeVar("T", bound="ImportDataRequest")


@_attrs_define
class ImportDataRequest:
    """
    Attributes:
        name (str): Name of the dataset
        public_ids (list[str]):
        description (str | Unset): Description of the dataset
        tags (list[Tag] | None | Unset): List of tags to apply to the dataset
        download_method (ImportDataRequestDownloadMethod | Unset): Method to download FastQ files Default:
            ImportDataRequestDownloadMethod.SRATOOLS.
        dbgap_key (None | str | Unset): dbGaP repository key (used to access protected data on SRA)
    """

    name: str
    public_ids: list[str]
    description: str | Unset = UNSET
    tags: list[Tag] | None | Unset = UNSET
    download_method: ImportDataRequestDownloadMethod | Unset = ImportDataRequestDownloadMethod.SRATOOLS
    dbgap_key: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        public_ids = self.public_ids

        description = self.description

        tags: list[dict[str, Any]] | None | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = []
            for tags_type_0_item_data in self.tags:
                tags_type_0_item = tags_type_0_item_data.to_dict()
                tags.append(tags_type_0_item)

        else:
            tags = self.tags

        download_method: str | Unset = UNSET
        if not isinstance(self.download_method, Unset):
            download_method = self.download_method.value

        dbgap_key: None | str | Unset
        if isinstance(self.dbgap_key, Unset):
            dbgap_key = UNSET
        else:
            dbgap_key = self.dbgap_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "publicIds": public_ids,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags
        if download_method is not UNSET:
            field_dict["downloadMethod"] = download_method
        if dbgap_key is not UNSET:
            field_dict["dbgapKey"] = dbgap_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag import Tag

        d = dict(src_dict)
        name = d.pop("name")

        public_ids = cast(list[str], d.pop("publicIds"))

        description = d.pop("description", UNSET)

        def _parse_tags(data: object) -> list[Tag] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = []
                _tags_type_0 = data
                for tags_type_0_item_data in _tags_type_0:
                    tags_type_0_item = Tag.from_dict(tags_type_0_item_data)

                    tags_type_0.append(tags_type_0_item)

                return tags_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Tag] | None | Unset, data)

        tags = _parse_tags(d.pop("tags", UNSET))

        _download_method = d.pop("downloadMethod", UNSET)
        download_method: ImportDataRequestDownloadMethod | Unset
        if isinstance(_download_method, Unset):
            download_method = UNSET
        else:
            download_method = ImportDataRequestDownloadMethod(_download_method)

        def _parse_dbgap_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dbgap_key = _parse_dbgap_key(d.pop("dbgapKey", UNSET))

        import_data_request = cls(
            name=name,
            public_ids=public_ids,
            description=description,
            tags=tags,
            download_method=download_method,
            dbgap_key=dbgap_key,
        )

        import_data_request.additional_properties = d
        return import_data_request

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
