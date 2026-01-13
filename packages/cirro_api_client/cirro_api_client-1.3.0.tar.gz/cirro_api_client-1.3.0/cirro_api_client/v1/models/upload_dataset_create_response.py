from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UploadDatasetCreateResponse")


@_attrs_define
class UploadDatasetCreateResponse:
    """
    Attributes:
        id (str):
        message (str):
        upload_path (str):
        bucket (str):
    """

    id: str
    message: str
    upload_path: str
    bucket: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        message = self.message

        upload_path = self.upload_path

        bucket = self.bucket

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "message": message,
                "uploadPath": upload_path,
                "bucket": bucket,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        message = d.pop("message")

        upload_path = d.pop("uploadPath")

        bucket = d.pop("bucket")

        upload_dataset_create_response = cls(
            id=id,
            message=message,
            upload_path=upload_path,
            bucket=bucket,
        )

        upload_dataset_create_response.additional_properties = d
        return upload_dataset_create_response

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
