import datetime

from conveyor.pb.buf.validate import validate_pb2 as _validate_pb2
import conveyor.pb.common_pb2 as _common_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from conveyor.pb.tagger import tagger_pb2 as _tagger_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeploymentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DeploymentType_Unknown: _ClassVar[DeploymentType]
    DeploymentType_Release: _ClassVar[DeploymentType]
    DeploymentType_Trial: _ClassVar[DeploymentType]

class PackageRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PackageAdmin: _ClassVar[PackageRole]
    PackageContributor: _ClassVar[PackageRole]
DeploymentType_Unknown: DeploymentType
DeploymentType_Release: DeploymentType
DeploymentType_Trial: DeploymentType
PackageAdmin: PackageRole
PackageContributor: PackageRole

class CreatePackageRequest(_message.Message):
    __slots__ = ("name", "description", "git_repo")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    git_repo: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., git_repo: _Optional[str] = ...) -> None: ...

class Package(_message.Message):
    __slots__ = ("id", "name", "description", "state", "created_at", "updated_at", "git_repo")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    state: _common_pb2.State
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    git_repo: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., git_repo: _Optional[str] = ...) -> None: ...

class DeletePackageRequest(_message.Message):
    __slots__ = ("package_id",)
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    def __init__(self, package_id: _Optional[str] = ...) -> None: ...

class GetPackageRequest(_message.Message):
    __slots__ = ("package_id",)
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    def __init__(self, package_id: _Optional[str] = ...) -> None: ...

class DeletePackageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPackagesRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ListPackagesResponse(_message.Message):
    __slots__ = ("packages",)
    PACKAGES_FIELD_NUMBER: _ClassVar[int]
    packages: _containers.RepeatedCompositeFieldContainer[Package]
    def __init__(self, packages: _Optional[_Iterable[_Union[Package, _Mapping]]] = ...) -> None: ...

class CreatePackageBuildRequest(_message.Message):
    __slots__ = ("package_id", "commit_hash", "deployment_type", "documentation")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    COMMIT_HASH_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTATION_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    commit_hash: str
    deployment_type: DeploymentType
    documentation: str
    def __init__(self, package_id: _Optional[str] = ..., commit_hash: _Optional[str] = ..., deployment_type: _Optional[_Union[DeploymentType, str]] = ..., documentation: _Optional[str] = ...) -> None: ...

class UpdatePackageBuildRequest(_message.Message):
    __slots__ = ("package_build_id", "package_id", "state", "base_image_tag", "image", "labels", "documentation")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PACKAGE_BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_TAG_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTATION_FIELD_NUMBER: _ClassVar[int]
    package_build_id: str
    package_id: str
    state: _common_pb2.State
    base_image_tag: str
    image: str
    labels: _containers.ScalarMap[str, str]
    documentation: str
    def __init__(self, package_build_id: _Optional[str] = ..., package_id: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., base_image_tag: _Optional[str] = ..., image: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., documentation: _Optional[str] = ...) -> None: ...

class GetPackageBuildRequest(_message.Message):
    __slots__ = ("package_id", "package_build_id", "package_build_version")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_BUILD_VERSION_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    package_build_id: str
    package_build_version: str
    def __init__(self, package_id: _Optional[str] = ..., package_build_id: _Optional[str] = ..., package_build_version: _Optional[str] = ...) -> None: ...

class SetPackageBuildVersionRequest(_message.Message):
    __slots__ = ("package_id", "package_build_id", "version", "deployment_type")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    package_build_id: str
    version: str
    deployment_type: DeploymentType
    def __init__(self, package_id: _Optional[str] = ..., package_build_id: _Optional[str] = ..., version: _Optional[str] = ..., deployment_type: _Optional[_Union[DeploymentType, str]] = ...) -> None: ...

class DetermineNextVersionRequest(_message.Message):
    __slots__ = ("package_id", "bump_rule")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    BUMP_RULE_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    bump_rule: str
    def __init__(self, package_id: _Optional[str] = ..., bump_rule: _Optional[str] = ...) -> None: ...

