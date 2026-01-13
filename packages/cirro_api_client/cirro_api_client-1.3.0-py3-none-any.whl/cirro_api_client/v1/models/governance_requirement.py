from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.governance_scope import GovernanceScope
from ..models.governance_training_verification import GovernanceTrainingVerification
from ..models.governance_type import GovernanceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.governance_expiry import GovernanceExpiry
    from ..models.governance_file import GovernanceFile
    from ..models.governance_requirement_project_file_map import GovernanceRequirementProjectFileMap


T = TypeVar("T", bound="GovernanceRequirement")


@_attrs_define
class GovernanceRequirement:
    """
    Attributes:
        id (str): The unique identifier for the requirement
        name (str):  The name of the requirement
        description (str): A brief description of the requirement
        type_ (GovernanceType): The types of governance requirements that can be enforced
        path (str): S3 prefix where files for the requirement are saved
        scope (GovernanceScope): The levels at which governance requirements can be enforced
        contact_ids (list[str]): The IDs of governance contacts assigned to the requirement.
        expiration (GovernanceExpiry):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        project_id (str | Unset): The project ID if the requirement is project scope
        acceptance (GovernanceScope | None | Unset): Specifies the level at which it is satisfied
        enactment_date (datetime.datetime | None | Unset): The date of enactment for a requirement
        supplemental_docs (list[GovernanceFile] | None | Unset): Optional files with extra information, e.g. templates
            for documents, links, etc
        file (GovernanceFile | None | Unset):
        authorship (GovernanceScope | None | Unset): Who needs to supply the agreement document
        project_file_map (GovernanceRequirementProjectFileMap | None | Unset): Files supplied by each project when
            authorship is project
        verification_method (GovernanceTrainingVerification | None | Unset): The value indicating how the completion of
            the training is verified.
    """

    id: str
    name: str
    description: str
    type_: GovernanceType
    path: str
    scope: GovernanceScope
    contact_ids: list[str]
    expiration: GovernanceExpiry
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    project_id: str | Unset = UNSET
    acceptance: GovernanceScope | None | Unset = UNSET
    enactment_date: datetime.datetime | None | Unset = UNSET
    supplemental_docs: list[GovernanceFile] | None | Unset = UNSET
    file: GovernanceFile | None | Unset = UNSET
    authorship: GovernanceScope | None | Unset = UNSET
    project_file_map: GovernanceRequirementProjectFileMap | None | Unset = UNSET
    verification_method: GovernanceTrainingVerification | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.governance_file import GovernanceFile
        from ..models.governance_requirement_project_file_map import GovernanceRequirementProjectFileMap

        id = self.id

        name = self.name

        description = self.description

        type_ = self.type_.value

        path = self.path

        scope = self.scope.value

        contact_ids = self.contact_ids

        expiration = self.expiration.to_dict()

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        project_id = self.project_id

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

        project_file_map: dict[str, Any] | None | Unset
        if isinstance(self.project_file_map, Unset):
            project_file_map = UNSET
        elif isinstance(self.project_file_map, GovernanceRequirementProjectFileMap):
            project_file_map = self.project_file_map.to_dict()
        else:
            project_file_map = self.project_file_map

        verification_method: None | str | Unset
        if isinstance(self.verification_method, Unset):
            verification_method = UNSET
        elif isinstance(self.verification_method, GovernanceTrainingVerification):
            verification_method = self.verification_method.value
        else:
            verification_method = self.verification_method

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "type": type_,
                "path": path,
                "scope": scope,
                "contactIds": contact_ids,
                "expiration": expiration,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if acceptance is not UNSET:
            field_dict["acceptance"] = acceptance
        if enactment_date is not UNSET:
            field_dict["enactmentDate"] = enactment_date
        if supplemental_docs is not UNSET:
            field_dict["supplementalDocs"] = supplemental_docs
        if file is not UNSET:
            field_dict["file"] = file
        if authorship is not UNSET:
            field_dict["authorship"] = authorship
        if project_file_map is not UNSET:
            field_dict["projectFileMap"] = project_file_map
        if verification_method is not UNSET:
            field_dict["verificationMethod"] = verification_method

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.governance_expiry import GovernanceExpiry
        from ..models.governance_file import GovernanceFile
        from ..models.governance_requirement_project_file_map import GovernanceRequirementProjectFileMap

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        type_ = GovernanceType(d.pop("type"))

        path = d.pop("path")

        scope = GovernanceScope(d.pop("scope"))

        contact_ids = cast(list[str], d.pop("contactIds"))

        expiration = GovernanceExpiry.from_dict(d.pop("expiration"))

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        project_id = d.pop("projectId", UNSET)

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

        def _parse_project_file_map(data: object) -> GovernanceRequirementProjectFileMap | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                project_file_map_type_0 = GovernanceRequirementProjectFileMap.from_dict(data)

                return project_file_map_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GovernanceRequirementProjectFileMap | None | Unset, data)

        project_file_map = _parse_project_file_map(d.pop("projectFileMap", UNSET))

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

        governance_requirement = cls(
            id=id,
            name=name,
            description=description,
            type_=type_,
            path=path,
            scope=scope,
            contact_ids=contact_ids,
            expiration=expiration,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            project_id=project_id,
            acceptance=acceptance,
            enactment_date=enactment_date,
            supplemental_docs=supplemental_docs,
            file=file,
            authorship=authorship,
            project_file_map=project_file_map,
            verification_method=verification_method,
        )

        governance_requirement.additional_properties = d
        return governance_requirement

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
