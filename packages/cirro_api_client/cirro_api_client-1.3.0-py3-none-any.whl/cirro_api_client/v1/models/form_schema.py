from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.form_schema_form import FormSchemaForm
    from ..models.form_schema_ui import FormSchemaUi


T = TypeVar("T", bound="FormSchema")


@_attrs_define
class FormSchema:
    """
    Attributes:
        form (FormSchemaForm | Unset): JSONSchema representation of the parameters
        ui (FormSchemaUi | Unset): Describes how the form should be rendered, see rjsf
    """

    form: FormSchemaForm | Unset = UNSET
    ui: FormSchemaUi | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        form: dict[str, Any] | Unset = UNSET
        if not isinstance(self.form, Unset):
            form = self.form.to_dict()

        ui: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ui, Unset):
            ui = self.ui.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if form is not UNSET:
            field_dict["form"] = form
        if ui is not UNSET:
            field_dict["ui"] = ui

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.form_schema_form import FormSchemaForm
        from ..models.form_schema_ui import FormSchemaUi

        d = dict(src_dict)
        _form = d.pop("form", UNSET)
        form: FormSchemaForm | Unset
        if isinstance(_form, Unset):
            form = UNSET
        else:
            form = FormSchemaForm.from_dict(_form)

        _ui = d.pop("ui", UNSET)
        ui: FormSchemaUi | Unset
        if isinstance(_ui, Unset):
            ui = UNSET
        else:
            ui = FormSchemaUi.from_dict(_ui)

        form_schema = cls(
            form=form,
            ui=ui,
        )

        form_schema.additional_properties = d
        return form_schema

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
