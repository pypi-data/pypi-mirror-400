from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.executor import Executor
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_pipeline_settings import CustomPipelineSettings
    from ..models.file_mapping_rule import FileMappingRule
    from ..models.pipeline_code import PipelineCode


T = TypeVar("T", bound="CustomProcessInput")


@_attrs_define
class CustomProcessInput:
    """
    Attributes:
        id (str): Unique ID of the Process Example: process-hutch-magic_flute-1_0.
        name (str): Friendly name for the process Example: MAGeCK Flute.
        description (str): Description of the process Example: MAGeCK Flute enables accurate identification of essential
            genes with their related biological functions.
        executor (Executor): How the workflow is executed
        child_process_ids (list[str]): IDs of pipelines that can be run downstream
        parent_process_ids (list[str]): IDs of processes that can run this pipeline
        linked_project_ids (list[str]): Projects that can run this process
        data_type (None | str | Unset): Name of the data type this pipeline produces (if it is not defined, use the
            name)
        category (str | Unset): Category of the process Example: Microbial Analysis.
        documentation_url (None | str | Unset): Link to process documentation Example:
            https://docs.cirro.bio/pipelines/catalog_targeted_sequencing/#crispr-screen-analysis.
        file_requirements_message (None | str | Unset): Description of the files to be uploaded (optional)
        pipeline_code (None | PipelineCode | Unset):
        is_tenant_wide (bool | Unset): Whether the process is shared with the tenant
        allow_multiple_sources (bool | Unset): Whether the pipeline is allowed to have multiple dataset sources
        uses_sample_sheet (bool | Unset): Whether the pipeline uses the Cirro-provided sample sheet
        custom_settings (CustomPipelineSettings | None | Unset):
        file_mapping_rules (list[FileMappingRule] | None | Unset):
    """

    id: str
    name: str
    description: str
    executor: Executor
    child_process_ids: list[str]
    parent_process_ids: list[str]
    linked_project_ids: list[str]
    data_type: None | str | Unset = UNSET
    category: str | Unset = UNSET
    documentation_url: None | str | Unset = UNSET
    file_requirements_message: None | str | Unset = UNSET
    pipeline_code: None | PipelineCode | Unset = UNSET
    is_tenant_wide: bool | Unset = UNSET
    allow_multiple_sources: bool | Unset = UNSET
    uses_sample_sheet: bool | Unset = UNSET
    custom_settings: CustomPipelineSettings | None | Unset = UNSET
    file_mapping_rules: list[FileMappingRule] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.custom_pipeline_settings import CustomPipelineSettings
        from ..models.pipeline_code import PipelineCode

        id = self.id

        name = self.name

        description = self.description

        executor = self.executor.value

        child_process_ids = self.child_process_ids

        parent_process_ids = self.parent_process_ids

        linked_project_ids = self.linked_project_ids

        data_type: None | str | Unset
        if isinstance(self.data_type, Unset):
            data_type = UNSET
        else:
            data_type = self.data_type

        category = self.category

        documentation_url: None | str | Unset
        if isinstance(self.documentation_url, Unset):
            documentation_url = UNSET
        else:
            documentation_url = self.documentation_url

        file_requirements_message: None | str | Unset
        if isinstance(self.file_requirements_message, Unset):
            file_requirements_message = UNSET
        else:
            file_requirements_message = self.file_requirements_message

        pipeline_code: dict[str, Any] | None | Unset
        if isinstance(self.pipeline_code, Unset):
            pipeline_code = UNSET
        elif isinstance(self.pipeline_code, PipelineCode):
            pipeline_code = self.pipeline_code.to_dict()
        else:
            pipeline_code = self.pipeline_code

        is_tenant_wide = self.is_tenant_wide

        allow_multiple_sources = self.allow_multiple_sources

        uses_sample_sheet = self.uses_sample_sheet

        custom_settings: dict[str, Any] | None | Unset
        if isinstance(self.custom_settings, Unset):
            custom_settings = UNSET
        elif isinstance(self.custom_settings, CustomPipelineSettings):
            custom_settings = self.custom_settings.to_dict()
        else:
            custom_settings = self.custom_settings

        file_mapping_rules: list[dict[str, Any]] | None | Unset
        if isinstance(self.file_mapping_rules, Unset):
            file_mapping_rules = UNSET
        elif isinstance(self.file_mapping_rules, list):
            file_mapping_rules = []
            for file_mapping_rules_type_0_item_data in self.file_mapping_rules:
                file_mapping_rules_type_0_item = file_mapping_rules_type_0_item_data.to_dict()
                file_mapping_rules.append(file_mapping_rules_type_0_item)

        else:
            file_mapping_rules = self.file_mapping_rules

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "executor": executor,
                "childProcessIds": child_process_ids,
                "parentProcessIds": parent_process_ids,
                "linkedProjectIds": linked_project_ids,
            }
        )
        if data_type is not UNSET:
            field_dict["dataType"] = data_type
        if category is not UNSET:
            field_dict["category"] = category
        if documentation_url is not UNSET:
            field_dict["documentationUrl"] = documentation_url
        if file_requirements_message is not UNSET:
            field_dict["fileRequirementsMessage"] = file_requirements_message
        if pipeline_code is not UNSET:
            field_dict["pipelineCode"] = pipeline_code
        if is_tenant_wide is not UNSET:
            field_dict["isTenantWide"] = is_tenant_wide
        if allow_multiple_sources is not UNSET:
            field_dict["allowMultipleSources"] = allow_multiple_sources
        if uses_sample_sheet is not UNSET:
            field_dict["usesSampleSheet"] = uses_sample_sheet
        if custom_settings is not UNSET:
            field_dict["customSettings"] = custom_settings
        if file_mapping_rules is not UNSET:
            field_dict["fileMappingRules"] = file_mapping_rules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_pipeline_settings import CustomPipelineSettings
        from ..models.file_mapping_rule import FileMappingRule
        from ..models.pipeline_code import PipelineCode

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        executor = Executor(d.pop("executor"))

        child_process_ids = cast(list[str], d.pop("childProcessIds"))

        parent_process_ids = cast(list[str], d.pop("parentProcessIds"))

        linked_project_ids = cast(list[str], d.pop("linkedProjectIds"))

        def _parse_data_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        data_type = _parse_data_type(d.pop("dataType", UNSET))

        category = d.pop("category", UNSET)

        def _parse_documentation_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        documentation_url = _parse_documentation_url(d.pop("documentationUrl", UNSET))

        def _parse_file_requirements_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_requirements_message = _parse_file_requirements_message(d.pop("fileRequirementsMessage", UNSET))

        def _parse_pipeline_code(data: object) -> None | PipelineCode | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pipeline_code_type_1 = PipelineCode.from_dict(data)

                return pipeline_code_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PipelineCode | Unset, data)

        pipeline_code = _parse_pipeline_code(d.pop("pipelineCode", UNSET))

        is_tenant_wide = d.pop("isTenantWide", UNSET)

        allow_multiple_sources = d.pop("allowMultipleSources", UNSET)

        uses_sample_sheet = d.pop("usesSampleSheet", UNSET)

        def _parse_custom_settings(data: object) -> CustomPipelineSettings | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_settings_type_1 = CustomPipelineSettings.from_dict(data)

                return custom_settings_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomPipelineSettings | None | Unset, data)

        custom_settings = _parse_custom_settings(d.pop("customSettings", UNSET))

        def _parse_file_mapping_rules(data: object) -> list[FileMappingRule] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                file_mapping_rules_type_0 = []
                _file_mapping_rules_type_0 = data
                for file_mapping_rules_type_0_item_data in _file_mapping_rules_type_0:
                    file_mapping_rules_type_0_item = FileMappingRule.from_dict(file_mapping_rules_type_0_item_data)

                    file_mapping_rules_type_0.append(file_mapping_rules_type_0_item)

                return file_mapping_rules_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[FileMappingRule] | None | Unset, data)

        file_mapping_rules = _parse_file_mapping_rules(d.pop("fileMappingRules", UNSET))

        custom_process_input = cls(
            id=id,
            name=name,
            description=description,
            executor=executor,
            child_process_ids=child_process_ids,
            parent_process_ids=parent_process_ids,
            linked_project_ids=linked_project_ids,
            data_type=data_type,
            category=category,
            documentation_url=documentation_url,
            file_requirements_message=file_requirements_message,
            pipeline_code=pipeline_code,
            is_tenant_wide=is_tenant_wide,
            allow_multiple_sources=allow_multiple_sources,
            uses_sample_sheet=uses_sample_sheet,
            custom_settings=custom_settings,
            file_mapping_rules=file_mapping_rules,
        )

        custom_process_input.additional_properties = d
        return custom_process_input

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
