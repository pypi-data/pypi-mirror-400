from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.budget_period import BudgetPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectSettings")


@_attrs_define
class ProjectSettings:
    """
    Attributes:
        budget_amount (int): Total allowed cost for the budget period
        budget_period (BudgetPeriod): Time period associated with the budget amount
        enable_backup (bool | Unset): Enables the AWS Backup service for S3 Default: False.
        enable_sftp (bool | Unset): Enables access to files over SFTP Default: False.
        service_connections (list[str] | Unset): List of service connections to enable
        kms_arn (None | str | Unset): KMS Key ARN to encrypt S3 objects, if not provided, default bucket encryption will
            be used
        retention_policy_days (int | Unset): Days to keep deleted datasets before being permanently erased Default: 7.
        temporary_storage_lifetime_days (int | Unset): Days to keep temporary storage space (workflow executor cache)
            Default: 14.
        vpc_id (None | str | Unset): VPC that the compute environment will use Example: vpc-00000000000000000.
        batch_subnets (list[str] | None | Unset): List of subnets that the pipeline compute environment will use
            Example: ['subnet-00000000000000000'].
        sagemaker_subnets (list[str] | None | Unset): List of subnets that the sagemaker instances will use Example:
            ['subnet-00000000000000000'].
        workspace_subnets (list[str] | None | Unset): List of subnets that workspace instances will use Example:
            ['subnet-00000000000000000'].
        max_spot_vcpu (int | Unset): vCPU service quota limit for standard spot instances (pipelines) Default: 0.
        max_fpgavcpu (int | Unset): vCPU service quota limit for FPGA-enabled instances (pipelines) Default: 0.
        max_gpuvcpu (int | Unset): vCPU service quota limit for GPU-enabled spot instances (pipelines) Default: 0.
        enable_dragen (bool | Unset): Enables the DRAGEN compute environment (pipelines) Default: False.
        dragen_ami (None | str | Unset): AMI ID for the DRAGEN compute environment, if enabled (pipelines)
        max_workspaces_vcpu (int | Unset): vCPU service quota limit for standard instances (workspaces) Default: 0.
        max_workspaces_gpuvcpu (int | Unset): vCPU service quota limit for GPU-enabled instances (workspaces) Default:
            0.
        max_workspaces_per_user (int | Unset): Maximum number of workspaces per user (workspaces) Default: 0.
        is_discoverable (bool | None | Unset): Enables the project to be discoverable by other users Default: False.
        is_shareable (bool | None | Unset): Enables the project to be shared with other projects Default: False.
        has_pipelines_enabled (bool | None | Unset): (Read-only) Whether this project has pipelines enabled Default:
            False.
        has_workspaces_enabled (bool | None | Unset): (Read-only) Whether this project has workspaces enabled Default:
            False.
    """

    budget_amount: int
    budget_period: BudgetPeriod
    enable_backup: bool | Unset = False
    enable_sftp: bool | Unset = False
    service_connections: list[str] | Unset = UNSET
    kms_arn: None | str | Unset = UNSET
    retention_policy_days: int | Unset = 7
    temporary_storage_lifetime_days: int | Unset = 14
    vpc_id: None | str | Unset = UNSET
    batch_subnets: list[str] | None | Unset = UNSET
    sagemaker_subnets: list[str] | None | Unset = UNSET
    workspace_subnets: list[str] | None | Unset = UNSET
    max_spot_vcpu: int | Unset = 0
    max_fpgavcpu: int | Unset = 0
    max_gpuvcpu: int | Unset = 0
    enable_dragen: bool | Unset = False
    dragen_ami: None | str | Unset = UNSET
    max_workspaces_vcpu: int | Unset = 0
    max_workspaces_gpuvcpu: int | Unset = 0
    max_workspaces_per_user: int | Unset = 0
    is_discoverable: bool | None | Unset = False
    is_shareable: bool | None | Unset = False
    has_pipelines_enabled: bool | None | Unset = False
    has_workspaces_enabled: bool | None | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        budget_amount = self.budget_amount

        budget_period = self.budget_period.value

        enable_backup = self.enable_backup

        enable_sftp = self.enable_sftp

        service_connections: list[str] | Unset = UNSET
        if not isinstance(self.service_connections, Unset):
            service_connections = self.service_connections

        kms_arn: None | str | Unset
        if isinstance(self.kms_arn, Unset):
            kms_arn = UNSET
        else:
            kms_arn = self.kms_arn

        retention_policy_days = self.retention_policy_days

        temporary_storage_lifetime_days = self.temporary_storage_lifetime_days

        vpc_id: None | str | Unset
        if isinstance(self.vpc_id, Unset):
            vpc_id = UNSET
        else:
            vpc_id = self.vpc_id

        batch_subnets: list[str] | None | Unset
        if isinstance(self.batch_subnets, Unset):
            batch_subnets = UNSET
        elif isinstance(self.batch_subnets, list):
            batch_subnets = self.batch_subnets

        else:
            batch_subnets = self.batch_subnets

        sagemaker_subnets: list[str] | None | Unset
        if isinstance(self.sagemaker_subnets, Unset):
            sagemaker_subnets = UNSET
        elif isinstance(self.sagemaker_subnets, list):
            sagemaker_subnets = self.sagemaker_subnets

        else:
            sagemaker_subnets = self.sagemaker_subnets

        workspace_subnets: list[str] | None | Unset
        if isinstance(self.workspace_subnets, Unset):
            workspace_subnets = UNSET
        elif isinstance(self.workspace_subnets, list):
            workspace_subnets = self.workspace_subnets

        else:
            workspace_subnets = self.workspace_subnets

        max_spot_vcpu = self.max_spot_vcpu

        max_fpgavcpu = self.max_fpgavcpu

        max_gpuvcpu = self.max_gpuvcpu

        enable_dragen = self.enable_dragen

        dragen_ami: None | str | Unset
        if isinstance(self.dragen_ami, Unset):
            dragen_ami = UNSET
        else:
            dragen_ami = self.dragen_ami

        max_workspaces_vcpu = self.max_workspaces_vcpu

        max_workspaces_gpuvcpu = self.max_workspaces_gpuvcpu

        max_workspaces_per_user = self.max_workspaces_per_user

        is_discoverable: bool | None | Unset
        if isinstance(self.is_discoverable, Unset):
            is_discoverable = UNSET
        else:
            is_discoverable = self.is_discoverable

        is_shareable: bool | None | Unset
        if isinstance(self.is_shareable, Unset):
            is_shareable = UNSET
        else:
            is_shareable = self.is_shareable

        has_pipelines_enabled: bool | None | Unset
        if isinstance(self.has_pipelines_enabled, Unset):
            has_pipelines_enabled = UNSET
        else:
            has_pipelines_enabled = self.has_pipelines_enabled

        has_workspaces_enabled: bool | None | Unset
        if isinstance(self.has_workspaces_enabled, Unset):
            has_workspaces_enabled = UNSET
        else:
            has_workspaces_enabled = self.has_workspaces_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "budgetAmount": budget_amount,
                "budgetPeriod": budget_period,
            }
        )
        if enable_backup is not UNSET:
            field_dict["enableBackup"] = enable_backup
        if enable_sftp is not UNSET:
            field_dict["enableSftp"] = enable_sftp
        if service_connections is not UNSET:
            field_dict["serviceConnections"] = service_connections
        if kms_arn is not UNSET:
            field_dict["kmsArn"] = kms_arn
        if retention_policy_days is not UNSET:
            field_dict["retentionPolicyDays"] = retention_policy_days
        if temporary_storage_lifetime_days is not UNSET:
            field_dict["temporaryStorageLifetimeDays"] = temporary_storage_lifetime_days
        if vpc_id is not UNSET:
            field_dict["vpcId"] = vpc_id
        if batch_subnets is not UNSET:
            field_dict["batchSubnets"] = batch_subnets
        if sagemaker_subnets is not UNSET:
            field_dict["sagemakerSubnets"] = sagemaker_subnets
        if workspace_subnets is not UNSET:
            field_dict["workspaceSubnets"] = workspace_subnets
        if max_spot_vcpu is not UNSET:
            field_dict["maxSpotVCPU"] = max_spot_vcpu
        if max_fpgavcpu is not UNSET:
            field_dict["maxFPGAVCPU"] = max_fpgavcpu
        if max_gpuvcpu is not UNSET:
            field_dict["maxGPUVCPU"] = max_gpuvcpu
        if enable_dragen is not UNSET:
            field_dict["enableDragen"] = enable_dragen
        if dragen_ami is not UNSET:
            field_dict["dragenAmi"] = dragen_ami
        if max_workspaces_vcpu is not UNSET:
            field_dict["maxWorkspacesVCPU"] = max_workspaces_vcpu
        if max_workspaces_gpuvcpu is not UNSET:
            field_dict["maxWorkspacesGPUVCPU"] = max_workspaces_gpuvcpu
        if max_workspaces_per_user is not UNSET:
            field_dict["maxWorkspacesPerUser"] = max_workspaces_per_user
        if is_discoverable is not UNSET:
            field_dict["isDiscoverable"] = is_discoverable
        if is_shareable is not UNSET:
            field_dict["isShareable"] = is_shareable
        if has_pipelines_enabled is not UNSET:
            field_dict["hasPipelinesEnabled"] = has_pipelines_enabled
        if has_workspaces_enabled is not UNSET:
            field_dict["hasWorkspacesEnabled"] = has_workspaces_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        budget_amount = d.pop("budgetAmount")

        budget_period = BudgetPeriod(d.pop("budgetPeriod"))

        enable_backup = d.pop("enableBackup", UNSET)

        enable_sftp = d.pop("enableSftp", UNSET)

        service_connections = cast(list[str], d.pop("serviceConnections", UNSET))

        def _parse_kms_arn(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        kms_arn = _parse_kms_arn(d.pop("kmsArn", UNSET))

        retention_policy_days = d.pop("retentionPolicyDays", UNSET)

        temporary_storage_lifetime_days = d.pop("temporaryStorageLifetimeDays", UNSET)

        def _parse_vpc_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        vpc_id = _parse_vpc_id(d.pop("vpcId", UNSET))

        def _parse_batch_subnets(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                batch_subnets_type_0 = cast(list[str], data)

                return batch_subnets_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        batch_subnets = _parse_batch_subnets(d.pop("batchSubnets", UNSET))

        def _parse_sagemaker_subnets(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sagemaker_subnets_type_0 = cast(list[str], data)

                return sagemaker_subnets_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        sagemaker_subnets = _parse_sagemaker_subnets(d.pop("sagemakerSubnets", UNSET))

        def _parse_workspace_subnets(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                workspace_subnets_type_0 = cast(list[str], data)

                return workspace_subnets_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        workspace_subnets = _parse_workspace_subnets(d.pop("workspaceSubnets", UNSET))

        max_spot_vcpu = d.pop("maxSpotVCPU", UNSET)

        max_fpgavcpu = d.pop("maxFPGAVCPU", UNSET)

        max_gpuvcpu = d.pop("maxGPUVCPU", UNSET)

        enable_dragen = d.pop("enableDragen", UNSET)

        def _parse_dragen_ami(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dragen_ami = _parse_dragen_ami(d.pop("dragenAmi", UNSET))

        max_workspaces_vcpu = d.pop("maxWorkspacesVCPU", UNSET)

        max_workspaces_gpuvcpu = d.pop("maxWorkspacesGPUVCPU", UNSET)

        max_workspaces_per_user = d.pop("maxWorkspacesPerUser", UNSET)

        def _parse_is_discoverable(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_discoverable = _parse_is_discoverable(d.pop("isDiscoverable", UNSET))

        def _parse_is_shareable(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_shareable = _parse_is_shareable(d.pop("isShareable", UNSET))

        def _parse_has_pipelines_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        has_pipelines_enabled = _parse_has_pipelines_enabled(d.pop("hasPipelinesEnabled", UNSET))

        def _parse_has_workspaces_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        has_workspaces_enabled = _parse_has_workspaces_enabled(d.pop("hasWorkspacesEnabled", UNSET))

        project_settings = cls(
            budget_amount=budget_amount,
            budget_period=budget_period,
            enable_backup=enable_backup,
            enable_sftp=enable_sftp,
            service_connections=service_connections,
            kms_arn=kms_arn,
            retention_policy_days=retention_policy_days,
            temporary_storage_lifetime_days=temporary_storage_lifetime_days,
            vpc_id=vpc_id,
            batch_subnets=batch_subnets,
            sagemaker_subnets=sagemaker_subnets,
            workspace_subnets=workspace_subnets,
            max_spot_vcpu=max_spot_vcpu,
            max_fpgavcpu=max_fpgavcpu,
            max_gpuvcpu=max_gpuvcpu,
            enable_dragen=enable_dragen,
            dragen_ami=dragen_ami,
            max_workspaces_vcpu=max_workspaces_vcpu,
            max_workspaces_gpuvcpu=max_workspaces_gpuvcpu,
            max_workspaces_per_user=max_workspaces_per_user,
            is_discoverable=is_discoverable,
            is_shareable=is_shareable,
            has_pipelines_enabled=has_pipelines_enabled,
            has_workspaces_enabled=has_workspaces_enabled,
        )

        project_settings.additional_properties = d
        return project_settings

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