class DetermineNextVersionResponse(_message.Message):
    __slots__ = ("version",)
    VERSION_FIELD_NUMBER: _ClassVar[int]
    version: str
    def __init__(self, version: _Optional[str] = ...) -> None: ...

class PackageBuild(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "package_id", "state", "git_hash", "git_hash_repo_link", "image_details", "version", "deployment_type", "documentation")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_REPO_LINK_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DETAILS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    package_id: str
    state: _common_pb2.State
    git_hash: str
    git_hash_repo_link: str
    image_details: _common_pb2.BuildImageDetails
    version: str
    deployment_type: DeploymentType
    documentation: str
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., package_id: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., git_hash: _Optional[str] = ..., git_hash_repo_link: _Optional[str] = ..., image_details: _Optional[_Union[_common_pb2.BuildImageDetails, _Mapping]] = ..., version: _Optional[str] = ..., deployment_type: _Optional[_Union[DeploymentType, str]] = ..., documentation: _Optional[str] = ...) -> None: ...

class ListTrialPackageBuildsRequest(_message.Message):
    __slots__ = ("package_id", "version", "limit")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    version: str
    limit: int
    def __init__(self, package_id: _Optional[str] = ..., version: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class ListPackageBuildsResponse(_message.Message):
    __slots__ = ("builds",)
    BUILDS_FIELD_NUMBER: _ClassVar[int]
    builds: _containers.RepeatedCompositeFieldContainer[PackageBuild]
    def __init__(self, builds: _Optional[_Iterable[_Union[PackageBuild, _Mapping]]] = ...) -> None: ...

class PackageDeployment(_message.Message):
    __slots__ = ("id", "package_id", "build_id", "version", "git_hash", "gitHashRepoLink", "created_at", "created_by", "deployment_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    GIT_HASH_FIELD_NUMBER: _ClassVar[int]
    GITHASHREPOLINK_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    package_id: str
    build_id: str
    version: str
    git_hash: str
    gitHashRepoLink: str
    created_at: _timestamp_pb2.Timestamp
    created_by: str
    deployment_type: DeploymentType
    def __init__(self, id: _Optional[str] = ..., package_id: _Optional[str] = ..., build_id: _Optional[str] = ..., version: _Optional[str] = ..., git_hash: _Optional[str] = ..., gitHashRepoLink: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_by: _Optional[str] = ..., deployment_type: _Optional[_Union[DeploymentType, str]] = ...) -> None: ...

class CreatePackageDeploymentRequest(_message.Message):
    __slots__ = ("package_id", "version")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    version: str
    def __init__(self, package_id: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class CreatePackageDeploymentResponse(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: PackageDeployment
    def __init__(self, deployment: _Optional[_Union[PackageDeployment, _Mapping]] = ...) -> None: ...

class DeletePackageDeploymentRequest(_message.Message):
    __slots__ = ("package_id", "version")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    version: str
    def __init__(self, package_id: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class DeletePackageDeploymentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPackageDeploymentsRequest(_message.Message):
    __slots__ = ("package_id", "deployment_types", "page", "limit")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    deployment_types: _containers.RepeatedScalarFieldContainer[DeploymentType]
    page: int
    limit: int
    def __init__(self, package_id: _Optional[str] = ..., deployment_types: _Optional[_Iterable[_Union[DeploymentType, str]]] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListPackageDeploymentsResponse(_message.Message):
    __slots__ = ("deployments", "latest", "page", "visible_pages", "limit")
    DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    LATEST_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_PAGES_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    deployments: _containers.RepeatedCompositeFieldContainer[PackageDeployment]
    latest: str
    page: int
    visible_pages: int
    limit: int
    def __init__(self, deployments: _Optional[_Iterable[_Union[PackageDeployment, _Mapping]]] = ..., latest: _Optional[str] = ..., page: _Optional[int] = ..., visible_pages: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class GetPackageBuildDownloadInfoRequest(_message.Message):
    __slots__ = ("name", "release_version_constraint", "trial_version_constraint")
    NAME_FIELD_NUMBER: _ClassVar[int]
    RELEASE_VERSION_CONSTRAINT_FIELD_NUMBER: _ClassVar[int]
    TRIAL_VERSION_CONSTRAINT_FIELD_NUMBER: _ClassVar[int]
    name: str
    release_version_constraint: str
    trial_version_constraint: str
    def __init__(self, name: _Optional[str] = ..., release_version_constraint: _Optional[str] = ..., trial_version_constraint: _Optional[str] = ...) -> None: ...

class GetPackageBuildDownloadInfoDataPlaneRequest(_message.Message):
    __slots__ = ("name", "build_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    build_id: str
    def __init__(self, name: _Optional[str] = ..., build_id: _Optional[str] = ...) -> None: ...

class GetPackageBuildDownloadInfoResponse(_message.Message):
    __slots__ = ("resolved_version", "package_id", "build_id", "aws_credentials", "azure_credentials")
    class AwsCredentials(_message.Message):
        __slots__ = ("access_key_id", "region", "secret_access_key", "session_token", "artifacts_bucket", "artifacts_path_name")
        ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
        REGION_FIELD_NUMBER: _ClassVar[int]
        SECRET_ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
        SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
        ARTIFACTS_BUCKET_FIELD_NUMBER: _ClassVar[int]
        ARTIFACTS_PATH_NAME_FIELD_NUMBER: _ClassVar[int]
        access_key_id: str
        region: str
        secret_access_key: str
        session_token: str
        artifacts_bucket: str
        artifacts_path_name: str
        def __init__(self, access_key_id: _Optional[str] = ..., region: _Optional[str] = ..., secret_access_key: _Optional[str] = ..., session_token: _Optional[str] = ..., artifacts_bucket: _Optional[str] = ..., artifacts_path_name: _Optional[str] = ...) -> None: ...
    class AzureCredentials(_message.Message):
        __slots__ = ("storage_account_sas_url", "storage_container")
        STORAGE_ACCOUNT_SAS_URL_FIELD_NUMBER: _ClassVar[int]
        STORAGE_CONTAINER_FIELD_NUMBER: _ClassVar[int]
        storage_account_sas_url: str
        storage_container: str
        def __init__(self, storage_account_sas_url: _Optional[str] = ..., storage_container: _Optional[str] = ...) -> None: ...
    RESOLVED_VERSION_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    AWS_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    AZURE_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    resolved_version: str
    package_id: str
    build_id: str
    aws_credentials: GetPackageBuildDownloadInfoResponse.AwsCredentials
    azure_credentials: GetPackageBuildDownloadInfoResponse.AzureCredentials
    def __init__(self, resolved_version: _Optional[str] = ..., package_id: _Optional[str] = ..., build_id: _Optional[str] = ..., aws_credentials: _Optional[_Union[GetPackageBuildDownloadInfoResponse.AwsCredentials, _Mapping]] = ..., azure_credentials: _Optional[_Union[GetPackageBuildDownloadInfoResponse.AzureCredentials, _Mapping]] = ...) -> None: ...

class RemovePackageArtifactsRequest(_message.Message):
    __slots__ = ("package_name", "build_id")
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    package_name: str
    build_id: str
    def __init__(self, package_name: _Optional[str] = ..., build_id: _Optional[str] = ...) -> None: ...

class RemovePackageArtifactsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RolloutGlobalDeploymentRequest(_message.Message):
    __slots__ = ("package_name", "package_id", "build_id", "version")
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    package_name: str
    package_id: str
    build_id: str
    version: str
    def __init__(self, package_name: _Optional[str] = ..., package_id: _Optional[str] = ..., build_id: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class RolloutGlobalDeploymentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RollbackGlobalDeploymentRequest(_message.Message):
    __slots__ = ("build_id",)
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    build_id: str
    def __init__(self, build_id: _Optional[str] = ...) -> None: ...

class RollbackGlobalDeploymentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreatePackageCommand(_message.Message):
    __slots__ = ("tenant_id", "package_id", "package_name")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    package_id: str
    package_name: str
    def __init__(self, tenant_id: _Optional[str] = ..., package_id: _Optional[str] = ..., package_name: _Optional[str] = ...) -> None: ...

class DeletePackageCommand(_message.Message):
    __slots__ = ("tenant_id", "package_id", "package_name")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    package_id: str
    package_name: str
    def __init__(self, tenant_id: _Optional[str] = ..., package_id: _Optional[str] = ..., package_name: _Optional[str] = ...) -> None: ...

class PackageStateChangedEvent(_message.Message):
    __slots__ = ("tenant_id", "package_id", "package_name", "state", "message")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    package_id: str
    package_name: str
    state: _common_pb2.State
    message: str
    def __init__(self, tenant_id: _Optional[str] = ..., package_id: _Optional[str] = ..., package_name: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.State, str]] = ..., message: _Optional[str] = ...) -> None: ...

class GetPackageCredentialsRequest(_message.Message):
    __slots__ = ("package_id",)
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    def __init__(self, package_id: _Optional[str] = ...) -> None: ...

class GetPackageCredentialsResponse(_message.Message):
    __slots__ = ("aws_credentials", "azure_credentials")
    class AwsPackageCredentials(_message.Message):
        __slots__ = ("access_key_id", "region", "secret_access_key", "session_token", "artifacts_bucket", "registry_url", "registry_auth")
        ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
        REGION_FIELD_NUMBER: _ClassVar[int]
        SECRET_ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
        SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
        ARTIFACTS_BUCKET_FIELD_NUMBER: _ClassVar[int]
        REGISTRY_URL_FIELD_NUMBER: _ClassVar[int]
        REGISTRY_AUTH_FIELD_NUMBER: _ClassVar[int]
        access_key_id: str
        region: str
        secret_access_key: str
        session_token: str
        artifacts_bucket: str
        registry_url: str
        registry_auth: str
        def __init__(self, access_key_id: _Optional[str] = ..., region: _Optional[str] = ..., secret_access_key: _Optional[str] = ..., session_token: _Optional[str] = ..., artifacts_bucket: _Optional[str] = ..., registry_url: _Optional[str] = ..., registry_auth: _Optional[str] = ...) -> None: ...
    class AzurePackageCredentials(_message.Message):
        __slots__ = ("storage_account_sas_url", "storage_container", "registry_url", "registry_auth")
        STORAGE_ACCOUNT_SAS_URL_FIELD_NUMBER: _ClassVar[int]
        STORAGE_CONTAINER_FIELD_NUMBER: _ClassVar[int]
        REGISTRY_URL_FIELD_NUMBER: _ClassVar[int]
        REGISTRY_AUTH_FIELD_NUMBER: _ClassVar[int]
        storage_account_sas_url: str
        storage_container: str
        registry_url: str
        registry_auth: str
        def __init__(self, storage_account_sas_url: _Optional[str] = ..., storage_container: _Optional[str] = ..., registry_url: _Optional[str] = ..., registry_auth: _Optional[str] = ...) -> None: ...
    AWS_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    AZURE_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    aws_credentials: GetPackageCredentialsResponse.AwsPackageCredentials
    azure_credentials: GetPackageCredentialsResponse.AzurePackageCredentials
    def __init__(self, aws_credentials: _Optional[_Union[GetPackageCredentialsResponse.AwsPackageCredentials, _Mapping]] = ..., azure_credentials: _Optional[_Union[GetPackageCredentialsResponse.AzurePackageCredentials, _Mapping]] = ...) -> None: ...

class GetPackageCredentialsDataPlaneRequest(_message.Message):
    __slots__ = ("package_name",)
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    package_name: str
    def __init__(self, package_name: _Optional[str] = ...) -> None: ...

class AddUserToPackageRequest(_message.Message):
    __slots__ = ("package_id", "user_id", "role")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    user_id: str
    role: PackageRole
    def __init__(self, package_id: _Optional[str] = ..., user_id: _Optional[str] = ..., role: _Optional[_Union[PackageRole, str]] = ...) -> None: ...

class AddUserToPackageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AddTeamToPackageRequest(_message.Message):
    __slots__ = ("package_id", "team_id", "role")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    team_id: str
    role: PackageRole
    def __init__(self, package_id: _Optional[str] = ..., team_id: _Optional[str] = ..., role: _Optional[_Union[PackageRole, str]] = ...) -> None: ...

class AddTeamToPackageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveUserFromPackageRequest(_message.Message):
    __slots__ = ("package_id", "user_id")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    user_id: str
    def __init__(self, package_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class RemoveUserFromPackageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveTeamFromPackageRequest(_message.Message):
    __slots__ = ("package_id", "team_id")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    team_id: str
    def __init__(self, package_id: _Optional[str] = ..., team_id: _Optional[str] = ...) -> None: ...

class RemoveTeamFromPackageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPackageUsersRequest(_message.Message):
    __slots__ = ("package_id",)
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    def __init__(self, package_id: _Optional[str] = ...) -> None: ...

class ListPackageUsersResponse(_message.Message):
    __slots__ = ("users",)
    class user(_message.Message):
        __slots__ = ("name", "role")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        role: PackageRole
        def __init__(self, name: _Optional[str] = ..., role: _Optional[_Union[PackageRole, str]] = ...) -> None: ...
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[ListPackageUsersResponse.user]
    def __init__(self, users: _Optional[_Iterable[_Union[ListPackageUsersResponse.user, _Mapping]]] = ...) -> None: ...

class ListPackageTeamsRequest(_message.Message):
    __slots__ = ("package_id",)
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    def __init__(self, package_id: _Optional[str] = ...) -> None: ...

class ListPackageTeamsResponse(_message.Message):
    __slots__ = ("teams",)
    class team(_message.Message):
        __slots__ = ("name", "id", "role")
        NAME_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        id: str
        role: PackageRole
        def __init__(self, name: _Optional[str] = ..., id: _Optional[str] = ..., role: _Optional[_Union[PackageRole, str]] = ...) -> None: ...
    TEAMS_FIELD_NUMBER: _ClassVar[int]
    teams: _containers.RepeatedCompositeFieldContainer[ListPackageTeamsResponse.team]
    def __init__(self, teams: _Optional[_Iterable[_Union[ListPackageTeamsResponse.team, _Mapping]]] = ...) -> None: ...

class PackagesCopyImageRequest(_message.Message):
    __slots__ = ("package_id", "image", "tag", "target_repository")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    TARGET_REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    image: str
    tag: str
    target_repository: str
    def __init__(self, package_id: _Optional[str] = ..., image: _Optional[str] = ..., tag: _Optional[str] = ..., target_repository: _Optional[str] = ...) -> None: ...

class PackagesCopyImagDataPlaneRequest(_message.Message):
    __slots__ = ("package_name", "image", "tag", "target_repository")
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    TARGET_REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    package_name: str
    image: str
    tag: str
    target_repository: str
    def __init__(self, package_name: _Optional[str] = ..., image: _Optional[str] = ..., tag: _Optional[str] = ..., target_repository: _Optional[str] = ...) -> None: ...

class PackagesCopyImageResponse(_message.Message):
    __slots__ = ("finished", "heartbeat")
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    finished: bool
    heartbeat: _timestamp_pb2.Timestamp
    def __init__(self, finished: bool = ..., heartbeat: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UpdatePackageGitInfoRequest(_message.Message):
    __slots__ = ("package_id", "git_repo")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    git_repo: str
    def __init__(self, package_id: _Optional[str] = ..., git_repo: _Optional[str] = ...) -> None: ...

class UpdatePackageRequest(_message.Message):
    __slots__ = ("package_id", "git_repo", "description")
    PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    package_id: str
    git_repo: str
    description: str
    def __init__(self, package_id: _Optional[str] = ..., git_repo: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
