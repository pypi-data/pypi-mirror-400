from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_file import DataFile
    from ..models.sample_metadata import SampleMetadata


T = TypeVar("T", bound="Sample")


@_attrs_define
class Sample:
    """
    Attributes:
        id (str):
        name (str):
        metadata (None | SampleMetadata | Unset):
        files (list[DataFile] | None | Unset): Files associated with this sample
        dataset_ids (list[str] | None | Unset):
        created_at (datetime.datetime | None | Unset):
        updated_at (datetime.datetime | None | Unset):
    """

    id: str
    name: str
    metadata: None | SampleMetadata | Unset = UNSET
    files: list[DataFile] | None | Unset = UNSET
    dataset_ids: list[str] | None | Unset = UNSET
    created_at: datetime.datetime | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sample_metadata import SampleMetadata

        id = self.id

        name = self.name

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, SampleMetadata):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        files: list[dict[str, Any]] | None | Unset
        if isinstance(self.files, Unset):
            files = UNSET
        elif isinstance(self.files, list):
            files = []
            for files_type_0_item_data in self.files:
                files_type_0_item = files_type_0_item_data.to_dict()
                files.append(files_type_0_item)

        else:
            files = self.files

        dataset_ids: list[str] | None | Unset
        if isinstance(self.dataset_ids, Unset):
            dataset_ids = UNSET
        elif isinstance(self.dataset_ids, list):
            dataset_ids = self.dataset_ids

        else:
            dataset_ids = self.dataset_ids

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if files is not UNSET:
            field_dict["files"] = files
        if dataset_ids is not UNSET:
            field_dict["datasetIds"] = dataset_ids
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_file import DataFile
        from ..models.sample_metadata import SampleMetadata

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        def _parse_metadata(data: object) -> None | SampleMetadata | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = SampleMetadata.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SampleMetadata | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_files(data: object) -> list[DataFile] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                files_type_0 = []
                _files_type_0 = data
                for files_type_0_item_data in _files_type_0:
                    files_type_0_item = DataFile.from_dict(files_type_0_item_data)

                    files_type_0.append(files_type_0_item)

                return files_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[DataFile] | None | Unset, data)

        files = _parse_files(d.pop("files", UNSET))

        def _parse_dataset_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                dataset_ids_type_0 = cast(list[str], data)

                return dataset_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        dataset_ids = _parse_dataset_ids(d.pop("datasetIds", UNSET))

        def _parse_created_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = isoparse(data)

                return created_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        created_at = _parse_created_at(d.pop("createdAt", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updatedAt", UNSET))

        sample = cls(
            id=id,
            name=name,
            metadata=metadata,
            files=files,
            dataset_ids=dataset_ids,
            created_at=created_at,
            updated_at=updated_at,
        )

        sample.additional_properties = d
        return sample

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
