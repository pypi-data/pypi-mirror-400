from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.error_message import ErrorMessage


T = TypeVar("T", bound="PortalErrorResponse")


@_attrs_define
class PortalErrorResponse:
    """
    Attributes:
        status_code (int):
        error_code (str):
        error_detail (str):
        errors (list[ErrorMessage]):
    """

    status_code: int
    error_code: str
    error_detail: str
    errors: list[ErrorMessage]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status_code = self.status_code

        error_code = self.error_code

        error_detail = self.error_detail

        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "statusCode": status_code,
                "errorCode": error_code,
                "errorDetail": error_detail,
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_message import ErrorMessage

        d = dict(src_dict)
        status_code = d.pop("statusCode")

        error_code = d.pop("errorCode")

        error_detail = d.pop("errorDetail")

        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = ErrorMessage.from_dict(errors_item_data)

            errors.append(errors_item)

        portal_error_response = cls(
            status_code=status_code,
            error_code=error_code,
            error_detail=error_detail,
            errors=errors,
        )

        portal_error_response.additional_properties = d
        return portal_error_response

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
