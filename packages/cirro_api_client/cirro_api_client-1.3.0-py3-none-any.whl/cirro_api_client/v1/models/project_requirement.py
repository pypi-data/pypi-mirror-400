from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.governance_expiry_type import GovernanceExpiryType
from ..models.governance_scope import GovernanceScope
from ..models.governance_training_verification import GovernanceTrainingVerification
from ..models.governance_type import GovernanceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.governance_contact import GovernanceContact
    from ..models.governance_file import GovernanceFile


T = TypeVar("T", bound="ProjectRequirement")


@_attrs_define
class ProjectRequirement:
    """
    Attributes:
        id (str): The unique identifier for the requirement
        name (str): The name of the requirement
        description (str): A brief description of the requirement
        type_ (GovernanceType): The types of governance requirements that can be enforced
        path (str): S3 prefix where the main file for the requirement is saved
        supplemental_path (str): S3 prefix where supplemental files for the requirement are saved
        scope (GovernanceScope): The levels at which governance requirements can be enforced
        contacts (list[GovernanceContact]): The governance contacts assigned to the requirement.
        is_enacted (bool): Whether the requirement is past the enactment date
        is_project_configured (bool): A requirement is project configured if it was created by the tenant but needs a
            file uploaded by the project
        is_fulfilled (bool): Whether the current user has fulfilled the requirement for this project
        acceptance (GovernanceScope | None | Unset): Specifies the level at which it is satisfied
        enactment_date (datetime.datetime | None | Unset): The date of enactment for the requirement
        expiration_type (GovernanceExpiryType | Unset): The expiry conditions that can be applied to governance
            requirements.
        expiration_days_after_completion (int | None | Unset): The number of days for a relative to completion
            expiration
        expiration_date (datetime.datetime | None | Unset): The date of expiration for the requirement
        supplemental_docs (list[GovernanceFile] | None | Unset): Optional files with extra information, e.g. templates
            for documents, links, etc
        file (GovernanceFile | None | Unset):
        authorship (GovernanceScope | None | Unset): Who needs to supply the agreement document
        verification_method (GovernanceTrainingVerification | None | Unset): The value indicating how the completion of
            the training is verified.
        fulfillment_id (None | str | Unset): The id for the requirement fulfillment
        fulfillment_date (datetime.datetime | None | Unset): The date the requirement was fulfilled by the user
        fulfillment_file (None | str | Unset): The optional file uploaded to fulfill the requirement
        fulfillment_path (None | str | Unset): The path to the optional fulfillment file
        requires_user_fulfillment (bool | Unset): Whether this requirement requires the user to fulfill (it is active,
            requires fulfillment, and user has not fulfilled
    """

    id: str
    name: str
    description: str
    type_: GovernanceType
    path: str
    supplemental_path: str
    scope: GovernanceScope
    contacts: list[GovernanceContact]
    is_enacted: bool
    is_project_configured: bool
    is_fulfilled: bool
    acceptance: GovernanceScope | None | Unset = UNSET
    enactment_date: datetime.datetime | None | Unset = UNSET
    expiration_type: GovernanceExpiryType | Unset = UNSET
    expiration_days_after_completion: int | None | Unset = UNSET
    expiration_date: datetime.datetime | None | Unset = UNSET
    supplemental_docs: list[GovernanceFile] | None | Unset = UNSET
    file: GovernanceFile | None | Unset = UNSET
    authorship: GovernanceScope | None | Unset = UNSET
    verification_method: GovernanceTrainingVerification | None | Unset = UNSET
    fulfillment_id: None | str | Unset = UNSET
    fulfillment_date: datetime.datetime | None | Unset = UNSET
    fulfillment_file: None | str | Unset = UNSET
    fulfillment_path: None | str | Unset = UNSET
    requires_user_fulfillment: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.governance_file import GovernanceFile

        id = self.id

        name = self.name

        description = self.description

        type_ = self.type_.value

        path = self.path

        supplemental_path = self.supplemental_path

        scope = self.scope.value

        contacts = []
        for contacts_item_data in self.contacts:
            contacts_item = contacts_item_data.to_dict()
            contacts.append(contacts_item)

        is_enacted = self.is_enacted

        is_project_configured = self.is_project_configured

        is_fulfilled = self.is_fulfilled

        acceptance: None | str | Unset
        if isinstance(self.acceptance, Unset):
            acceptance = UNSET
        elif isinstance(self.acceptance, GovernanceScope):
            acceptance = self.acceptance.value
        else:
            acceptance = self.acceptance

        enactment_date: None | str | Unset
        if isinstance(self.enactment_date, Unset):
            enactment_date = UNSET
        elif isinstance(self.enactment_date, datetime.datetime):
            enactment_date = self.enactment_date.isoformat()
        else:
            enactment_date = self.enactment_date

        expiration_type: str | Unset = UNSET
        if not isinstance(self.expiration_type, Unset):
            expiration_type = self.expiration_type.value

        expiration_days_after_completion: int | None | Unset
        if isinstance(self.expiration_days_after_completion, Unset):
            expiration_days_after_completion = UNSET
        else:
            expiration_days_after_completion = self.expiration_days_after_completion

        expiration_date: None | str | Unset
        if isinstance(self.expiration_date, Unset):
            expiration_date = UNSET
        elif isinstance(self.expiration_date, datetime.datetime):
            expiration_date = self.expiration_date.isoformat()
        else:
            expiration_date = self.expiration_date

        supplemental_docs: list[dict[str, Any]] | None | Unset
        if isinstance(self.supplemental_docs, Unset):
            supplemental_docs = UNSET
        elif isinstance(self.supplemental_docs, list):
            supplemental_docs = []
            for supplemental_docs_type_0_item_data in self.supplemental_docs:
                supplemental_docs_type_0_item = supplemental_docs_type_0_item_data.to_dict()
                supplemental_docs.append(supplemental_docs_type_0_item)

        else:
            supplemental_docs = self.supplemental_docs

        file: dict[str, Any] | None | Unset
        if isinstance(self.file, Unset):
            file = UNSET
        elif isinstance(self.file, GovernanceFile):
            file = self.file.to_dict()
        else:
            file = self.file

        authorship: None | str | Unset
        if isinstance(self.authorship, Unset):
            authorship = UNSET
        elif isinstance(self.authorship, GovernanceScope):
            authorship = self.authorship.value
        else:
            authorship = self.authorship

        verification_method: None | str | Unset
        if isinstance(self.verification_method, Unset):
            verification_method = UNSET
        elif isinstance(self.verification_method, GovernanceTrainingVerification):
            verification_method = self.verification_method.value
        else:
            verification_method = self.verification_method

        fulfillment_id: None | str | Unset
        if isinstance(self.fulfillment_id, Unset):
            fulfillment_id = UNSET
        else:
            fulfillment_id = self.fulfillment_id

        fulfillment_date: None | str | Unset
        if isinstance(self.fulfillment_date, Unset):
            fulfillment_date = UNSET
        elif isinstance(self.fulfillment_date, datetime.datetime):
            fulfillment_date = self.fulfillment_date.isoformat()
        else:
            fulfillment_date = self.fulfillment_date

        fulfillment_file: None | str | Unset
        if isinstance(self.fulfillment_file, Unset):
            fulfillment_file = UNSET
        else:
            fulfillment_file = self.fulfillment_file

        fulfillment_path: None | str | Unset
        if isinstance(self.fulfillment_path, Unset):
            fulfillment_path = UNSET
        else:
            fulfillment_path = self.fulfillment_path

        requires_user_fulfillment = self.requires_user_fulfillment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "type": type_,
                "path": path,
                "supplementalPath": supplemental_path,
                "scope": scope,
                "contacts": contacts,
                "isEnacted": is_enacted,
                "isProjectConfigured": is_project_configured,
                "isFulfilled": is_fulfilled,
            }
        )
        if acceptance is not UNSET:
            field_dict["acceptance"] = acceptance
        if enactment_date is not UNSET:
            field_dict["enactmentDate"] = enactment_date
        if expiration_type is not UNSET:
            field_dict["expirationType"] = expiration_type
        if expiration_days_after_completion is not UNSET:
            field_dict["expirationDaysAfterCompletion"] = expiration_days_after_completion
        if expiration_date is not UNSET:
            field_dict["expirationDate"] = expiration_date
        if supplemental_docs is not UNSET:
            field_dict["supplementalDocs"] = supplemental_docs
        if file is not UNSET:
            field_dict["file"] = file
        if authorship is not UNSET:
            field_dict["authorship"] = authorship
        if verification_method is not UNSET:
            field_dict["verificationMethod"] = verification_method
        if fulfillment_id is not UNSET:
            field_dict["fulfillmentId"] = fulfillment_id
        if fulfillment_date is not UNSET:
            field_dict["fulfillmentDate"] = fulfillment_date
        if fulfillment_file is not UNSET:
            field_dict["fulfillmentFile"] = fulfillment_file
        if fulfillment_path is not UNSET:
            field_dict["fulfillmentPath"] = fulfillment_path
        if requires_user_fulfillment is not UNSET:
            field_dict["requiresUserFulfillment"] = requires_user_fulfillment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.governance_contact import GovernanceContact
        from ..models.governance_file import GovernanceFile

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        type_ = GovernanceType(d.pop("type"))

        path = d.pop("path")

        supplemental_path = d.pop("supplementalPath")

        scope = GovernanceScope(d.pop("scope"))

        contacts = []
        _contacts = d.pop("contacts")
        for contacts_item_data in _contacts:
            contacts_item = GovernanceContact.from_dict(contacts_item_data)

            contacts.append(contacts_item)

        is_enacted = d.pop("isEnacted")

        is_project_configured = d.pop("isProjectConfigured")

        is_fulfilled = d.pop("isFulfilled")

        def _parse_acceptance(data: object) -> GovernanceScope | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                acceptance_type_1 = GovernanceScope(data)

                return acceptance_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GovernanceScope | None | Unset, data)

        acceptance = _parse_acceptance(d.pop("acceptance", UNSET))

        def _parse_enactment_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                enactment_date_type_0 = isoparse(data)

                return enactment_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        enactment_date = _parse_enactment_date(d.pop("enactmentDate", UNSET))

        _expiration_type = d.pop("expirationType", UNSET)
        expiration_type: GovernanceExpiryType | Unset
        if isinstance(_expiration_type, Unset):
            expiration_type = UNSET
        else:
            expiration_type = GovernanceExpiryType(_expiration_type)

        def _parse_expiration_days_after_completion(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expiration_days_after_completion = _parse_expiration_days_after_completion(
            d.pop("expirationDaysAfterCompletion", UNSET)
        )

        def _parse_expiration_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expiration_date_type_0 = isoparse(data)

                return expiration_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expiration_date = _parse_expiration_date(d.pop("expirationDate", UNSET))

        def _parse_supplemental_docs(data: object) -> list[GovernanceFile] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                supplemental_docs_type_0 = []
                _supplemental_docs_type_0 = data
                for supplemental_docs_type_0_item_data in _supplemental_docs_type_0:
                    supplemental_docs_type_0_item = GovernanceFile.from_dict(supplemental_docs_type_0_item_data)

                    supplemental_docs_type_0.append(supplemental_docs_type_0_item)

                return supplemental_docs_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[GovernanceFile] | None | Unset, data)

        supplemental_docs = _parse_supplemental_docs(d.pop("supplementalDocs", UNSET))

        def _parse_file(data: object) -> GovernanceFile | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                file_type_1 = GovernanceFile.from_dict(data)

                return file_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GovernanceFile | None | Unset, data)

        file = _parse_file(d.pop("file", UNSET))

        def _parse_authorship(data: object) -> GovernanceScope | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                authorship_type_1 = GovernanceScope(data)

                return authorship_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GovernanceScope | None | Unset, data)

        authorship = _parse_authorship(d.pop("authorship", UNSET))

        def _parse_verification_method(data: object) -> GovernanceTrainingVerification | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                verification_method_type_1 = GovernanceTrainingVerification(data)

                return verification_method_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GovernanceTrainingVerification | None | Unset, data)

        verification_method = _parse_verification_method(d.pop("verificationMethod", UNSET))

        def _parse_fulfillment_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        fulfillment_id = _parse_fulfillment_id(d.pop("fulfillmentId", UNSET))

        def _parse_fulfillment_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                fulfillment_date_type_0 = isoparse(data)

                return fulfillment_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        fulfillment_date = _parse_fulfillment_date(d.pop("fulfillmentDate", UNSET))

        def _parse_fulfillment_file(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        fulfillment_file = _parse_fulfillment_file(d.pop("fulfillmentFile", UNSET))

        def _parse_fulfillment_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        fulfillment_path = _parse_fulfillment_path(d.pop("fulfillmentPath", UNSET))

        requires_user_fulfillment = d.pop("requiresUserFulfillment", UNSET)

        project_requirement = cls(
            id=id,
            name=name,
            description=description,
            type_=type_,
            path=path,
            supplemental_path=supplemental_path,
            scope=scope,
            contacts=contacts,
            is_enacted=is_enacted,
            is_project_configured=is_project_configured,
            is_fulfilled=is_fulfilled,
            acceptance=acceptance,
            enactment_date=enactment_date,
            expiration_type=expiration_type,
            expiration_days_after_completion=expiration_days_after_completion,
            expiration_date=expiration_date,
            supplemental_docs=supplemental_docs,
            file=file,
            authorship=authorship,
            verification_method=verification_method,
            fulfillment_id=fulfillment_id,
            fulfillment_date=fulfillment_date,
            fulfillment_file=fulfillment_file,
            fulfillment_path=fulfillment_path,
            requires_user_fulfillment=requires_user_fulfillment,
        )

        project_requirement.additional_properties = d
        return project_requirement

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
