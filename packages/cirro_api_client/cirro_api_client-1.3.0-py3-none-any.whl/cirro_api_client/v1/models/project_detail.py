from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cloud_account import CloudAccount
    from ..models.contact import Contact
    from ..models.project_settings import ProjectSettings
    from ..models.tag import Tag


T = TypeVar("T", bound="ProjectDetail")


@_attrs_define
class ProjectDetail:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        billing_account_id (str):
        contacts (list[Contact]):
        organization (str):
        status (Status):
        settings (ProjectSettings):
        account (CloudAccount):
        status_message (str):
        tags (list[Tag]):
        classification_ids (list[str]):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        deployed_at (datetime.datetime | None | Unset):
    """

    id: str
    name: str
    description: str
    billing_account_id: str
    contacts: list[Contact]
    organization: str
    status: Status
    settings: ProjectSettings
    account: CloudAccount
    status_message: str
    tags: list[Tag]
    classification_ids: list[str]
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deployed_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        billing_account_id = self.billing_account_id

        contacts = []
        for contacts_item_data in self.contacts:
            contacts_item = contacts_item_data.to_dict()
            contacts.append(contacts_item)

        organization = self.organization

        status = self.status.value

        settings = self.settings.to_dict()

        account = self.account.to_dict()

        status_message = self.status_message

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        classification_ids = self.classification_ids

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        deployed_at: None | str | Unset
        if isinstance(self.deployed_at, Unset):
            deployed_at = UNSET
        elif isinstance(self.deployed_at, datetime.datetime):
            deployed_at = self.deployed_at.isoformat()
        else:
            deployed_at = self.deployed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "billingAccountId": billing_account_id,
                "contacts": contacts,
                "organization": organization,
                "status": status,
                "settings": settings,
                "account": account,
                "statusMessage": status_message,
                "tags": tags,
                "classificationIds": classification_ids,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if deployed_at is not UNSET:
            field_dict["deployedAt"] = deployed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cloud_account import CloudAccount
        from ..models.contact import Contact
        from ..models.project_settings import ProjectSettings
        from ..models.tag import Tag

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        billing_account_id = d.pop("billingAccountId")

        contacts = []
        _contacts = d.pop("contacts")
        for contacts_item_data in _contacts:
            contacts_item = Contact.from_dict(contacts_item_data)

            contacts.append(contacts_item)

        organization = d.pop("organization")

        status = Status(d.pop("status"))

        settings = ProjectSettings.from_dict(d.pop("settings"))

        account = CloudAccount.from_dict(d.pop("account"))

        status_message = d.pop("statusMessage")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        classification_ids = cast(list[str], d.pop("classificationIds"))

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_deployed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deployed_at_type_0 = isoparse(data)

                return deployed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        deployed_at = _parse_deployed_at(d.pop("deployedAt", UNSET))

        project_detail = cls(
            id=id,
            name=name,
            description=description,
            billing_account_id=billing_account_id,
            contacts=contacts,
            organization=organization,
            status=status,
            settings=settings,
            account=account,
            status_message=status_message,
            tags=tags,
            classification_ids=classification_ids,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            deployed_at=deployed_at,
        )

        project_detail.additional_properties = d
        return project_detail

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
