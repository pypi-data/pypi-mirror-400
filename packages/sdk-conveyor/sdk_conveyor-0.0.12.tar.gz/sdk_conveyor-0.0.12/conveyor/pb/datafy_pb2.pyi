import datetime

import conveyor.pb.application_runs_pb2 as _application_runs_pb2
from conveyor.pb.buf.validate import validate_pb2 as _validate_pb2
import conveyor.pb.common_pb2 as _common_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.api import httpbody_pb2 as _httpbody_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from conveyor.pb.protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
import conveyor.pb.tag_pb2 as _tag_pb2
from conveyor.pb.tagger import tagger_pb2 as _tagger_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Stack(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Stack_Unknown: _ClassVar[Stack]
    Stack_Python: _ClassVar[Stack]
    Stack_Dbt: _ClassVar[Stack]
    Stack_Spark: _ClassVar[Stack]
    stack_Scala: _ClassVar[Stack]

class TenantState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Initialized: _ClassVar[TenantState]
    CloudDetailsProvided: _ClassVar[TenantState]
    Installed: _ClassVar[TenantState]

class SparkMetricCalculationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unknown: _ClassVar[SparkMetricCalculationState]
    Started: _ClassVar[SparkMetricCalculationState]
    NotProcessed: _ClassVar[SparkMetricCalculationState]
    Succeeded: _ClassVar[SparkMetricCalculationState]
    Failed: _ClassVar[SparkMetricCalculationState]

class LinkIcon(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ICON_NONE: _ClassVar[LinkIcon]
    ICON_AWS: _ClassVar[LinkIcon]
    ICON_AWS_ATHENA: _ClassVar[LinkIcon]
    ICON_AWS_GLUE: _ClassVar[LinkIcon]
    ICON_AWS_REDSHIFT: _ClassVar[LinkIcon]
    ICON_AWS_LAKE_FORMATION: _ClassVar[LinkIcon]
    ICON_AZURE: _ClassVar[LinkIcon]
    ICON_GRAFANA: _ClassVar[LinkIcon]
    ICON_SNOWFLAKE: _ClassVar[LinkIcon]
    ICON_DATAHUB: _ClassVar[LinkIcon]
    ICON_DATABRICKS: _ClassVar[LinkIcon]
    ICON_JIRA: _ClassVar[LinkIcon]
    ICON_DATA_PRODUCT_PORTAL: _ClassVar[LinkIcon]
    ICON_TRINO: _ClassVar[LinkIcon]
    ICON_AWS_CLOUDWATCH: _ClassVar[LinkIcon]
    ICON_API: _ClassVar[LinkIcon]
    ICON_DOLLAR: _ClassVar[LinkIcon]
    ICON_EURO: _ClassVar[LinkIcon]

class ProjectRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Admin: _ClassVar[ProjectRole]
    Contributor: _ClassVar[ProjectRole]

class AirflowVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AirflowVersion_V1: _ClassVar[AirflowVersion]
    AirflowVersion_V2: _ClassVar[AirflowVersion]
    AirflowVersion_V3: _ClassVar[AirflowVersion]

class AirflowInstanceLifecycle(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SPOT: _ClassVar[AirflowInstanceLifecycle]
    ON_DEMAND: _ClassVar[AirflowInstanceLifecycle]

class EnvironmentRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EnvironmentAdmin: _ClassVar[EnvironmentRole]
    EnvironmentContributor: _ClassVar[EnvironmentRole]
    EnvironmentOperator: _ClassVar[EnvironmentRole]

class PipelineState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PipelineState_All: _ClassVar[PipelineState]
    PipelineState_WithFailures: _ClassVar[PipelineState]

class PipelineExecutionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PipelineExecutionStatus_Unknown: _ClassVar[PipelineExecutionStatus]
    PipelineExecutionStatus_Running: _ClassVar[PipelineExecutionStatus]
    PipelineExecutionStatus_Success: _ClassVar[PipelineExecutionStatus]
    PipelineExecutionStatus_Failed: _ClassVar[PipelineExecutionStatus]
    PipelineExecutionStatus_Queued: _ClassVar[PipelineExecutionStatus]

class TeamMemberType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TeamMember: _ClassVar[TeamMemberType]
    TeamAdmin: _ClassVar[TeamMemberType]
Stack_Unknown: Stack
Stack_Python: Stack
Stack_Dbt: Stack
Stack_Spark: Stack
stack_Scala: Stack
Initialized: TenantState
CloudDetailsProvided: TenantState
Installed: TenantState
Unknown: SparkMetricCalculationState
Started: SparkMetricCalculationState
NotProcessed: SparkMetricCalculationState
Succeeded: SparkMetricCalculationState
Failed: SparkMetricCalculationState
ICON_NONE: LinkIcon
ICON_AWS: LinkIcon
ICON_AWS_ATHENA: LinkIcon
ICON_AWS_GLUE: LinkIcon
ICON_AWS_REDSHIFT: LinkIcon
ICON_AWS_LAKE_FORMATION: LinkIcon
ICON_AZURE: LinkIcon
ICON_GRAFANA: LinkIcon
ICON_SNOWFLAKE: LinkIcon
ICON_DATAHUB: LinkIcon
ICON_DATABRICKS: LinkIcon
ICON_JIRA: LinkIcon
ICON_DATA_PRODUCT_PORTAL: LinkIcon
ICON_TRINO: LinkIcon
ICON_AWS_CLOUDWATCH: LinkIcon
ICON_API: LinkIcon
ICON_DOLLAR: LinkIcon
ICON_EURO: LinkIcon
Admin: ProjectRole
Contributor: ProjectRole
AirflowVersion_V1: AirflowVersion
AirflowVersion_V2: AirflowVersion
AirflowVersion_V3: AirflowVersion
SPOT: AirflowInstanceLifecycle
ON_DEMAND: AirflowInstanceLifecycle
EnvironmentAdmin: EnvironmentRole
EnvironmentContributor: EnvironmentRole
EnvironmentOperator: EnvironmentRole
PipelineState_All: PipelineState
PipelineState_WithFailures: PipelineState
PipelineExecutionStatus_Unknown: PipelineExecutionStatus
PipelineExecutionStatus_Running: PipelineExecutionStatus
PipelineExecutionStatus_Success: PipelineExecutionStatus
PipelineExecutionStatus_Failed: PipelineExecutionStatus
PipelineExecutionStatus_Queued: PipelineExecutionStatus
TeamMember: TeamMemberType
TeamAdmin: TeamMemberType

class Deployment(_message.Message):
    __slots__ = ("id", "build_id", "deployed_on", "environment_id", "environment_name", "project_id", "project_name", "git_hash", "git_hash_repo_link", "is_active", "created_by")
    ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    DEPLOYED_ON_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_REPO_LINK_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    id: str
    build_id: str
    deployed_on: _timestamp_pb2.Timestamp
    environment_id: str
    environment_name: str
    project_id: str
    project_name: str
    git_hash: str
    git_hash_repo_link: str
    is_active: bool
    created_by: str
    def __init__(self, id: _Optional[str] = ..., build_id: _Optional[str] = ..., deployed_on: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., git_hash: _Optional[str] = ..., git_hash_repo_link: _Optional[str] = ..., is_active: bool = ..., created_by: _Optional[str] = ...) -> None: ...

class InspectPodDetailsRequest(_message.Message):
    __slots__ = ("cluster_id", "environment_name", "label_selector", "pod_name", "field_selector")
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    LABEL_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    FIELD_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    environment_name: str
    label_selector: Selector
    pod_name: str
    field_selector: Selector
    def __init__(self, cluster_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., label_selector: _Optional[_Union[Selector, _Mapping]] = ..., pod_name: _Optional[str] = ..., field_selector: _Optional[_Union[Selector, _Mapping]] = ...) -> None: ...

class Selector(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class InspectPodDetailsResponse(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class AddUserToAdminRoleForTenantRequest(_message.Message):
    __slots__ = ("user", "tenantId")
    USER_FIELD_NUMBER: _ClassVar[int]
    TENANTID_FIELD_NUMBER: _ClassVar[int]
    user: str
    tenantId: str
    def __init__(self, user: _Optional[str] = ..., tenantId: _Optional[str] = ...) -> None: ...

class AddUserToAdminRoleForTenantResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveUserFromAdminRoleForTenantRequest(_message.Message):
    __slots__ = ("user", "tenantId")
    USER_FIELD_NUMBER: _ClassVar[int]
    TENANTID_FIELD_NUMBER: _ClassVar[int]
    user: str
    tenantId: str
    def __init__(self, user: _Optional[str] = ..., tenantId: _Optional[str] = ...) -> None: ...

class RemoveUserFromAdminRoleForTenantResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListUsersForTenantRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListUsersForTenantResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, users: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class ListClustersForTenantRequest(_message.Message):
    __slots__ = ("tenantId",)
    TENANTID_FIELD_NUMBER: _ClassVar[int]
    tenantId: str
    def __init__(self, tenantId: _Optional[str] = ...) -> None: ...

class UpdateClusterForTenantRequest(_message.Message):
    __slots__ = ("id", "name", "is_default", "aws", "tenantId")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    AWS_FIELD_NUMBER: _ClassVar[int]
    TENANTID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    is_default: bool
    aws: AwsClusterDetails
    tenantId: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., is_default: bool = ..., aws: _Optional[_Union[AwsClusterDetails, _Mapping]] = ..., tenantId: _Optional[str] = ...) -> None: ...

class DeleteTenantRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteTenantResponse(_message.Message):
    __slots__ = ("warnings",)
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, warnings: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateTenantRequest(_message.Message):
    __slots__ = ("id", "name", "cloud_details", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    cloud_details: AwsCloudDetails
    state: TenantState
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., cloud_details: _Optional[_Union[AwsCloudDetails, _Mapping]] = ..., state: _Optional[_Union[TenantState, str]] = ...) -> None: ...

class InitializeTenantWithUserResponse(_message.Message):
    __slots__ = ("id", "created_at", "name", "cloud", "email")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    name: str
    cloud: _common_pb2.Cloud
    email: str
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., email: _Optional[str] = ...) -> None: ...

class InitializeTenantWithUserRequest(_message.Message):
    __slots__ = ("name", "email", "cloud", "first_name", "last_name")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    cloud: _common_pb2.Cloud
    first_name: str
    last_name: str
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ...) -> None: ...

class CheckCanAWSRoleBeAssumedRequest(_message.Message):
    __slots__ = ("role_arn",)
    ROLE_ARN_FIELD_NUMBER: _ClassVar[int]
    role_arn: str
    def __init__(self, role_arn: _Optional[str] = ...) -> None: ...

class CheckCanAWSRoleBeAssumedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTenantRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class TenantVersion(_message.Message):
    __slots__ = ("name", "version", "cloudformation_template_version", "cluster_name")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CLOUDFORMATION_TEMPLATE_VERSION_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    cloudformation_template_version: str
    cluster_name: str
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., cloudformation_template_version: _Optional[str] = ..., cluster_name: _Optional[str] = ...) -> None: ...

class GetTenantVersionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTenantVersionsResponse(_message.Message):
    __slots__ = ("tenant_versions",)
    TENANT_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    tenant_versions: _containers.RepeatedCompositeFieldContainer[TenantVersion]
    def __init__(self, tenant_versions: _Optional[_Iterable[_Union[TenantVersion, _Mapping]]] = ...) -> None: ...

class PendulumUpgradeCheckDataPlaneRequest(_message.Message):
    __slots__ = ("tenant_name", "cluster_name", "environment_name")
    TENANT_NAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    tenant_name: str
    cluster_name: str
    environment_name: str
    def __init__(self, tenant_name: _Optional[str] = ..., cluster_name: _Optional[str] = ..., environment_name: _Optional[str] = ...) -> None: ...

class PendulumUpgradeCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PendulumUpgradeCheck(_message.Message):
    __slots__ = ("tenant_name", "cluster_name", "environment_name", "failing_dag_codes", "error")
    TENANT_NAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    FAILING_DAG_CODES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    tenant_name: str
    cluster_name: str
    environment_name: str
    failing_dag_codes: _containers.RepeatedScalarFieldContainer[str]
    error: str
    def __init__(self, tenant_name: _Optional[str] = ..., cluster_name: _Optional[str] = ..., environment_name: _Optional[str] = ..., failing_dag_codes: _Optional[_Iterable[str]] = ..., error: _Optional[str] = ...) -> None: ...

class PendulumUpgradeCheckResponse(_message.Message):
    __slots__ = ("pendulum_upgrade_checks",)
    PENDULUM_UPGRADE_CHECKS_FIELD_NUMBER: _ClassVar[int]
    pendulum_upgrade_checks: _containers.RepeatedCompositeFieldContainer[PendulumUpgradeCheck]
    def __init__(self, pendulum_upgrade_checks: _Optional[_Iterable[_Union[PendulumUpgradeCheck, _Mapping]]] = ...) -> None: ...

class UpdateTenantIntegrationRequest(_message.Message):
    __slots__ = ("gitpod_enabled", "gitpod_url", "codespaces_enabled", "notebooks_enabled", "ides_enabled", "project_creation_enabled", "project_creation_message", "environment_creation_enabled", "environment_creation_message", "limit_environment_and_project_visibility")
    GITPOD_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GITPOD_URL_FIELD_NUMBER: _ClassVar[int]
    CODESPACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOKS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    IDES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_CREATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_CREATION_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_CREATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_CREATION_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_ENVIRONMENT_AND_PROJECT_VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    gitpod_enabled: bool
    gitpod_url: str
    codespaces_enabled: bool
    notebooks_enabled: bool
    ides_enabled: bool
    project_creation_enabled: bool
    project_creation_message: str
    environment_creation_enabled: bool
    environment_creation_message: str
    limit_environment_and_project_visibility: bool
    def __init__(self, gitpod_enabled: bool = ..., gitpod_url: _Optional[str] = ..., codespaces_enabled: bool = ..., notebooks_enabled: bool = ..., ides_enabled: bool = ..., project_creation_enabled: bool = ..., project_creation_message: _Optional[str] = ..., environment_creation_enabled: bool = ..., environment_creation_message: _Optional[str] = ..., limit_environment_and_project_visibility: bool = ...) -> None: ...

class UpdateTenantStateRequest(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: TenantState
    def __init__(self, state: _Optional[_Union[TenantState, str]] = ...) -> None: ...

class ListTenantsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AwsCloudDetails(_message.Message):
    __slots__ = ("region", "sqs_uri")
    REGION_FIELD_NUMBER: _ClassVar[int]
    SQS_URI_FIELD_NUMBER: _ClassVar[int]
    region: str
    sqs_uri: str
    def __init__(self, region: _Optional[str] = ..., sqs_uri: _Optional[str] = ...) -> None: ...

class CreateTenantRequest(_message.Message):
    __slots__ = ("name", "cloud_details", "cloud")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    name: str
    cloud_details: AwsCloudDetails
    cloud: _common_pb2.Cloud
    def __init__(self, name: _Optional[str] = ..., cloud_details: _Optional[_Union[AwsCloudDetails, _Mapping]] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ...) -> None: ...

class GetCurrentTenantRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCICDTokensRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCICDTokensResponse(_message.Message):
    __slots__ = ("tokens",)
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    tokens: _containers.RepeatedCompositeFieldContainer[AuthToken]
    def __init__(self, tokens: _Optional[_Iterable[_Union[AuthToken, _Mapping]]] = ...) -> None: ...

class CreateCICDTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateCICDTokenResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteCICDTokenRequest(_message.Message):
    __slots__ = ("client_id",)
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    def __init__(self, client_id: _Optional[str] = ...) -> None: ...

class DeleteCICDTokenResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuthToken(_message.Message):
    __slots__ = ("key", "secret", "created_at", "last_fetched_at")
    KEY_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_FETCHED_AT_FIELD_NUMBER: _ClassVar[int]
    key: str
    secret: str
    created_at: _timestamp_pb2.Timestamp
    last_fetched_at: _timestamp_pb2.Timestamp
    def __init__(self, key: _Optional[str] = ..., secret: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_fetched_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Tenant(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "name", "cloud_details", "cloud", "rbac_enabled", "state", "gitpod_enabled", "gitpod_url", "codespaces_enabled", "notebooks_enabled", "ides_enabled", "project_creation_enabled", "project_creation_message", "environment_creation_enabled", "environment_creation_message", "limit_environment_and_project_visibility")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    RBAC_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    GITPOD_ENABLED_FIELD_NUMBER: _ClassVar[int]
    GITPOD_URL_FIELD_NUMBER: _ClassVar[int]
    CODESPACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOKS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    IDES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_CREATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_CREATION_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_CREATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_CREATION_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_ENVIRONMENT_AND_PROJECT_VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    name: str
    cloud_details: AwsCloudDetails
    cloud: _common_pb2.Cloud
    rbac_enabled: bool
    state: TenantState
    gitpod_enabled: bool
    gitpod_url: str
    codespaces_enabled: bool
    notebooks_enabled: bool
    ides_enabled: bool
    project_creation_enabled: bool
    project_creation_message: str
    environment_creation_enabled: bool
    environment_creation_message: str
    limit_environment_and_project_visibility: bool
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., cloud_details: _Optional[_Union[AwsCloudDetails, _Mapping]] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., rbac_enabled: bool = ..., state: _Optional[_Union[TenantState, str]] = ..., gitpod_enabled: bool = ..., gitpod_url: _Optional[str] = ..., codespaces_enabled: bool = ..., notebooks_enabled: bool = ..., ides_enabled: bool = ..., project_creation_enabled: bool = ..., project_creation_message: _Optional[str] = ..., environment_creation_enabled: bool = ..., environment_creation_message: _Optional[str] = ..., limit_environment_and_project_visibility: bool = ...) -> None: ...

class TenantList(_message.Message):
    __slots__ = ("tenants",)
    TENANTS_FIELD_NUMBER: _ClassVar[int]
    tenants: _containers.RepeatedCompositeFieldContainer[Tenant]
    def __init__(self, tenants: _Optional[_Iterable[_Union[Tenant, _Mapping]]] = ...) -> None: ...

class GetProjectLinksRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class ProjectLink(_message.Message):
    __slots__ = ("url", "name", "icon", "color")
    URL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    url: str
    name: str
    icon: LinkIcon
    color: _common_pb2.Color
    def __init__(self, url: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[_Union[LinkIcon, str]] = ..., color: _Optional[_Union[_common_pb2.Color, str]] = ...) -> None: ...

class GetProjectLinksResponse(_message.Message):
    __slots__ = ("project_links",)
    PROJECT_LINKS_FIELD_NUMBER: _ClassVar[int]
    project_links: _containers.RepeatedCompositeFieldContainer[ProjectLink]
    def __init__(self, project_links: _Optional[_Iterable[_Union[ProjectLink, _Mapping]]] = ...) -> None: ...

class UpdateProjectLinksRequest(_message.Message):
    __slots__ = ("project_id", "project_links")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_LINKS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    project_links: _containers.RepeatedCompositeFieldContainer[ProjectLink]
    def __init__(self, project_id: _Optional[str] = ..., project_links: _Optional[_Iterable[_Union[ProjectLink, _Mapping]]] = ...) -> None: ...

class UpdateProjectLinksResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListProjectUsersRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class ListProjectUsersResponse(_message.Message):
    __slots__ = ("users",)
    class user(_message.Message):
        __slots__ = ("name", "role")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        role: ProjectRole
        def __init__(self, name: _Optional[str] = ..., role: _Optional[_Union[ProjectRole, str]] = ...) -> None: ...
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[ListProjectUsersResponse.user]
    def __init__(self, users: _Optional[_Iterable[_Union[ListProjectUsersResponse.user, _Mapping]]] = ...) -> None: ...

class AddUserToProjectRequest(_message.Message):
    __slots__ = ("project_id", "user", "role")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    user: str
    role: ProjectRole
    def __init__(self, project_id: _Optional[str] = ..., user: _Optional[str] = ..., role: _Optional[_Union[ProjectRole, str]] = ...) -> None: ...

class AddUserToProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveUserFromProjectRequest(_message.Message):
    __slots__ = ("project_id", "user")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    user: str
    def __init__(self, project_id: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...

class RemoveUserFromProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListProjectTeamsRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class ListProjectTeamsResponse(_message.Message):
    __slots__ = ("teams",)
    class team(_message.Message):
        __slots__ = ("name", "id", "role")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        id: str
        role: ProjectRole
        def __init__(self, name: _Optional[str] = ..., id: _Optional[str] = ..., role: _Optional[_Union[ProjectRole, str]] = ...) -> None: ...
    TEAMS_FIELD_NUMBER: _ClassVar[int]
    teams: _containers.RepeatedCompositeFieldContainer[ListProjectTeamsResponse.team]
    def __init__(self, teams: _Optional[_Iterable[_Union[ListProjectTeamsResponse.team, _Mapping]]] = ...) -> None: ...

class AddTeamToProjectRequest(_message.Message):
    __slots__ = ("project_id", "team_id", "role")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    team_id: str
    role: ProjectRole
    def __init__(self, project_id: _Optional[str] = ..., team_id: _Optional[str] = ..., role: _Optional[_Union[ProjectRole, str]] = ...) -> None: ...

class AddTeamToProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveTeamFromProjectRequest(_message.Message):
    __slots__ = ("project_id", "team_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    team_id: str
    def __init__(self, project_id: _Optional[str] = ..., team_id: _Optional[str] = ...) -> None: ...

class RemoveTeamFromProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateProjectTagsRequest(_message.Message):
    __slots__ = ("project_id", "tag_ids")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TAG_IDS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    tag_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_id: _Optional[str] = ..., tag_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateProjectTagsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CopyImageRequest(_message.Message):
    __slots__ = ("project_id", "project_name", "image", "tag", "target_repository")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    TARGET_REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    project_name: str
    image: str
    tag: str
    target_repository: str
    def __init__(self, project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., image: _Optional[str] = ..., tag: _Optional[str] = ..., target_repository: _Optional[str] = ...) -> None: ...

class CopyImageResponse(_message.Message):
    __slots__ = ("finished", "heartbeat")
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    finished: bool
    heartbeat: _timestamp_pb2.Timestamp
    def __init__(self, finished: bool = ..., heartbeat: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetConveyorRegistryCredentialsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetConveyorRegistryCredentialsResponse(_message.Message):
    __slots__ = ("auth", "registry_url", "airflow_v2_image", "airflow_v3_image", "package_docs_generation_image")
    AUTH_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_URL_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_V2_IMAGE_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_V3_IMAGE_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_DOCS_GENERATION_IMAGE_FIELD_NUMBER: _ClassVar[int]
    auth: str
    registry_url: str
    airflow_v2_image: str
    airflow_v3_image: str
    package_docs_generation_image: str
    def __init__(self, auth: _Optional[str] = ..., registry_url: _Optional[str] = ..., airflow_v2_image: _Optional[str] = ..., airflow_v3_image: _Optional[str] = ..., package_docs_generation_image: _Optional[str] = ...) -> None: ...

class RenderDefaultIamIdentityRequest(_message.Message):
    __slots__ = ("project_id", "environment_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    environment_id: str
    def __init__(self, project_id: _Optional[str] = ..., environment_id: _Optional[str] = ...) -> None: ...

class RenderDefaultIamIdentityResponse(_message.Message):
    __slots__ = ("iam_identity",)
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    iam_identity: str
    def __init__(self, iam_identity: _Optional[str] = ...) -> None: ...

class GetPublicRegistryDockerCredentialsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPublicRegistryDockerCredentialsResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class GetConveyorRegistryCredentialsDataPlaneRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetConveyorRegistryCredentialsDataPlaneResponse(_message.Message):
    __slots__ = ("token", "registry_url")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_URL_FIELD_NUMBER: _ClassVar[int]
    token: str
    registry_url: str
    def __init__(self, token: _Optional[str] = ..., registry_url: _Optional[str] = ...) -> None: ...

class GetProjectCredentialsDataPlaneRequest(_message.Message):
    __slots__ = ("project_name",)
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    def __init__(self, project_name: _Optional[str] = ...) -> None: ...

class GetPipelinesDataPlaneRequest(_message.Message):
    __slots__ = ("project_name", "environment_name", "pipeline_state", "airflow_version")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_STATE_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    environment_name: str
    pipeline_state: PipelineState
    airflow_version: AirflowVersion
    def __init__(self, project_name: _Optional[str] = ..., environment_name: _Optional[str] = ..., pipeline_state: _Optional[_Union[PipelineState, str]] = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class RerunTaskInstanceRequest(_message.Message):
    __slots__ = ("project_id", "environment_id", "dag_id", "dag_run_id", "task_id", "dry_run")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    environment_id: str
    dag_id: str
    dag_run_id: str
    task_id: str
    dry_run: bool
    def __init__(self, project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dry_run: bool = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class RerunTaskInstanceResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(self, tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...) -> None: ...

class RerunTaskInstanceDataPlaneRequest(_message.Message):
    __slots__ = ("project_name", "environment_name", "pipeline_id", "dag_run_id", "task_id", "dry_run", "airflow_version")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    environment_name: str
    pipeline_id: str
    dag_run_id: str
    task_id: str
    dry_run: bool
    airflow_version: AirflowVersion
    def __init__(self, project_name: _Optional[str] = ..., environment_name: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dry_run: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class GetPipelineExecutionsDataPlaneRequest(_message.Message):
    __slots__ = ("pipeline", "environment_name", "project_name", "execution_date_until", "execution_date_from", "page", "limit", "airflow_version")
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_DATE_UNTIL_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_DATE_FROM_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    pipeline: str
    environment_name: str
    project_name: str
    execution_date_until: _timestamp_pb2.Timestamp
    execution_date_from: _timestamp_pb2.Timestamp
    page: int
    limit: int
    airflow_version: AirflowVersion
    def __init__(self, pipeline: _Optional[str] = ..., environment_name: _Optional[str] = ..., project_name: _Optional[str] = ..., execution_date_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., execution_date_from: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class GetRecentlyFailedTasksDataPlaneRequest(_message.Message):
    __slots__ = ("environment_name", "project_name", "airflow_version")
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    environment_name: str
    project_name: str
    airflow_version: AirflowVersion
    def __init__(self, environment_name: _Optional[str] = ..., project_name: _Optional[str] = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class GetTasksForDagRunDataPlaneRequest(_message.Message):
    __slots__ = ("environment_name", "project_name", "dag_id", "dag_run_id", "task_id", "airflow_version")
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    environment_name: str
    project_name: str
    dag_id: str
    dag_run_id: str
    task_id: str
    airflow_version: AirflowVersion
    def __init__(self, environment_name: _Optional[str] = ..., project_name: _Optional[str] = ..., dag_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., task_id: _Optional[str] = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class GetRecentlyFailedTasksDataPlaneResponse(_message.Message):
    __slots__ = ("recently_failed_tasks",)
    RECENTLY_FAILED_TASKS_FIELD_NUMBER: _ClassVar[int]
    recently_failed_tasks: _containers.RepeatedCompositeFieldContainer[_common_pb2.AirflowTaskInstance]
    def __init__(self, recently_failed_tasks: _Optional[_Iterable[_Union[_common_pb2.AirflowTaskInstance, _Mapping]]] = ...) -> None: ...

class GetTasksForDagRunDataPlaneResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[_common_pb2.AirflowTaskInstance]
    def __init__(self, tasks: _Optional[_Iterable[_Union[_common_pb2.AirflowTaskInstance, _Mapping]]] = ...) -> None: ...

class GetImageDetailsDataPlaneRequest(_message.Message):
    __slots__ = ("project_name", "build_id")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    build_id: str
    def __init__(self, project_name: _Optional[str] = ..., build_id: _Optional[str] = ...) -> None: ...

class GetImageDetailsDataPlaneResponse(_message.Message):
    __slots__ = ("labels",)
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    LABELS_FIELD_NUMBER: _ClassVar[int]
    labels: _containers.ScalarMap[str, str]
    def __init__(self, labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CleanupBuildRequest(_message.Message):
    __slots__ = ("tenant_id", "project_id", "project_name", "build_id")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    project_id: str
    project_name: str
    build_id: str
    def __init__(self, tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., build_id: _Optional[str] = ...) -> None: ...

class CleanupBuildResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AlertConfig(_message.Message):
    __slots__ = ("id", "emails", "dag_ids", "environment_id", "environment_name", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    DAG_IDS_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    dag_ids: _containers.RepeatedScalarFieldContainer[str]
    environment_id: str
    environment_name: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., emails: _Optional[_Iterable[str]] = ..., dag_ids: _Optional[_Iterable[str]] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetAlertConfigRequest(_message.Message):
    __slots__ = ("project_id", "alert_config_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    alert_config_id: str
    def __init__(self, project_id: _Optional[str] = ..., alert_config_id: _Optional[str] = ...) -> None: ...

class GetProjectAlertConfigsRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class GetProjectAlertConfigsResponse(_message.Message):
    __slots__ = ("alert_configs",)
    ALERT_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    alert_configs: _containers.RepeatedCompositeFieldContainer[AlertConfig]
    def __init__(self, alert_configs: _Optional[_Iterable[_Union[AlertConfig, _Mapping]]] = ...) -> None: ...

class CreateAlertConfigRequest(_message.Message):
    __slots__ = ("project_id", "alert_config_id", "environment_id", "dag_ids", "emails")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_IDS_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    alert_config_id: str
    environment_id: str
    dag_ids: _containers.RepeatedScalarFieldContainer[str]
    emails: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_id: _Optional[str] = ..., alert_config_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., dag_ids: _Optional[_Iterable[str]] = ..., emails: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateAlertConfigRequest(_message.Message):
    __slots__ = ("project_id", "alert_config_id", "environment_id", "dag_ids", "emails")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_IDS_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    alert_config_id: str
    environment_id: str
    dag_ids: _containers.RepeatedScalarFieldContainer[str]
    emails: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_id: _Optional[str] = ..., alert_config_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., dag_ids: _Optional[_Iterable[str]] = ..., emails: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteAlertConfigRequest(_message.Message):
    __slots__ = ("project_id", "alert_config_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    alert_config_id: str
    def __init__(self, project_id: _Optional[str] = ..., alert_config_id: _Optional[str] = ...) -> None: ...

class DeleteAlertConfigResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AirflowEvent(_message.Message):
    __slots__ = ("execution_timestamp", "dag_id", "dag_run_id", "project_id", "environment_id", "tenant_id")
    EXECUTION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    execution_timestamp: str
    dag_id: str
    dag_run_id: str
    project_id: str
    environment_id: str
    tenant_id: str
    def __init__(self, execution_timestamp: _Optional[str] = ..., dag_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., tenant_id: _Optional[str] = ...) -> None: ...

class UpdateProjectConfigCRDRequest(_message.Message):
    __slots__ = ("id", "name", "default_iam_identity")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    default_iam_identity: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., default_iam_identity: _Optional[str] = ...) -> None: ...

class UpdateProjectConfigCRDResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteProjectConfigCRDRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteProjectConfigCRDResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateProjectRequest(_message.Message):
    __slots__ = ("name", "description", "git_repo", "git_sub_folder", "default_iam_identity", "default_ide_config", "default_ide_environment_id", "default_base_image_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    GIT_SUB_FOLDER_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IDE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IDE_ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    git_repo: str
    git_sub_folder: str
    default_iam_identity: str
    default_ide_config: _common_pb2.IDEConfig
    default_ide_environment_id: str
    default_base_image_id: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., git_repo: _Optional[str] = ..., git_sub_folder: _Optional[str] = ..., default_iam_identity: _Optional[str] = ..., default_ide_config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., default_ide_environment_id: _Optional[str] = ..., default_base_image_id: _Optional[str] = ...) -> None: ...

class UpdateProjectInfoRequest(_message.Message):
    __slots__ = ("project_id", "git_repo", "git_sub_folder", "description", "default_iam_identity", "default_ide_config", "default_ide_environment_id", "default_base_image_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    GIT_SUB_FOLDER_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IDE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IDE_ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    git_repo: str
    git_sub_folder: str
    description: str
    default_iam_identity: str
    default_ide_config: _common_pb2.IDEConfig
    default_ide_environment_id: str
    default_base_image_id: str
    def __init__(self, project_id: _Optional[str] = ..., git_repo: _Optional[str] = ..., git_sub_folder: _Optional[str] = ..., description: _Optional[str] = ..., default_iam_identity: _Optional[str] = ..., default_ide_config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., default_ide_environment_id: _Optional[str] = ..., default_base_image_id: _Optional[str] = ...) -> None: ...

class Project(_message.Message):
    __slots__ = ("id", "name", "default_iam_identity", "state", "created_at", "last_activity", "updated_at", "tenant_id", "description", "git_repo", "git_sub_folder", "tags", "default_ide_config", "default_ide_environment_id", "default_base_image_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    GIT_SUB_FOLDER_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IDE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_IDE_ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    default_iam_identity: str
    state: _common_pb2.State
    created_at: _timestamp_pb2.Timestamp
    last_activity: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    tenant_id: str
    description: str
    git_repo: str
    git_sub_folder: str
    tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.ResourceTag]
    default_ide_config: _common_pb2.IDEConfig
    default_ide_environment_id: str
    default_base_image_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., default_iam_identity: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_activity: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., tenant_id: _Optional[str] = ..., description: _Optional[str] = ..., git_repo: _Optional[str] = ..., git_sub_folder: _Optional[str] = ..., tags: _Optional[_Iterable[_Union[_tag_pb2.ResourceTag, _Mapping]]] = ..., default_ide_config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., default_ide_environment_id: _Optional[str] = ..., default_base_image_id: _Optional[str] = ...) -> None: ...

class GetProjectRequest(_message.Message):
    __slots__ = ("project_id", "project_name")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    project_name: str
    def __init__(self, project_id: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...

class GetProjectEventsRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class GetProjectEventsResponse(_message.Message):
    __slots__ = ("events",)
    class ProjectEvent(_message.Message):
        __slots__ = ("created_at", "state", "message", "project_id")
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        created_at: _timestamp_pb2.Timestamp
        state: _common_pb2.State
        message: str
        project_id: str
        def __init__(self, created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., message: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[GetProjectEventsResponse.ProjectEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[GetProjectEventsResponse.ProjectEvent, _Mapping]]] = ...) -> None: ...

class GetProjectCredentialsRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class GetProjectCredentialsResponse(_message.Message):
    __slots__ = ("aws_credentials", "azure_credentials", "registry_auth")
    class AwsProjectCredentials(_message.Message):
        __slots__ = ("access_key_id", "region", "secret_access_key", "session_token", "artifacts_bucket", "registry_url")
        ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
        REGION_FIELD_NUMBER: _ClassVar[int]
        SECRET_ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
        SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
        ARTIFACTS_BUCKET_FIELD_NUMBER: _ClassVar[int]
        REGISTRY_URL_FIELD_NUMBER: _ClassVar[int]
        access_key_id: str
        region: str
        secret_access_key: str
        session_token: str
        artifacts_bucket: str
        registry_url: str
        def __init__(self, access_key_id: _Optional[str] = ..., region: _Optional[str] = ..., secret_access_key: _Optional[str] = ..., session_token: _Optional[str] = ..., artifacts_bucket: _Optional[str] = ..., registry_url: _Optional[str] = ...) -> None: ...
    class AzureProjectCredentials(_message.Message):
        __slots__ = ("storage_account_sas_url", "storage_container", "registry_url", "notebook_registry_auth", "ide_bases_registry_auth")
        STORAGE_ACCOUNT_SAS_URL_FIELD_NUMBER: _ClassVar[int]
        STORAGE_CONTAINER_FIELD_NUMBER: _ClassVar[int]
        REGISTRY_URL_FIELD_NUMBER: _ClassVar[int]
        NOTEBOOK_REGISTRY_AUTH_FIELD_NUMBER: _ClassVar[int]
        IDE_BASES_REGISTRY_AUTH_FIELD_NUMBER: _ClassVar[int]
        storage_account_sas_url: str
        storage_container: str
        registry_url: str
        notebook_registry_auth: str
        ide_bases_registry_auth: str
        def __init__(self, storage_account_sas_url: _Optional[str] = ..., storage_container: _Optional[str] = ..., registry_url: _Optional[str] = ..., notebook_registry_auth: _Optional[str] = ..., ide_bases_registry_auth: _Optional[str] = ...) -> None: ...
    AWS_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    AZURE_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_AUTH_FIELD_NUMBER: _ClassVar[int]
    aws_credentials: GetProjectCredentialsResponse.AwsProjectCredentials
    azure_credentials: GetProjectCredentialsResponse.AzureProjectCredentials
    registry_auth: str
    def __init__(self, aws_credentials: _Optional[_Union[GetProjectCredentialsResponse.AwsProjectCredentials, _Mapping]] = ..., azure_credentials: _Optional[_Union[GetProjectCredentialsResponse.AzureProjectCredentials, _Mapping]] = ..., registry_auth: _Optional[str] = ...) -> None: ...

class DeleteProjectRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class DeleteProjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListProjectsRequest(_message.Message):
    __slots__ = ("check_access", "name")
    CHECK_ACCESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    check_access: bool
    name: str
    def __init__(self, check_access: bool = ..., name: _Optional[str] = ...) -> None: ...

class ListProjectsResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[Project]
    def __init__(self, projects: _Optional[_Iterable[_Union[Project, _Mapping]]] = ...) -> None: ...

class CreateBuildRequest(_message.Message):
    __slots__ = ("project_id", "commit_hash")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    COMMIT_HASH_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    commit_hash: str
    def __init__(self, project_id: _Optional[str] = ..., commit_hash: _Optional[str] = ...) -> None: ...

class ValidateStreamingSpecRequest(_message.Message):
    __slots__ = ("project_id", "streaming_spec")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STREAMING_SPEC_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    streaming_spec: str
    def __init__(self, project_id: _Optional[str] = ..., streaming_spec: _Optional[str] = ...) -> None: ...

class ValidateStreamingSpecResult(_message.Message):
    __slots__ = ("valid", "errorList")
    class Error(_message.Message):
        __slots__ = ("detail",)
        DETAIL_FIELD_NUMBER: _ClassVar[int]
        detail: str
        def __init__(self, detail: _Optional[str] = ...) -> None: ...
    VALID_FIELD_NUMBER: _ClassVar[int]
    ERRORLIST_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    errorList: _containers.RepeatedCompositeFieldContainer[ValidateStreamingSpecResult.Error]
    def __init__(self, valid: bool = ..., errorList: _Optional[_Iterable[_Union[ValidateStreamingSpecResult.Error, _Mapping]]] = ...) -> None: ...

class Build(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "tenant_id", "project_id", "state", "git_hash", "git_hash_repo_link", "image_details")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_REPO_LINK_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DETAILS_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    tenant_id: str
    project_id: str
    state: _common_pb2.State
    git_hash: str
    git_hash_repo_link: str
    image_details: _common_pb2.BuildImageDetails
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., git_hash: _Optional[str] = ..., git_hash_repo_link: _Optional[str] = ..., image_details: _Optional[_Union[_common_pb2.BuildImageDetails, _Mapping]] = ...) -> None: ...

class GetBuildRequest(_message.Message):
    __slots__ = ("project_id", "build_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    build_id: str
    def __init__(self, project_id: _Optional[str] = ..., build_id: _Optional[str] = ...) -> None: ...

class GetLatestBuildForGitCommitRequest(_message.Message):
    __slots__ = ("project_id", "git_hash", "limit")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    git_hash: str
    limit: int
    def __init__(self, project_id: _Optional[str] = ..., git_hash: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class ListBuildsRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class UpdateBuildRequest(_message.Message):
    __slots__ = ("build_id", "project_id", "state", "base_image_tag", "image", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_TAG_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    build_id: str
    project_id: str
    state: _common_pb2.State
    base_image_tag: str
    image: str
    labels: _containers.ScalarMap[str, str]
    def __init__(self, build_id: _Optional[str] = ..., project_id: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., base_image_tag: _Optional[str] = ..., image: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ListBuildsResponse(_message.Message):
    __slots__ = ("builds",)
    BUILDS_FIELD_NUMBER: _ClassVar[int]
    builds: _containers.RepeatedCompositeFieldContainer[Build]
    def __init__(self, builds: _Optional[_Iterable[_Union[Build, _Mapping]]] = ...) -> None: ...

class GetLatestBuildsForGitCommitResponse(_message.Message):
    __slots__ = ("builds",)
    BUILDS_FIELD_NUMBER: _ClassVar[int]
    builds: _containers.RepeatedCompositeFieldContainer[Build]
    def __init__(self, builds: _Optional[_Iterable[_Union[Build, _Mapping]]] = ...) -> None: ...

class ListProjectDeploymentsRequest(_message.Message):
    __slots__ = ("project_id", "active_only", "checkEnvironmentAccess")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    CHECKENVIRONMENTACCESS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    active_only: bool
    checkEnvironmentAccess: bool
    def __init__(self, project_id: _Optional[str] = ..., active_only: bool = ..., checkEnvironmentAccess: bool = ...) -> None: ...

class ListProjectDeploymentsResponse(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: _containers.RepeatedCompositeFieldContainer[Deployment]
    def __init__(self, deployment: _Optional[_Iterable[_Union[Deployment, _Mapping]]] = ...) -> None: ...

class RunApplicationLogsRequest(_message.Message):
    __slots__ = ("environment_id", "spark_app_id", "container_app_id", "project_id", "start_from", "application_run_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_APP_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    START_FROM_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    spark_app_id: str
    container_app_id: str
    project_id: str
    start_from: _timestamp_pb2.Timestamp
    application_run_id: str
    def __init__(self, environment_id: _Optional[str] = ..., spark_app_id: _Optional[str] = ..., container_app_id: _Optional[str] = ..., project_id: _Optional[str] = ..., start_from: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., application_run_id: _Optional[str] = ...) -> None: ...

class RunApplicationLogsDataPlaneRequest(_message.Message):
    __slots__ = ("environment_id", "environment_name", "spark_app_id", "container_app_id", "start_from")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_APP_ID_FIELD_NUMBER: _ClassVar[int]
    START_FROM_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    environment_name: str
    spark_app_id: str
    container_app_id: str
    start_from: _timestamp_pb2.Timestamp
    def __init__(self, environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., spark_app_id: _Optional[str] = ..., container_app_id: _Optional[str] = ..., start_from: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CancelApplicationRequest(_message.Message):
    __slots__ = ("environment_id", "environment_name", "spark_app_id", "container_app_id", "project_id", "application_run_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_APP_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    environment_name: str
    spark_app_id: str
    container_app_id: str
    project_id: str
    application_run_id: str
    def __init__(self, environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., spark_app_id: _Optional[str] = ..., container_app_id: _Optional[str] = ..., project_id: _Optional[str] = ..., application_run_id: _Optional[str] = ...) -> None: ...

class CancelApplicationDataplaneRequest(_message.Message):
    __slots__ = ("environment_id", "environment_name", "spark_app_id", "container_app_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_APP_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    environment_name: str
    spark_app_id: str
    container_app_id: str
    def __init__(self, environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., spark_app_id: _Optional[str] = ..., container_app_id: _Optional[str] = ...) -> None: ...

class CancelApplicationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SparkSpec(_message.Message):
    __slots__ = ("image", "application", "application_args", "spark_config", "aws_role", "azure_application_client_id", "airflow_info", "datafy_project_info", "java_class", "env_vars", "env_variables", "mode", "aws_availability_zone", "scheduled_by", "driver_instance_type", "executor_instance_type", "executor_disk_size", "number_of_executors", "instance_life_cycle", "s3_committer", "abfs_committer", "verbose")
    class SparkConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class EnvVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class EnvVariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.EnvVarResolver
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.EnvVarResolver, _Mapping]] = ...) -> None: ...
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ARGS_FIELD_NUMBER: _ClassVar[int]
    SPARK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_INFO_FIELD_NUMBER: _ClassVar[int]
    DATAFY_PROJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    JAVA_CLASS_FIELD_NUMBER: _ClassVar[int]
    ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    ENV_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    AWS_AVAILABILITY_ZONE_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_BY_FIELD_NUMBER: _ClassVar[int]
    DRIVER_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_DISK_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_EXECUTORS_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFE_CYCLE_FIELD_NUMBER: _ClassVar[int]
    S3_COMMITTER_FIELD_NUMBER: _ClassVar[int]
    ABFS_COMMITTER_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    image: str
    application: str
    application_args: _containers.RepeatedScalarFieldContainer[str]
    spark_config: _containers.ScalarMap[str, str]
    aws_role: str
    azure_application_client_id: str
    airflow_info: AirflowInfo
    datafy_project_info: DatafyProjectInfo
    java_class: str
    env_vars: _containers.ScalarMap[str, str]
    env_variables: _containers.MessageMap[str, _common_pb2.EnvVarResolver]
    mode: str
    aws_availability_zone: str
    scheduled_by: str
    driver_instance_type: str
    executor_instance_type: str
    executor_disk_size: int
    number_of_executors: int
    instance_life_cycle: str
    s3_committer: str
    abfs_committer: str
    verbose: bool
    def __init__(self, image: _Optional[str] = ..., application: _Optional[str] = ..., application_args: _Optional[_Iterable[str]] = ..., spark_config: _Optional[_Mapping[str, str]] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., airflow_info: _Optional[_Union[AirflowInfo, _Mapping]] = ..., datafy_project_info: _Optional[_Union[DatafyProjectInfo, _Mapping]] = ..., java_class: _Optional[str] = ..., env_vars: _Optional[_Mapping[str, str]] = ..., env_variables: _Optional[_Mapping[str, _common_pb2.EnvVarResolver]] = ..., mode: _Optional[str] = ..., aws_availability_zone: _Optional[str] = ..., scheduled_by: _Optional[str] = ..., driver_instance_type: _Optional[str] = ..., executor_instance_type: _Optional[str] = ..., executor_disk_size: _Optional[int] = ..., number_of_executors: _Optional[int] = ..., instance_life_cycle: _Optional[str] = ..., s3_committer: _Optional[str] = ..., abfs_committer: _Optional[str] = ..., verbose: bool = ...) -> None: ...

class AirflowInfo(_message.Message):
    __slots__ = ("task", "dag", "execution_timestamp", "data_interval_start", "data_interval_end", "task_type")
    TASK_FIELD_NUMBER: _ClassVar[int]
    DAG_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_START_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_END_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    task: str
    dag: str
    execution_timestamp: str
    data_interval_start: str
    data_interval_end: str
    task_type: _application_runs_pb2.DatafyApplicationType
    def __init__(self, task: _Optional[str] = ..., dag: _Optional[str] = ..., execution_timestamp: _Optional[str] = ..., data_interval_start: _Optional[str] = ..., data_interval_end: _Optional[str] = ..., task_type: _Optional[_Union[_application_runs_pb2.DatafyApplicationType, str]] = ...) -> None: ...

class ContainerSpec(_message.Message):
    __slots__ = ("image", "command", "args", "airflow_info", "datafy_project_info", "environment_variables", "instance_type", "aws_role", "azure_application_client_id", "instance_life_cycle", "env_variables", "scheduled_by", "disk_size", "disk_mount_path")
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class EnvVariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.EnvVarResolver
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.EnvVarResolver, _Mapping]] = ...) -> None: ...
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_INFO_FIELD_NUMBER: _ClassVar[int]
    DATAFY_PROJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFE_CYCLE_FIELD_NUMBER: _ClassVar[int]
    ENV_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_BY_FIELD_NUMBER: _ClassVar[int]
    DISK_SIZE_FIELD_NUMBER: _ClassVar[int]
    DISK_MOUNT_PATH_FIELD_NUMBER: _ClassVar[int]
    image: str
    command: _containers.RepeatedScalarFieldContainer[str]
    args: _containers.RepeatedScalarFieldContainer[str]
    airflow_info: AirflowInfo
    datafy_project_info: DatafyProjectInfo
    environment_variables: _containers.ScalarMap[str, str]
    instance_type: str
    aws_role: str
    azure_application_client_id: str
    instance_life_cycle: str
    env_variables: _containers.MessageMap[str, _common_pb2.EnvVarResolver]
    scheduled_by: str
    disk_size: int
    disk_mount_path: str
    def __init__(self, image: _Optional[str] = ..., command: _Optional[_Iterable[str]] = ..., args: _Optional[_Iterable[str]] = ..., airflow_info: _Optional[_Union[AirflowInfo, _Mapping]] = ..., datafy_project_info: _Optional[_Union[DatafyProjectInfo, _Mapping]] = ..., environment_variables: _Optional[_Mapping[str, str]] = ..., instance_type: _Optional[str] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., instance_life_cycle: _Optional[str] = ..., env_variables: _Optional[_Mapping[str, _common_pb2.EnvVarResolver]] = ..., scheduled_by: _Optional[str] = ..., disk_size: _Optional[int] = ..., disk_mount_path: _Optional[str] = ...) -> None: ...

class DatafyProjectInfo(_message.Message):
    __slots__ = ("project_name", "project_id", "build_id", "environment_id")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    project_id: str
    build_id: str
    environment_id: str
    def __init__(self, project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., build_id: _Optional[str] = ..., environment_id: _Optional[str] = ...) -> None: ...

class RunApplicationRequest(_message.Message):
    __slots__ = ("environment_id", "task_name", "timeout", "spark_spec", "container_spec")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    SPARK_SPEC_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_SPEC_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    task_name: str
    timeout: _duration_pb2.Duration
    spark_spec: SparkSpec
    container_spec: ContainerSpec
    def __init__(self, environment_id: _Optional[str] = ..., task_name: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., spark_spec: _Optional[_Union[SparkSpec, _Mapping]] = ..., container_spec: _Optional[_Union[ContainerSpec, _Mapping]] = ...) -> None: ...

class RunApplicationDataPlaneRequest(_message.Message):
    __slots__ = ("environment_id", "environment_name", "manual_run_info", "timeout", "spark_spec", "container_spec")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    MANUAL_RUN_INFO_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    SPARK_SPEC_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_SPEC_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    environment_name: str
    manual_run_info: _common_pb2.ManualRunInfo
    timeout: _duration_pb2.Duration
    spark_spec: SparkSpec
    container_spec: ContainerSpec
    def __init__(self, environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., manual_run_info: _Optional[_Union[_common_pb2.ManualRunInfo, _Mapping]] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., spark_spec: _Optional[_Union[SparkSpec, _Mapping]] = ..., container_spec: _Optional[_Union[ContainerSpec, _Mapping]] = ...) -> None: ...

class RunApplicationResponse(_message.Message):
    __slots__ = ("spark_app_name", "container_app_name", "application_run_id")
    SPARK_APP_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_APP_NAME_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    spark_app_name: str
    container_app_name: str
    application_run_id: str
    def __init__(self, spark_app_name: _Optional[str] = ..., container_app_name: _Optional[str] = ..., application_run_id: _Optional[str] = ...) -> None: ...

class UpdateAllEnvironmentsRequest(_message.Message):
    __slots__ = ("include_project_updates",)
    INCLUDE_PROJECT_UPDATES_FIELD_NUMBER: _ClassVar[int]
    include_project_updates: bool
    def __init__(self, include_project_updates: bool = ...) -> None: ...

class UpdateAllEnvironmentsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Environment(_message.Message):
    __slots__ = ("name", "state", "deletion_protection", "airflow_version", "created_at", "updated_at", "instance_lifecycle", "id", "tenant_id", "description", "cluster_id", "experimental_enabled", "datahub_integration", "airflow_configuration", "iam_identity")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DELETION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    DATAHUB_INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    name: str
    state: _common_pb2.State
    deletion_protection: bool
    airflow_version: AirflowVersion
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    instance_lifecycle: AirflowInstanceLifecycle
    id: str
    tenant_id: str
    description: str
    cluster_id: str
    experimental_enabled: bool
    datahub_integration: EnvironmentDataHubIntegration
    airflow_configuration: EnvironmentAirflowConfiguration
    iam_identity: str
    def __init__(self, name: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., deletion_protection: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., instance_lifecycle: _Optional[_Union[AirflowInstanceLifecycle, str]] = ..., id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., description: _Optional[str] = ..., cluster_id: _Optional[str] = ..., experimental_enabled: bool = ..., datahub_integration: _Optional[_Union[EnvironmentDataHubIntegration, _Mapping]] = ..., airflow_configuration: _Optional[_Union[EnvironmentAirflowConfiguration, _Mapping]] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class EnvironmentDataHubIntegration(_message.Message):
    __slots__ = ("enabled", "conn_id", "cluster", "capture_ownership_info", "capture_tags_info", "graceful_exceptions")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONN_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_OWNERSHIP_INFO_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_TAGS_INFO_FIELD_NUMBER: _ClassVar[int]
    GRACEFUL_EXCEPTIONS_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    conn_id: _wrappers_pb2.StringValue
    cluster: _wrappers_pb2.StringValue
    capture_ownership_info: _wrappers_pb2.BoolValue
    capture_tags_info: _wrappers_pb2.BoolValue
    graceful_exceptions: _wrappers_pb2.BoolValue
    def __init__(self, enabled: bool = ..., conn_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., cluster: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., capture_ownership_info: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., capture_tags_info: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., graceful_exceptions: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class EnvironmentAirflowConfiguration(_message.Message):
    __slots__ = ("core", "webserver", "secret")
    CORE_FIELD_NUMBER: _ClassVar[int]
    WEBSERVER_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    core: EnvironmentAirflowConfiguration_Core
    webserver: EnvironmentAirflowConfiguration_Webserver
    secret: EnvironmentAirflowConfiguration_SecretBackend
    def __init__(self, core: _Optional[_Union[EnvironmentAirflowConfiguration_Core, _Mapping]] = ..., webserver: _Optional[_Union[EnvironmentAirflowConfiguration_Webserver, _Mapping]] = ..., secret: _Optional[_Union[EnvironmentAirflowConfiguration_SecretBackend, _Mapping]] = ...) -> None: ...

class AirflowSecretLocation(_message.Message):
    __slots__ = ("awsSecret", "azureSecret")
    AWSSECRET_FIELD_NUMBER: _ClassVar[int]
    AZURESECRET_FIELD_NUMBER: _ClassVar[int]
    awsSecret: AwsAirflowSecretLocation
    azureSecret: AzureAirflowSecretLocation
    def __init__(self, awsSecret: _Optional[_Union[AwsAirflowSecretLocation, _Mapping]] = ..., azureSecret: _Optional[_Union[AzureAirflowSecretLocation, _Mapping]] = ...) -> None: ...

class AwsAirflowSecretLocation(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class AzureAirflowSecretLocation(_message.Message):
    __slots__ = ("name", "key_vault_name")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_VAULT_NAME_FIELD_NUMBER: _ClassVar[int]
    name: _wrappers_pb2.StringValue
    key_vault_name: _wrappers_pb2.StringValue
    def __init__(self, name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., key_vault_name: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class EnvironmentAirflowConfiguration_SecretBackend(_message.Message):
    __slots__ = ("enabled", "connection", "variable")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    connection: AirflowSecretLocation
    variable: AirflowSecretLocation
    def __init__(self, enabled: bool = ..., connection: _Optional[_Union[AirflowSecretLocation, _Mapping]] = ..., variable: _Optional[_Union[AirflowSecretLocation, _Mapping]] = ...) -> None: ...

class EnvironmentAirflowConfiguration_Webserver(_message.Message):
    __slots__ = ("navbar_color",)
    NAVBAR_COLOR_FIELD_NUMBER: _ClassVar[int]
    navbar_color: _wrappers_pb2.StringValue
    def __init__(self, navbar_color: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class EnvironmentAirflowConfiguration_Core(_message.Message):
    __slots__ = ("parallelism", "max_active_tasks_per_dag")
    PARALLELISM_FIELD_NUMBER: _ClassVar[int]
    MAX_ACTIVE_TASKS_PER_DAG_FIELD_NUMBER: _ClassVar[int]
    parallelism: _wrappers_pb2.Int32Value
    max_active_tasks_per_dag: _wrappers_pb2.Int32Value
    def __init__(self, parallelism: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ..., max_active_tasks_per_dag: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...) -> None: ...

class CreateEnvironmentRequest(_message.Message):
    __slots__ = ("name", "deletionProtection", "cluster_id", "experimental_enabled", "airflow_version", "instance_lifecycle", "datahub_integration", "airflow_configuration", "iam_identity")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DELETIONPROTECTION_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    DATAHUB_INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    name: str
    deletionProtection: bool
    cluster_id: str
    experimental_enabled: bool
    airflow_version: AirflowVersion
    instance_lifecycle: AirflowInstanceLifecycle
    datahub_integration: EnvironmentDataHubIntegration
    airflow_configuration: EnvironmentAirflowConfiguration
    iam_identity: str
    def __init__(self, name: _Optional[str] = ..., deletionProtection: bool = ..., cluster_id: _Optional[str] = ..., experimental_enabled: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ..., instance_lifecycle: _Optional[_Union[AirflowInstanceLifecycle, str]] = ..., datahub_integration: _Optional[_Union[EnvironmentDataHubIntegration, _Mapping]] = ..., airflow_configuration: _Optional[_Union[EnvironmentAirflowConfiguration, _Mapping]] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class UpdateEnvironmentRequest(_message.Message):
    __slots__ = ("environment_id", "deletionProtection", "experimental_enabled", "airflow_version", "instance_lifecycle", "datahub_integration", "airflow_configuration", "iam_identity")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DELETIONPROTECTION_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    DATAHUB_INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    deletionProtection: bool
    experimental_enabled: bool
    airflow_version: AirflowVersion
    instance_lifecycle: AirflowInstanceLifecycle
    datahub_integration: EnvironmentDataHubIntegration
    airflow_configuration: EnvironmentAirflowConfiguration
    iam_identity: str
    def __init__(self, environment_id: _Optional[str] = ..., deletionProtection: bool = ..., experimental_enabled: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ..., instance_lifecycle: _Optional[_Union[AirflowInstanceLifecycle, str]] = ..., datahub_integration: _Optional[_Union[EnvironmentDataHubIntegration, _Mapping]] = ..., airflow_configuration: _Optional[_Union[EnvironmentAirflowConfiguration, _Mapping]] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class UpdateEnvironmentInfoRequest(_message.Message):
    __slots__ = ("environment_id", "description")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    description: str
    def __init__(self, environment_id: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class GetEnvironmentRequest(_message.Message):
    __slots__ = ("environment_id",)
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    def __init__(self, environment_id: _Optional[str] = ...) -> None: ...

class UnlockEnvironmentRequest(_message.Message):
    __slots__ = ("environment_id",)
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    def __init__(self, environment_id: _Optional[str] = ...) -> None: ...

class GetEnvironmentEventsRequest(_message.Message):
    __slots__ = ("environment_id",)
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    def __init__(self, environment_id: _Optional[str] = ...) -> None: ...

class GetEnvironmentEventsResponse(_message.Message):
    __slots__ = ("events",)
    class EnvironmentEvent(_message.Message):
        __slots__ = ("created_at", "state", "message", "environment_id")
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
        created_at: _timestamp_pb2.Timestamp
        state: _common_pb2.State
        message: str
        environment_id: str
        def __init__(self, created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., message: _Optional[str] = ..., environment_id: _Optional[str] = ...) -> None: ...
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[GetEnvironmentEventsResponse.EnvironmentEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[GetEnvironmentEventsResponse.EnvironmentEvent, _Mapping]]] = ...) -> None: ...

class ListEnvironmentsRequest(_message.Message):
    __slots__ = ("state", "check_access", "name")
    class ListEnvironmentsRequestFilter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Active: _ClassVar[ListEnvironmentsRequest.ListEnvironmentsRequestFilter]
        All: _ClassVar[ListEnvironmentsRequest.ListEnvironmentsRequestFilter]
        Inactive: _ClassVar[ListEnvironmentsRequest.ListEnvironmentsRequestFilter]
    Active: ListEnvironmentsRequest.ListEnvironmentsRequestFilter
    All: ListEnvironmentsRequest.ListEnvironmentsRequestFilter
    Inactive: ListEnvironmentsRequest.ListEnvironmentsRequestFilter
    STATE_FIELD_NUMBER: _ClassVar[int]
    CHECK_ACCESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    state: ListEnvironmentsRequest.ListEnvironmentsRequestFilter
    check_access: bool
    name: str
    def __init__(self, state: _Optional[_Union[ListEnvironmentsRequest.ListEnvironmentsRequestFilter, str]] = ..., check_access: bool = ..., name: _Optional[str] = ...) -> None: ...

class ListEnvironmentsResponse(_message.Message):
    __slots__ = ("environments",)
    class ListEnvironmentsResponseEnvironment(_message.Message):
        __slots__ = ("name", "state", "cluster_name", "deletion_protection", "airflow_version", "instance_lifecycle", "created_at", "updated_at", "id", "tenant_id", "description", "cluster_id", "experimental_enabled", "datahub_integration", "airflow_configuration", "iam_identity")
        NAME_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
        DELETION_PROTECTION_FIELD_NUMBER: _ClassVar[int]
        AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
        INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        TENANT_ID_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
        EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
        DATAHUB_INTEGRATION_FIELD_NUMBER: _ClassVar[int]
        AIRFLOW_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
        IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
        name: str
        state: _common_pb2.State
        cluster_name: str
        deletion_protection: bool
        airflow_version: AirflowVersion
        instance_lifecycle: AirflowInstanceLifecycle
        created_at: _timestamp_pb2.Timestamp
        updated_at: _timestamp_pb2.Timestamp
        id: str
        tenant_id: str
        description: str
        cluster_id: str
        experimental_enabled: bool
        datahub_integration: EnvironmentDataHubIntegration
        airflow_configuration: EnvironmentAirflowConfiguration
        iam_identity: str
        def __init__(self, name: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., cluster_name: _Optional[str] = ..., deletion_protection: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ..., instance_lifecycle: _Optional[_Union[AirflowInstanceLifecycle, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., description: _Optional[str] = ..., cluster_id: _Optional[str] = ..., experimental_enabled: bool = ..., datahub_integration: _Optional[_Union[EnvironmentDataHubIntegration, _Mapping]] = ..., airflow_configuration: _Optional[_Union[EnvironmentAirflowConfiguration, _Mapping]] = ..., iam_identity: _Optional[str] = ...) -> None: ...
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    environments: _containers.RepeatedCompositeFieldContainer[ListEnvironmentsResponse.ListEnvironmentsResponseEnvironment]
    def __init__(self, environments: _Optional[_Iterable[_Union[ListEnvironmentsResponse.ListEnvironmentsResponseEnvironment, _Mapping]]] = ...) -> None: ...

class DeleteEnvironmentRequest(_message.Message):
    __slots__ = ("environment_id",)
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    def __init__(self, environment_id: _Optional[str] = ...) -> None: ...

class DeactivateDeploymentRequest(_message.Message):
    __slots__ = ("environment_id", "project_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class DeactivateDeploymentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateDeploymentRequest(_message.Message):
    __slots__ = ("environment_id", "project_id", "build_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    build_id: str
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., build_id: _Optional[str] = ...) -> None: ...

class GetActiveDeploymentRequest(_message.Message):
    __slots__ = ("environment_id", "project_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class CreateDeploymentResponse(_message.Message):
    __slots__ = ("id", "tenant_id", "environment_id", "project_id", "build_id", "deployed_on", "is_active", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    DEPLOYED_ON_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    tenant_id: str
    environment_id: str
    project_id: str
    build_id: str
    deployed_on: _timestamp_pb2.Timestamp
    is_active: bool
    state: _common_pb2.State
    def __init__(self, id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., build_id: _Optional[str] = ..., deployed_on: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., is_active: bool = ..., state: _Optional[_Union[_common_pb2.State, str]] = ...) -> None: ...

class GetActiveDeploymentResponse(_message.Message):
    __slots__ = ("id", "tenant_id", "environment_id", "project_id", "build_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    tenant_id: str
    environment_id: str
    project_id: str
    build_id: str
    def __init__(self, id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., build_id: _Optional[str] = ...) -> None: ...

class ListEnvironmentDeploymentsRequest(_message.Message):
    __slots__ = ("id", "active_only")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    id: str
    active_only: bool
    def __init__(self, id: _Optional[str] = ..., active_only: bool = ...) -> None: ...

class ListEnvironmentDeploymentsResponse(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: _containers.RepeatedCompositeFieldContainer[Deployment]
    def __init__(self, deployment: _Optional[_Iterable[_Union[Deployment, _Mapping]]] = ...) -> None: ...

class ListEnvironmentUsersRequest(_message.Message):
    __slots__ = ("environment_id",)
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    def __init__(self, environment_id: _Optional[str] = ...) -> None: ...

class ListEnvironmentUsersResponse(_message.Message):
    __slots__ = ("users",)
    class user(_message.Message):
        __slots__ = ("name", "role")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        role: EnvironmentRole
        def __init__(self, name: _Optional[str] = ..., role: _Optional[_Union[EnvironmentRole, str]] = ...) -> None: ...
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[ListEnvironmentUsersResponse.user]
    def __init__(self, users: _Optional[_Iterable[_Union[ListEnvironmentUsersResponse.user, _Mapping]]] = ...) -> None: ...

class AddUserToEnvironmentsRequest(_message.Message):
    __slots__ = ("environment_id", "user", "role")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    user: str
    role: EnvironmentRole
    def __init__(self, environment_id: _Optional[str] = ..., user: _Optional[str] = ..., role: _Optional[_Union[EnvironmentRole, str]] = ...) -> None: ...

class AddUserToEnvironmentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveUserFromEnvironmentRequest(_message.Message):
    __slots__ = ("environment_id", "user")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    user: str
    def __init__(self, environment_id: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...

class RemoveUserFromEnvironmentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListEnvironmentTeamsRequest(_message.Message):
    __slots__ = ("environment_id",)
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    def __init__(self, environment_id: _Optional[str] = ...) -> None: ...

class ListEnvironmentTeamsResponse(_message.Message):
    __slots__ = ("teams",)
    class team(_message.Message):
        __slots__ = ("name", "id", "role")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        id: str
        role: EnvironmentRole
        def __init__(self, name: _Optional[str] = ..., id: _Optional[str] = ..., role: _Optional[_Union[EnvironmentRole, str]] = ...) -> None: ...
    TEAMS_FIELD_NUMBER: _ClassVar[int]
    teams: _containers.RepeatedCompositeFieldContainer[ListEnvironmentTeamsResponse.team]
    def __init__(self, teams: _Optional[_Iterable[_Union[ListEnvironmentTeamsResponse.team, _Mapping]]] = ...) -> None: ...

class AddTeamToEnvironmentsRequest(_message.Message):
    __slots__ = ("environment_id", "team_id", "role")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    team_id: str
    role: EnvironmentRole
    def __init__(self, environment_id: _Optional[str] = ..., team_id: _Optional[str] = ..., role: _Optional[_Union[EnvironmentRole, str]] = ...) -> None: ...

class AddTeamToEnvironmentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveTeamFromEnvironmentRequest(_message.Message):
    __slots__ = ("environment_id", "team_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    team_id: str
    def __init__(self, environment_id: _Optional[str] = ..., team_id: _Optional[str] = ...) -> None: ...

class RemoveTeamFromEnvironmentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPipelinesRequest(_message.Message):
    __slots__ = ("environment_id", "project_id", "pipeline_state_filter")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_STATE_FILTER_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    pipeline_state_filter: PipelineState
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., pipeline_state_filter: _Optional[_Union[PipelineState, str]] = ...) -> None: ...

class GetPipelinesExecutionsRequest(_message.Message):
    __slots__ = ("environment_id", "project_id", "pipeline_id", "execution_date_until", "execution_date_from", "page", "limit")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_DATE_UNTIL_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_DATE_FROM_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    pipeline_id: str
    execution_date_until: _timestamp_pb2.Timestamp
    execution_date_from: _timestamp_pb2.Timestamp
    page: int
    limit: int
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., execution_date_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., execution_date_from: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class GetAirflowLogsForTaskRequest(_message.Message):
    __slots__ = ("environment_id", "project_id", "pipeline_id", "task_id", "dag_run_id", "try_number", "map_index")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TRY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MAP_INDEX_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    pipeline_id: str
    task_id: str
    dag_run_id: str
    try_number: int
    map_index: int
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., try_number: _Optional[int] = ..., map_index: _Optional[int] = ...) -> None: ...

class GetAirflowTaskInstanceRequest(_message.Message):
    __slots__ = ("environment_id", "project_id", "pipeline_id", "task_id", "dag_run_id", "map_index")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    MAP_INDEX_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    pipeline_id: str
    task_id: str
    dag_run_id: str
    map_index: int
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., map_index: _Optional[int] = ...) -> None: ...

class GetAirflowTaskInstanceInfoDataPlaneRequest(_message.Message):
    __slots__ = ("environment_name", "project_name", "pipeline_id", "task_id", "dag_run_id", "map_index", "airflow_version")
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    MAP_INDEX_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    environment_name: str
    project_name: str
    pipeline_id: str
    task_id: str
    dag_run_id: str
    map_index: int
    airflow_version: AirflowVersion
    def __init__(self, environment_name: _Optional[str] = ..., project_name: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., map_index: _Optional[int] = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class GetAirflowLogsForTaskDataPlaneRequest(_message.Message):
    __slots__ = ("environment_name", "project_name", "dag_id", "task_id", "dag_run_id", "try_number", "map_index", "airflow_version")
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TRY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MAP_INDEX_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    environment_name: str
    project_name: str
    dag_id: str
    task_id: str
    dag_run_id: str
    try_number: int
    map_index: int
    airflow_version: AirflowVersion
    def __init__(self, environment_name: _Optional[str] = ..., project_name: _Optional[str] = ..., dag_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., try_number: _Optional[int] = ..., map_index: _Optional[int] = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class GetAirflowLogsForTaskResponse(_message.Message):
    __slots__ = ("logs",)
    LOGS_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_common_pb2.Log]
    def __init__(self, logs: _Optional[_Iterable[_Union[_common_pb2.Log, _Mapping]]] = ...) -> None: ...

class PipelineExecution(_message.Message):
    __slots__ = ("pipeline_name", "status", "data_interval_start", "data_interval_end", "environment_name", "start_time", "end_time", "dag_run_id")
    PIPELINE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_START_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_END_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    pipeline_name: str
    status: PipelineExecutionStatus
    data_interval_start: _timestamp_pb2.Timestamp
    data_interval_end: _timestamp_pb2.Timestamp
    environment_name: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    dag_run_id: str
    def __init__(self, pipeline_name: _Optional[str] = ..., status: _Optional[_Union[PipelineExecutionStatus, str]] = ..., data_interval_start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., data_interval_end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., environment_name: _Optional[str] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., dag_run_id: _Optional[str] = ...) -> None: ...

class GetPipelineExecutionsResponse(_message.Message):
    __slots__ = ("pipeline_executions", "page", "visible_pages", "limit")
    PIPELINE_EXECUTIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_PAGES_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    pipeline_executions: _containers.RepeatedCompositeFieldContainer[PipelineExecution]
    page: int
    visible_pages: int
    limit: int
    def __init__(self, pipeline_executions: _Optional[_Iterable[_Union[PipelineExecution, _Mapping]]] = ..., page: _Optional[int] = ..., visible_pages: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class PipelineStreamingDetails(_message.Message):
    __slots__ = ("streaming_application_id",)
    STREAMING_APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    streaming_application_id: str
    def __init__(self, streaming_application_id: _Optional[str] = ...) -> None: ...

class PipelineLastExecutionBatchDetails(_message.Message):
    __slots__ = ("dag_run_id", "data_interval_start", "data_interval_end")
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_START_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_END_FIELD_NUMBER: _ClassVar[int]
    dag_run_id: str
    data_interval_start: _timestamp_pb2.Timestamp
    data_interval_end: _timestamp_pb2.Timestamp
    def __init__(self, dag_run_id: _Optional[str] = ..., data_interval_start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., data_interval_end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PipelineLastExecutionStreamingDetails(_message.Message):
    __slots__ = ("run_id", "streaming_application_id")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAMING_APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    streaming_application_id: str
    def __init__(self, run_id: _Optional[str] = ..., streaming_application_id: _Optional[str] = ...) -> None: ...

class PipelineLastExecution(_message.Message):
    __slots__ = ("state", "batch_details", "streaming_details")
    STATE_FIELD_NUMBER: _ClassVar[int]
    BATCH_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STREAMING_DETAILS_FIELD_NUMBER: _ClassVar[int]
    state: PipelineExecutionStatus
    batch_details: PipelineLastExecutionBatchDetails
    streaming_details: PipelineLastExecutionStreamingDetails
    def __init__(self, state: _Optional[_Union[PipelineExecutionStatus, str]] = ..., batch_details: _Optional[_Union[PipelineLastExecutionBatchDetails, _Mapping]] = ..., streaming_details: _Optional[_Union[PipelineLastExecutionStreamingDetails, _Mapping]] = ...) -> None: ...

class PipelineBatchDetails(_message.Message):
    __slots__ = ("task_failure_count", "schedule", "time_zone")
    TASK_FAILURE_COUNT_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    TIME_ZONE_FIELD_NUMBER: _ClassVar[int]
    task_failure_count: int
    schedule: str
    time_zone: str
    def __init__(self, task_failure_count: _Optional[int] = ..., schedule: _Optional[str] = ..., time_zone: _Optional[str] = ...) -> None: ...

class Pipeline(_message.Message):
    __slots__ = ("name", "last_executions", "batch_details", "streaming_details")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_EXECUTIONS_FIELD_NUMBER: _ClassVar[int]
    BATCH_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STREAMING_DETAILS_FIELD_NUMBER: _ClassVar[int]
    name: str
    last_executions: _containers.RepeatedCompositeFieldContainer[PipelineLastExecution]
    batch_details: PipelineBatchDetails
    streaming_details: PipelineStreamingDetails
    def __init__(self, name: _Optional[str] = ..., last_executions: _Optional[_Iterable[_Union[PipelineLastExecution, _Mapping]]] = ..., batch_details: _Optional[_Union[PipelineBatchDetails, _Mapping]] = ..., streaming_details: _Optional[_Union[PipelineStreamingDetails, _Mapping]] = ...) -> None: ...

class GetPipelinesResponse(_message.Message):
    __slots__ = ("pipelines",)
    PIPELINES_FIELD_NUMBER: _ClassVar[int]
    pipelines: _containers.RepeatedCompositeFieldContainer[Pipeline]
    def __init__(self, pipelines: _Optional[_Iterable[_Union[Pipeline, _Mapping]]] = ...) -> None: ...

class GetProjectEnvironmentStatusRequest(_message.Message):
    __slots__ = ("environment_id", "project_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetProjectEnvironmentStatusDataPlaneRequest(_message.Message):
    __slots__ = ("project_name", "environment_name", "airflow_version")
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    environment_name: str
    airflow_version: AirflowVersion
    def __init__(self, project_name: _Optional[str] = ..., environment_name: _Optional[str] = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class GetProjectEnvironmentStatusResponse(_message.Message):
    __slots__ = ("pipeline_success_rate", "task_success_rate")
    PIPELINE_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    TASK_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    pipeline_success_rate: int
    task_success_rate: int
    def __init__(self, pipeline_success_rate: _Optional[int] = ..., task_success_rate: _Optional[int] = ...) -> None: ...

class ProjectStateChangedEvent(_message.Message):
    __slots__ = ("tenant_id", "project_id", "project_name", "state", "message")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    project_id: str
    project_name: str
    state: _common_pb2.State
    message: str
    def __init__(self, tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., message: _Optional[str] = ...) -> None: ...

class CreateProjectCommand(_message.Message):
    __slots__ = ("tenant_id", "project_id", "project_name")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    project_id: str
    project_name: str
    def __init__(self, tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...

class DeleteProjectCommand(_message.Message):
    __slots__ = ("tenant_id", "project_id", "project_name")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    project_id: str
    project_name: str
    def __init__(self, tenant_id: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...

class EnvironmentStateChangedEvent(_message.Message):
    __slots__ = ("tenant_id", "environment_id", "environment_name", "state", "message", "build_id", "project_id", "deployment_id")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    environment_id: str
    environment_name: str
    state: _common_pb2.State
    message: str
    build_id: str
    project_id: str
    deployment_id: str
    def __init__(self, tenant_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., message: _Optional[str] = ..., build_id: _Optional[str] = ..., project_id: _Optional[str] = ..., deployment_id: _Optional[str] = ...) -> None: ...

class CreateEnvironmentCommand(_message.Message):
    __slots__ = ("tenant_id", "environment_id", "environment_name", "cluster_cloud_details", "experimental_enabled", "airflow_version", "instance_lifecycle", "datahub_integration", "airflow_configuration", "iam_identity")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    DATAHUB_INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    environment_id: str
    environment_name: str
    cluster_cloud_details: AwsClusterDetails
    experimental_enabled: bool
    airflow_version: AirflowVersion
    instance_lifecycle: AirflowInstanceLifecycle
    datahub_integration: EnvironmentDataHubIntegration
    airflow_configuration: EnvironmentAirflowConfiguration
    iam_identity: str
    def __init__(self, tenant_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., cluster_cloud_details: _Optional[_Union[AwsClusterDetails, _Mapping]] = ..., experimental_enabled: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ..., instance_lifecycle: _Optional[_Union[AirflowInstanceLifecycle, str]] = ..., datahub_integration: _Optional[_Union[EnvironmentDataHubIntegration, _Mapping]] = ..., airflow_configuration: _Optional[_Union[EnvironmentAirflowConfiguration, _Mapping]] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class DeleteEnvironmentCommand(_message.Message):
    __slots__ = ("tenant_id", "environment_id", "environment_name", "deployments", "cluster_cloud_details", "experimental_enabled", "airflow_version")
    class DeleteEnvironmentCommandDeployment(_message.Message):
        __slots__ = ("build_id", "project_name", "project_id", "deployment_id")
        BUILD_ID_FIELD_NUMBER: _ClassVar[int]
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
        build_id: str
        project_name: str
        project_id: str
        deployment_id: str
        def __init__(self, build_id: _Optional[str] = ..., project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., deployment_id: _Optional[str] = ...) -> None: ...
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    environment_id: str
    environment_name: str
    deployments: _containers.RepeatedCompositeFieldContainer[DeleteEnvironmentCommand.DeleteEnvironmentCommandDeployment]
    cluster_cloud_details: AwsClusterDetails
    experimental_enabled: bool
    airflow_version: AirflowVersion
    def __init__(self, tenant_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., deployments: _Optional[_Iterable[_Union[DeleteEnvironmentCommand.DeleteEnvironmentCommandDeployment, _Mapping]]] = ..., cluster_cloud_details: _Optional[_Union[AwsClusterDetails, _Mapping]] = ..., experimental_enabled: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ...) -> None: ...

class CreateDeploymentCommand(_message.Message):
    __slots__ = ("tenant_id", "environment_id", "environment_name", "deployments", "cluster_cloud_details", "experimental_enabled", "airflow_version", "instance_lifecycle", "datahub_integration", "airflow_configuration", "iam_identity")
    class DeploymentAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        None_: _ClassVar[CreateDeploymentCommand.DeploymentAction]
        Update: _ClassVar[CreateDeploymentCommand.DeploymentAction]
        Delete: _ClassVar[CreateDeploymentCommand.DeploymentAction]
    None_: CreateDeploymentCommand.DeploymentAction
    Update: CreateDeploymentCommand.DeploymentAction
    Delete: CreateDeploymentCommand.DeploymentAction
    class CreateDeploymentCommandDeployment(_message.Message):
        __slots__ = ("build_id", "project_name", "action", "project_id", "build_image_details", "deployment_id")
        BUILD_ID_FIELD_NUMBER: _ClassVar[int]
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        ACTION_FIELD_NUMBER: _ClassVar[int]
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        BUILD_IMAGE_DETAILS_FIELD_NUMBER: _ClassVar[int]
        DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
        build_id: str
        project_name: str
        action: CreateDeploymentCommand.DeploymentAction
        project_id: str
        build_image_details: _common_pb2.BuildImageDetails
        deployment_id: str
        def __init__(self, build_id: _Optional[str] = ..., project_name: _Optional[str] = ..., action: _Optional[_Union[CreateDeploymentCommand.DeploymentAction, str]] = ..., project_id: _Optional[str] = ..., build_image_details: _Optional[_Union[_common_pb2.BuildImageDetails, _Mapping]] = ..., deployment_id: _Optional[str] = ...) -> None: ...
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENTAL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    DATAHUB_INTEGRATION_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    environment_id: str
    environment_name: str
    deployments: _containers.RepeatedCompositeFieldContainer[CreateDeploymentCommand.CreateDeploymentCommandDeployment]
    cluster_cloud_details: AwsClusterDetails
    experimental_enabled: bool
    airflow_version: AirflowVersion
    instance_lifecycle: AirflowInstanceLifecycle
    datahub_integration: EnvironmentDataHubIntegration
    airflow_configuration: EnvironmentAirflowConfiguration
    iam_identity: str
    def __init__(self, tenant_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., deployments: _Optional[_Iterable[_Union[CreateDeploymentCommand.CreateDeploymentCommandDeployment, _Mapping]]] = ..., cluster_cloud_details: _Optional[_Union[AwsClusterDetails, _Mapping]] = ..., experimental_enabled: bool = ..., airflow_version: _Optional[_Union[AirflowVersion, str]] = ..., instance_lifecycle: _Optional[_Union[AirflowInstanceLifecycle, str]] = ..., datahub_integration: _Optional[_Union[EnvironmentDataHubIntegration, _Mapping]] = ..., airflow_configuration: _Optional[_Union[EnvironmentAirflowConfiguration, _Mapping]] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class UnlockEnvironmentCommand(_message.Message):
    __slots__ = ("tenant_id", "environment_id", "environment_name", "deployments", "cluster_cloud_details")
    class UnlockEnvironmentCommandDeployment(_message.Message):
        __slots__ = ("build_id", "project_name")
        BUILD_ID_FIELD_NUMBER: _ClassVar[int]
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        build_id: str
        project_name: str
        def __init__(self, build_id: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CLOUD_DETAILS_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    environment_id: str
    environment_name: str
    deployments: _containers.RepeatedCompositeFieldContainer[UnlockEnvironmentCommand.UnlockEnvironmentCommandDeployment]
    cluster_cloud_details: AwsClusterDetails
    def __init__(self, tenant_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., deployments: _Optional[_Iterable[_Union[UnlockEnvironmentCommand.UnlockEnvironmentCommandDeployment, _Mapping]]] = ..., cluster_cloud_details: _Optional[_Union[AwsClusterDetails, _Mapping]] = ...) -> None: ...

class GetCliRequest(_message.Message):
    __slots__ = ("os", "arch")
    OS_FIELD_NUMBER: _ClassVar[int]
    ARCH_FIELD_NUMBER: _ClassVar[int]
    os: str
    arch: str
    def __init__(self, os: _Optional[str] = ..., arch: _Optional[str] = ...) -> None: ...

class ListClustersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListClustersResponse(_message.Message):
    __slots__ = ("clusters",)
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    clusters: _containers.RepeatedCompositeFieldContainer[Cluster]
    def __init__(self, clusters: _Optional[_Iterable[_Union[Cluster, _Mapping]]] = ...) -> None: ...

class DeleteClusterRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteClusterResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetClusterRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetDefaultClusterRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateClusterRequest(_message.Message):
    __slots__ = ("name", "is_default", "aws")
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    AWS_FIELD_NUMBER: _ClassVar[int]
    name: str
    is_default: bool
    aws: AwsClusterDetails
    def __init__(self, name: _Optional[str] = ..., is_default: bool = ..., aws: _Optional[_Union[AwsClusterDetails, _Mapping]] = ...) -> None: ...

class UpdateClusterRequest(_message.Message):
    __slots__ = ("id", "name", "is_default", "aws")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    AWS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    is_default: bool
    aws: AwsClusterDetails
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., is_default: bool = ..., aws: _Optional[_Union[AwsClusterDetails, _Mapping]] = ...) -> None: ...

class AwsClusterDetails(_message.Message):
    __slots__ = ("eks_name", "iam_role", "region", "management_iam_role", "cidr_range", "oidc_url", "oidc_arn")
    EKS_NAME_FIELD_NUMBER: _ClassVar[int]
    IAM_ROLE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    MANAGEMENT_IAM_ROLE_FIELD_NUMBER: _ClassVar[int]
    CIDR_RANGE_FIELD_NUMBER: _ClassVar[int]
    OIDC_URL_FIELD_NUMBER: _ClassVar[int]
    OIDC_ARN_FIELD_NUMBER: _ClassVar[int]
    eks_name: str
    iam_role: str
    region: str
    management_iam_role: str
    cidr_range: str
    oidc_url: str
    oidc_arn: str
    def __init__(self, eks_name: _Optional[str] = ..., iam_role: _Optional[str] = ..., region: _Optional[str] = ..., management_iam_role: _Optional[str] = ..., cidr_range: _Optional[str] = ..., oidc_url: _Optional[str] = ..., oidc_arn: _Optional[str] = ...) -> None: ...

class Cluster(_message.Message):
    __slots__ = ("id", "name", "is_default", "aws")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    AWS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    is_default: bool
    aws: AwsClusterDetails
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., is_default: bool = ..., aws: _Optional[_Union[AwsClusterDetails, _Mapping]] = ...) -> None: ...

class Team(_message.Message):
    __slots__ = ("id", "name", "users", "roles", "sso_groups")
    class TeamUser(_message.Message):
        __slots__ = ("name", "team_member_type")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TEAM_MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
        name: str
        team_member_type: TeamMemberType
        def __init__(self, name: _Optional[str] = ..., team_member_type: _Optional[_Union[TeamMemberType, str]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USERS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    SSO_GROUPS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    users: _containers.RepeatedCompositeFieldContainer[Team.TeamUser]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    sso_groups: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., users: _Optional[_Iterable[_Union[Team.TeamUser, _Mapping]]] = ..., roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ..., sso_groups: _Optional[_Iterable[str]] = ...) -> None: ...

class ListTeamsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListTeamsResponse(_message.Message):
    __slots__ = ("teams",)
    TEAMS_FIELD_NUMBER: _ClassVar[int]
    teams: _containers.RepeatedCompositeFieldContainer[Team]
    def __init__(self, teams: _Optional[_Iterable[_Union[Team, _Mapping]]] = ...) -> None: ...

class CreateTeamRequest(_message.Message):
    __slots__ = ("name", "sso_groups")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SSO_GROUPS_FIELD_NUMBER: _ClassVar[int]
    name: str
    sso_groups: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., sso_groups: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateTeamRequest(_message.Message):
    __slots__ = ("id", "sso_groups")
    ID_FIELD_NUMBER: _ClassVar[int]
    SSO_GROUPS_FIELD_NUMBER: _ClassVar[int]
    id: str
    sso_groups: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., sso_groups: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTeamRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteTeamRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteTeamResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TeamAddUserRequest(_message.Message):
    __slots__ = ("id", "user_name", "team_member_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    TEAM_MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_name: str
    team_member_type: TeamMemberType
    def __init__(self, id: _Optional[str] = ..., user_name: _Optional[str] = ..., team_member_type: _Optional[_Union[TeamMemberType, str]] = ...) -> None: ...

class TeamRemoveUserRequest(_message.Message):
    __slots__ = ("id", "user_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_name: str
    def __init__(self, id: _Optional[str] = ..., user_name: _Optional[str] = ...) -> None: ...

class AddProjectsToTeamRequest(_message.Message):
    __slots__ = ("project_ids", "team_id", "role")
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    team_id: str
    role: ProjectRole
    def __init__(self, project_ids: _Optional[_Iterable[str]] = ..., team_id: _Optional[str] = ..., role: _Optional[_Union[ProjectRole, str]] = ...) -> None: ...

class AddProjectsToTeamResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AddEnvironmentsToTeamRequest(_message.Message):
    __slots__ = ("environment_ids", "team_id", "role")
    ENVIRONMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    environment_ids: _containers.RepeatedScalarFieldContainer[str]
    team_id: str
    role: EnvironmentRole
    def __init__(self, environment_ids: _Optional[_Iterable[str]] = ..., team_id: _Optional[str] = ..., role: _Optional[_Union[EnvironmentRole, str]] = ...) -> None: ...

class AddEnvironmentsToTeamResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VerifyCurrentUserEmailRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VerifyCurrentUserEmailResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OnboardNewTenantResult(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "name", "cloud")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    name: str
    cloud: _common_pb2.Cloud
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ...) -> None: ...

class ListUsersRequest(_message.Message):
    __slots__ = ("user_type",)
    class UserType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Default: _ClassVar[ListUsersRequest.UserType]
        Admin: _ClassVar[ListUsersRequest.UserType]
        NonAdmin: _ClassVar[ListUsersRequest.UserType]
    Default: ListUsersRequest.UserType
    Admin: ListUsersRequest.UserType
    NonAdmin: ListUsersRequest.UserType
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    user_type: ListUsersRequest.UserType
    def __init__(self, user_type: _Optional[_Union[ListUsersRequest.UserType, str]] = ...) -> None: ...

class ListUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, users: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class GetCurrentUserRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCurrentUserSettingsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetCurrentUserSettingsRequest(_message.Message):
    __slots__ = ("ide_settings", "projects_v2_enabled", "projects_v2_introduction_finished")
    IDE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_V2_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_V2_INTRODUCTION_FINISHED_FIELD_NUMBER: _ClassVar[int]
    ide_settings: str
    projects_v2_enabled: bool
    projects_v2_introduction_finished: bool
    def __init__(self, ide_settings: _Optional[str] = ..., projects_v2_enabled: bool = ..., projects_v2_introduction_finished: bool = ...) -> None: ...

class SetCurrentUserLastLoginDateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetCurrentUserLastLoginDateResponse(_message.Message):
    __slots__ = ("last_login_date",)
    LAST_LOGIN_DATE_FIELD_NUMBER: _ClassVar[int]
    last_login_date: _timestamp_pb2.Timestamp
    def __init__(self, last_login_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CurrentUserSettingsResponse(_message.Message):
    __slots__ = ("user", "ide_settings", "projects_v2_enabled", "projects_v2_introduction_finished")
    USER_FIELD_NUMBER: _ClassVar[int]
    IDE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_V2_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_V2_INTRODUCTION_FINISHED_FIELD_NUMBER: _ClassVar[int]
    user: str
    ide_settings: str
    projects_v2_enabled: bool
    projects_v2_introduction_finished: bool
    def __init__(self, user: _Optional[str] = ..., ide_settings: _Optional[str] = ..., projects_v2_enabled: bool = ..., projects_v2_introduction_finished: bool = ...) -> None: ...

class GetCurrentUserResponse(_message.Message):
    __slots__ = ("user", "signature", "projects_v2_enabled")
    USER_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_V2_ENABLED_FIELD_NUMBER: _ClassVar[int]
    user: User
    signature: str
    projects_v2_enabled: bool
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., signature: _Optional[str] = ..., projects_v2_enabled: bool = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("avatar", "roles", "name", "sso_groups")
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SSO_GROUPS_FIELD_NUMBER: _ClassVar[int]
    avatar: str
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    name: str
    sso_groups: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, avatar: _Optional[str] = ..., roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ..., name: _Optional[str] = ..., sso_groups: _Optional[_Iterable[str]] = ...) -> None: ...

class AddUserToAdminRoleRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class AddUserToAdminRoleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveUserFromAdminRoleRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class RemoveUserFromAdminRoleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetUserRolesRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class GetUserRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class AddProjectsToUserRequest(_message.Message):
    __slots__ = ("project_ids", "user", "role")
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    user: str
    role: ProjectRole
    def __init__(self, project_ids: _Optional[_Iterable[str]] = ..., user: _Optional[str] = ..., role: _Optional[_Union[ProjectRole, str]] = ...) -> None: ...

class AddProjectsToUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AddEnvironmentsToUserRequest(_message.Message):
    __slots__ = ("environment_ids", "user", "role")
    ENVIRONMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    environment_ids: _containers.RepeatedScalarFieldContainer[str]
    user: str
    role: EnvironmentRole
    def __init__(self, environment_ids: _Optional[_Iterable[str]] = ..., user: _Optional[str] = ..., role: _Optional[_Union[EnvironmentRole, str]] = ...) -> None: ...

class AddEnvironmentsToUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("user", "admin", "skip_invitation_email")
    USER_FIELD_NUMBER: _ClassVar[int]
    ADMIN_FIELD_NUMBER: _ClassVar[int]
    SKIP_INVITATION_EMAIL_FIELD_NUMBER: _ClassVar[int]
    user: str
    admin: bool
    skip_invitation_email: bool
    def __init__(self, user: _Optional[str] = ..., admin: bool = ..., skip_invitation_email: bool = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class DeleteUserResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GenerateCurrentUserLoginCodeRequest(_message.Message):
    __slots__ = ("access_token", "refresh_token", "id_token")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ID_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    id_token: str
    def __init__(self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ..., id_token: _Optional[str] = ...) -> None: ...

class GenerateCurrentUserLoginCodeResponse(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class ExchangeCodeForTokenRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class ExchangeCodeForTokenResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token", "id_token")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ID_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    id_token: str
    def __init__(self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ..., id_token: _Optional[str] = ...) -> None: ...

class SparkMetric(_message.Message):
    __slots__ = ("application_id", "project_id", "dag_id", "environment_id", "task_id", "build_id", "score", "duration", "executor_count", "efficiency", "cpu_efficiency", "unused_cpu_time_ms", "max_heap_memory_mb", "max_off_heap_memory_mb", "error_message", "started", "not_processed", "state")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_COUNT_FIELD_NUMBER: _ClassVar[int]
    EFFICIENCY_FIELD_NUMBER: _ClassVar[int]
    CPU_EFFICIENCY_FIELD_NUMBER: _ClassVar[int]
    UNUSED_CPU_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    MAX_HEAP_MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    MAX_OFF_HEAP_MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    NOT_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    project_id: str
    dag_id: str
    environment_id: str
    task_id: str
    build_id: str
    score: float
    duration: int
    executor_count: int
    efficiency: float
    cpu_efficiency: float
    unused_cpu_time_ms: int
    max_heap_memory_mb: int
    max_off_heap_memory_mb: int
    error_message: str
    started: _timestamp_pb2.Timestamp
    not_processed: bool
    state: SparkMetricCalculationState
    def __init__(self, application_id: _Optional[str] = ..., project_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., task_id: _Optional[str] = ..., build_id: _Optional[str] = ..., score: _Optional[float] = ..., duration: _Optional[int] = ..., executor_count: _Optional[int] = ..., efficiency: _Optional[float] = ..., cpu_efficiency: _Optional[float] = ..., unused_cpu_time_ms: _Optional[int] = ..., max_heap_memory_mb: _Optional[int] = ..., max_off_heap_memory_mb: _Optional[int] = ..., error_message: _Optional[str] = ..., started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., not_processed: bool = ..., state: _Optional[_Union[SparkMetricCalculationState, str]] = ...) -> None: ...

class TriggerSparkMetricCostCalculation(_message.Message):
    __slots__ = ("tenant_id", "finish_time")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    FINISH_TIME_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    finish_time: _timestamp_pb2.Timestamp
    def __init__(self, tenant_id: _Optional[str] = ..., finish_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetSparkMetricsResponse(_message.Message):
    __slots__ = ("metrics", "page", "last_page")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    metrics: _containers.RepeatedCompositeFieldContainer[SparkMetric]
    page: int
    last_page: bool
    def __init__(self, metrics: _Optional[_Iterable[_Union[SparkMetric, _Mapping]]] = ..., page: _Optional[int] = ..., last_page: bool = ...) -> None: ...

class CalculateSparkMetricRequest(_message.Message):
    __slots__ = ("application_id", "environment_id", "project_id")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    environment_id: str
    project_id: str
    def __init__(self, application_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class SparkMetricAggregate(_message.Message):
    __slots__ = ("project_id", "dag_id", "environment_id", "task_id", "latest_build_id", "score", "average_monthly_efficiency", "estimated_monthly_cost")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    LATEST_BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_MONTHLY_EFFICIENCY_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_MONTHLY_COST_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    dag_id: str
    environment_id: str
    task_id: str
    latest_build_id: str
    score: float
    average_monthly_efficiency: float
    estimated_monthly_cost: float
    def __init__(self, project_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., task_id: _Optional[str] = ..., latest_build_id: _Optional[str] = ..., score: _Optional[float] = ..., average_monthly_efficiency: _Optional[float] = ..., estimated_monthly_cost: _Optional[float] = ...) -> None: ...

class GetSparkMetricsAggregateResponse(_message.Message):
    __slots__ = ("metrics", "page", "last_page")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    metrics: _containers.RepeatedCompositeFieldContainer[SparkMetricAggregate]
    page: int
    last_page: bool
    def __init__(self, metrics: _Optional[_Iterable[_Union[SparkMetricAggregate, _Mapping]]] = ..., page: _Optional[int] = ..., last_page: bool = ...) -> None: ...

class GetSparkMetricsRequest(_message.Message):
    __slots__ = ("application_id", "project_id", "environment_id", "dag_id", "task_id", "page", "page_size")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    project_id: str
    environment_id: str
    dag_id: str
    task_id: str
    page: int
    page_size: int
    def __init__(self, application_id: _Optional[str] = ..., project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., task_id: _Optional[str] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class GetSparkMetricsAggregateRequest(_message.Message):
    __slots__ = ("project_id", "environment_id", "dag_id", "task_id", "max_efficiency", "page", "page_size")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_EFFICIENCY_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    environment_id: str
    dag_id: str
    task_id: str
    max_efficiency: float
    page: int
    page_size: int
    def __init__(self, project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., task_id: _Optional[str] = ..., max_efficiency: _Optional[float] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class GetSparkMetricsForApplicationRunsRequest(_message.Message):
    __slots__ = ("project_id", "environment_id", "application_ids")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_IDS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    environment_id: str
    application_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., application_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetSparkMetricsForApplicationRunsResponse(_message.Message):
    __slots__ = ("metrics",)
    METRICS_FIELD_NUMBER: _ClassVar[int]
    metrics: _containers.RepeatedCompositeFieldContainer[SparkMetric]
    def __init__(self, metrics: _Optional[_Iterable[_Union[SparkMetric, _Mapping]]] = ...) -> None: ...

class UpdateSparkMetricsRequest(_message.Message):
    __slots__ = ("application_id", "project_id", "dag_id", "environment_id", "task_id", "score", "duration", "executor_count", "efficiency", "cpu_efficiency", "unused_cpu_time_ms", "max_heap_memory_mb", "max_off_heap_memory_mb", "error_message", "started")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_COUNT_FIELD_NUMBER: _ClassVar[int]
    EFFICIENCY_FIELD_NUMBER: _ClassVar[int]
    CPU_EFFICIENCY_FIELD_NUMBER: _ClassVar[int]
    UNUSED_CPU_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    MAX_HEAP_MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    MAX_OFF_HEAP_MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    project_id: str
    dag_id: str
    environment_id: str
    task_id: str
    score: float
    duration: int
    executor_count: int
    efficiency: float
    cpu_efficiency: float
    unused_cpu_time_ms: int
    max_heap_memory_mb: int
    max_off_heap_memory_mb: int
    error_message: str
    started: _timestamp_pb2.Timestamp
    def __init__(self, application_id: _Optional[str] = ..., project_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., task_id: _Optional[str] = ..., score: _Optional[float] = ..., duration: _Optional[int] = ..., executor_count: _Optional[int] = ..., efficiency: _Optional[float] = ..., cpu_efficiency: _Optional[float] = ..., unused_cpu_time_ms: _Optional[int] = ..., max_heap_memory_mb: _Optional[int] = ..., max_off_heap_memory_mb: _Optional[int] = ..., error_message: _Optional[str] = ..., started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UpdateSparkMetricsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNodesDataPlaneRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNodeDataPlaneResponse(_message.Message):
    __slots__ = ("nodes",)
    NODES_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    def __init__(self, nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ("node_name", "node_id", "cloud_node_id", "instance_type", "cloud_instance_type", "instance_lifecycle", "created", "finished", "cloud", "node_type")
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    CLOUD_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLOUD_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    node_name: str
    node_id: str
    cloud_node_id: str
    instance_type: _common_pb2.DatafyInstanceType
    cloud_instance_type: str
    instance_lifecycle: _common_pb2.InstanceLifecycle
    created: _timestamp_pb2.Timestamp
    finished: _timestamp_pb2.Timestamp
    cloud: _common_pb2.Cloud
    node_type: _common_pb2.NodeType
    def __init__(self, node_name: _Optional[str] = ..., node_id: _Optional[str] = ..., cloud_node_id: _Optional[str] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., cloud_instance_type: _Optional[str] = ..., instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., node_type: _Optional[_Union[_common_pb2.NodeType, str]] = ...) -> None: ...

class ListProjectsForUserAccessRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class ListProjectsForUserAccessResponse(_message.Message):
    __slots__ = ("projects",)
    class ProjectForUserAccess(_message.Message):
        __slots__ = ("id", "name")
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        id: str
        name: str
        def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[ListProjectsForUserAccessResponse.ProjectForUserAccess]
    def __init__(self, projects: _Optional[_Iterable[_Union[ListProjectsForUserAccessResponse.ProjectForUserAccess, _Mapping]]] = ...) -> None: ...
