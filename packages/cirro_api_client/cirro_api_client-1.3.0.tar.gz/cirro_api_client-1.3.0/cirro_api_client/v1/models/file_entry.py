from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_entry_metadata import FileEntryMetadata


T = TypeVar("T", bound="FileEntry")


@_attrs_define
class FileEntry:
    """
    Attributes:
        path (str | Unset): Relative path to file Example: data/fastq/SRX12875516_SRR16674827_1.fastq.gz.
        size (int | Unset): File size (in bytes) Example: 1435658507.
        metadata (FileEntryMetadata | Unset): Metadata associated with the file Example: {'read': 1}.
    """

    path: str | Unset = UNSET
    size: int | Unset = UNSET
    metadata: FileEntryMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        size = self.size

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if path is not UNSET:
            field_dict["path"] = path
        if size is not UNSET:
            field_dict["size"] = size
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_entry_metadata import FileEntryMetadata

        d = dict(src_dict)
        path = d.pop("path", UNSET)

        size = d.pop("size", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: FileEntryMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = FileEntryMetadata.from_dict(_metadata)

        file_entry = cls(
            path=path,
            size=size,
            metadata=metadata,
        )

        file_entry.additional_properties = d
        return file_entry

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
