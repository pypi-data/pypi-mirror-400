from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact import Artifact
    from ..models.dataset_viz import DatasetViz
    from ..models.file_entry import FileEntry
    from ..models.table import Table


T = TypeVar("T", bound="DatasetAssetsManifest")


@_attrs_define
class DatasetAssetsManifest:
    """
    Attributes:
        domain (str | Unset): Base URL for files Example: s3://project-1a1a/datasets/1a1a.
        files (list[FileEntry] | Unset): List of files in the dataset, including metadata
        total_files (int | Unset): Total number of files in the dataset, used for pagination
        viz (list[DatasetViz] | Unset): List of viz to render for the dataset
        tables (list[Table] | Unset): List of web optimized tables for the dataset
        artifacts (list[Artifact] | Unset): Artifacts associated with the dataset
    """

    domain: str | Unset = UNSET
    files: list[FileEntry] | Unset = UNSET
    total_files: int | Unset = UNSET
    viz: list[DatasetViz] | Unset = UNSET
    tables: list[Table] | Unset = UNSET
    artifacts: list[Artifact] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain = self.domain

        files: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.files, Unset):
            files = []
            for files_item_data in self.files:
                files_item = files_item_data.to_dict()
                files.append(files_item)

        total_files = self.total_files

        viz: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.viz, Unset):
            viz = []
            for viz_item_data in self.viz:
                viz_item = viz_item_data.to_dict()
                viz.append(viz_item)

        tables: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tables, Unset):
            tables = []
            for tables_item_data in self.tables:
                tables_item = tables_item_data.to_dict()
                tables.append(tables_item)

        artifacts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.artifacts, Unset):
            artifacts = []
            for artifacts_item_data in self.artifacts:
                artifacts_item = artifacts_item_data.to_dict()
                artifacts.append(artifacts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if domain is not UNSET:
            field_dict["domain"] = domain
        if files is not UNSET:
            field_dict["files"] = files
        if total_files is not UNSET:
            field_dict["totalFiles"] = total_files
        if viz is not UNSET:
            field_dict["viz"] = viz
        if tables is not UNSET:
            field_dict["tables"] = tables
        if artifacts is not UNSET:
            field_dict["artifacts"] = artifacts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artifact import Artifact
        from ..models.dataset_viz import DatasetViz
        from ..models.file_entry import FileEntry
        from ..models.table import Table

        d = dict(src_dict)
        domain = d.pop("domain", UNSET)

        _files = d.pop("files", UNSET)
        files: list[FileEntry] | Unset = UNSET
        if _files is not UNSET:
            files = []
            for files_item_data in _files:
                files_item = FileEntry.from_dict(files_item_data)

                files.append(files_item)

        total_files = d.pop("totalFiles", UNSET)

        _viz = d.pop("viz", UNSET)
        viz: list[DatasetViz] | Unset = UNSET
        if _viz is not UNSET:
            viz = []
            for viz_item_data in _viz:
                viz_item = DatasetViz.from_dict(viz_item_data)

                viz.append(viz_item)

        _tables = d.pop("tables", UNSET)
        tables: list[Table] | Unset = UNSET
        if _tables is not UNSET:
            tables = []
            for tables_item_data in _tables:
                tables_item = Table.from_dict(tables_item_data)

                tables.append(tables_item)

        _artifacts = d.pop("artifacts", UNSET)
        artifacts: list[Artifact] | Unset = UNSET
        if _artifacts is not UNSET:
            artifacts = []
            for artifacts_item_data in _artifacts:
                artifacts_item = Artifact.from_dict(artifacts_item_data)

                artifacts.append(artifacts_item)

        dataset_assets_manifest = cls(
            domain=domain,
            files=files,
            total_files=total_files,
            viz=viz,
            tables=tables,
            artifacts=artifacts,
        )

        dataset_assets_manifest.additional_properties = d
        return dataset_assets_manifest

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
