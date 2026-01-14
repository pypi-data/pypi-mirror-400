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

class IDEState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDEState_Not_Ready: _ClassVar[IDEState]
    IDEState_Ready: _ClassVar[IDEState]
    IDEState_Failed: _ClassVar[IDEState]
    IDEState_Deleting: _ClassVar[IDEState]
    IDEState_Suspending: _ClassVar[IDEState]
    IDEState_Suspended: _ClassVar[IDEState]
    IDEState_Deleted: _ClassVar[IDEState]

class IDEBuildType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDEBuildType_Project: _ClassVar[IDEBuildType]
    IDEBuildType_BaseImage: _ClassVar[IDEBuildType]
    IDEBuildType_BaseImage_Local: _ClassVar[IDEBuildType]

class IDEBuildState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDEBuildState_Unknown: _ClassVar[IDEBuildState]
    IDEBuildState_Pending: _ClassVar[IDEBuildState]
    IDEBuildState_Completed: _ClassVar[IDEBuildState]
    IDEBuildState_Running: _ClassVar[IDEBuildState]
    IDEBuildState_Failed: _ClassVar[IDEBuildState]

class IDEBaseImageState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDEBaseImageState_Unknown: _ClassVar[IDEBaseImageState]
    IDEBaseImageState_Creating: _ClassVar[IDEBaseImageState]
    IDEBaseImageState_Updating: _ClassVar[IDEBaseImageState]
    IDEBaseImageState_Running: _ClassVar[IDEBaseImageState]
    IDEBaseImageState_Completed: _ClassVar[IDEBaseImageState]
    IDEBaseImageState_Failed: _ClassVar[IDEBaseImageState]
    IDEBaseImageState_Unsupported: _ClassVar[IDEBaseImageState]
IDEState_Not_Ready: IDEState
IDEState_Ready: IDEState
IDEState_Failed: IDEState
IDEState_Deleting: IDEState
IDEState_Suspending: IDEState
IDEState_Suspended: IDEState
IDEState_Deleted: IDEState
IDEBuildType_Project: IDEBuildType
IDEBuildType_BaseImage: IDEBuildType
IDEBuildType_BaseImage_Local: IDEBuildType
IDEBuildState_Unknown: IDEBuildState
IDEBuildState_Pending: IDEBuildState
IDEBuildState_Completed: IDEBuildState
IDEBuildState_Running: IDEBuildState
IDEBuildState_Failed: IDEBuildState
IDEBaseImageState_Unknown: IDEBaseImageState
IDEBaseImageState_Creating: IDEBaseImageState
IDEBaseImageState_Updating: IDEBaseImageState
IDEBaseImageState_Running: IDEBaseImageState
IDEBaseImageState_Completed: IDEBaseImageState
IDEBaseImageState_Failed: IDEBaseImageState
IDEBaseImageState_Unsupported: IDEBaseImageState

class CalculateImageSizeRequest(_message.Message):
    __slots__ = ("registry", "repositoryName", "tag")
    REGISTRY_FIELD_NUMBER: _ClassVar[int]
    REPOSITORYNAME_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    registry: str
    repositoryName: str
    tag: str
    def __init__(self, registry: _Optional[str] = ..., repositoryName: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class CalculateImageSizeResponse(_message.Message):
    __slots__ = ("sizeInBytes",)
    SIZEINBYTES_FIELD_NUMBER: _ClassVar[int]
    sizeInBytes: int
    def __init__(self, sizeInBytes: _Optional[int] = ...) -> None: ...

class GetBaseImagesAuthorizationTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetBaseImagesAuthorizationTokenResponse(_message.Message):
    __slots__ = ("docker_auth_token", "cloud")
    DOCKER_AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    docker_auth_token: str
    cloud: _common_pb2.Cloud
    def __init__(self, docker_auth_token: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ...) -> None: ...

class CreateIDEBuildDataPlaneRequest(_message.Message):
    __slots__ = ("id", "project_name", "project_id", "config", "previous_build_id", "type", "previous_image", "from_image", "result_image", "ide_base_image_id", "created_by", "iam_identity")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_IMAGE_FIELD_NUMBER: _ClassVar[int]
    FROM_IMAGE_FIELD_NUMBER: _ClassVar[int]
    RESULT_IMAGE_FIELD_NUMBER: _ClassVar[int]
    IDE_BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_name: str
    project_id: str
    config: _common_pb2.IDEConfig
    previous_build_id: str
    type: IDEBuildType
    previous_image: str
    from_image: str
    result_image: str
    ide_base_image_id: str
    created_by: str
    iam_identity: str
    def __init__(self, id: _Optional[str] = ..., project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., previous_build_id: _Optional[str] = ..., type: _Optional[_Union[IDEBuildType, str]] = ..., previous_image: _Optional[str] = ..., from_image: _Optional[str] = ..., result_image: _Optional[str] = ..., ide_base_image_id: _Optional[str] = ..., created_by: _Optional[str] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class CleanupIDEBuildDataPlaneRequest(_message.Message):
    __slots__ = ("id", "repository_name", "registry_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    repository_name: str
    registry_id: str
    def __init__(self, id: _Optional[str] = ..., repository_name: _Optional[str] = ..., registry_id: _Optional[str] = ...) -> None: ...

class CleanupIDEBuildDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateIDEBuildDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TailIDEBuildLogsDataPlaneRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ..., **kwargs) -> None: ...

class CreateIDEDataPlaneRequest(_message.Message):
    __slots__ = ("id", "environment_name", "environment_id", "project_name", "project_id", "instance_type", "aws_role", "azure_application_client_id", "owner", "git_repo", "git_sub_folder", "build_id", "user_settings", "from_image", "max_idle_time_minutes")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    GIT_REPO_FIELD_NUMBER: _ClassVar[int]
    GIT_SUB_FOLDER_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    USER_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    FROM_IMAGE_FIELD_NUMBER: _ClassVar[int]
    MAX_IDLE_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    id: str
    environment_name: str
    environment_id: str
    project_name: str
    project_id: str
    instance_type: _common_pb2.DatafyInstanceType
    aws_role: str
    azure_application_client_id: str
    owner: str
    git_repo: str
    git_sub_folder: str
    build_id: str
    user_settings: str
    from_image: str
    max_idle_time_minutes: int
    def __init__(self, id: _Optional[str] = ..., environment_name: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., owner: _Optional[str] = ..., git_repo: _Optional[str] = ..., git_sub_folder: _Optional[str] = ..., build_id: _Optional[str] = ..., user_settings: _Optional[str] = ..., from_image: _Optional[str] = ..., max_idle_time_minutes: _Optional[int] = ...) -> None: ...

class CreateIDEDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteIDEDataPlaneRequest(_message.Message):
    __slots__ = ("id", "environment_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    environment_name: str
    def __init__(self, id: _Optional[str] = ..., environment_name: _Optional[str] = ...) -> None: ...

class SuspendIDEDataPlaneRequest(_message.Message):
    __slots__ = ("id", "environment_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    environment_name: str
    def __init__(self, id: _Optional[str] = ..., environment_name: _Optional[str] = ...) -> None: ...

class ResumeIDEDataPlaneRequest(_message.Message):
    __slots__ = ("id", "environment_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    environment_name: str
    def __init__(self, id: _Optional[str] = ..., environment_name: _Optional[str] = ...) -> None: ...

class DeleteIDEDataPlaneResponse(_message.Message):
    __slots__ = ("found",)
    FOUND_FIELD_NUMBER: _ClassVar[int]
    found: bool
    def __init__(self, found: bool = ...) -> None: ...

class SuspendIDEDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResumeIDEDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetIDEBuildLogsRequest(_message.Message):
    __slots__ = ("id", "next_token", "start_from_head", "filter_pattern")
    ID_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_FROM_HEAD_FIELD_NUMBER: _ClassVar[int]
    FILTER_PATTERN_FIELD_NUMBER: _ClassVar[int]
    id: str
    next_token: str
    start_from_head: bool
    filter_pattern: str
    def __init__(self, id: _Optional[str] = ..., next_token: _Optional[str] = ..., start_from_head: bool = ..., filter_pattern: _Optional[str] = ...) -> None: ...

class GetIDEBuildLogsResponse(_message.Message):
    __slots__ = ("logs", "next_token", "previous_token")
    LOGS_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_common_pb2.Log]
    next_token: str
    previous_token: str
    def __init__(self, logs: _Optional[_Iterable[_Union[_common_pb2.Log, _Mapping]]] = ..., next_token: _Optional[str] = ..., previous_token: _Optional[str] = ...) -> None: ...

class IDEStatus(_message.Message):
    __slots__ = ("state", "failure_reason", "not_ready_reason", "last_state_change")
    STATE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    NOT_READY_REASON_FIELD_NUMBER: _ClassVar[int]
    LAST_STATE_CHANGE_FIELD_NUMBER: _ClassVar[int]
    state: IDEState
    failure_reason: _common_pb2.PodFailureReason
    not_ready_reason: _common_pb2.NotReadyReason
    last_state_change: _timestamp_pb2.Timestamp
    def __init__(self, state: _Optional[_Union[IDEState, str]] = ..., failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., not_ready_reason: _Optional[_Union[_common_pb2.NotReadyReason, str]] = ..., last_state_change: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class IDE(_message.Message):
    __slots__ = ("id", "name", "project_id", "environment_id", "owner", "environment_name", "project_name", "instance_type", "aws_role", "azure_application_client_id", "status", "from_image_tag", "build_id", "base_image_id", "max_idle_time_minutes", "created_at", "image_size_bytes", "average_startup_time_seconds")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FROM_IMAGE_TAG_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_IDLE_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_STARTUP_TIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    project_id: str
    environment_id: str
    owner: str
    environment_name: str
    project_name: str
    instance_type: _common_pb2.DatafyInstanceType
    aws_role: str
    azure_application_client_id: str
    status: IDEStatus
    from_image_tag: str
    build_id: str
    base_image_id: str
    max_idle_time_minutes: int
    created_at: _timestamp_pb2.Timestamp
    image_size_bytes: int
    average_startup_time_seconds: float
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., owner: _Optional[str] = ..., environment_name: _Optional[str] = ..., project_name: _Optional[str] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., status: _Optional[_Union[IDEStatus, _Mapping]] = ..., from_image_tag: _Optional[str] = ..., build_id: _Optional[str] = ..., base_image_id: _Optional[str] = ..., max_idle_time_minutes: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., image_size_bytes: _Optional[int] = ..., average_startup_time_seconds: _Optional[float] = ...) -> None: ...

class CreateIDERequest(_message.Message):
    __slots__ = ("project_id", "environment_id", "instance_type", "aws_role", "azure_application_client_id", "build_id", "name", "base_image_id", "max_idle_time_minutes")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_IDLE_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    environment_id: str
    instance_type: _common_pb2.DatafyInstanceType
    aws_role: str
    azure_application_client_id: str
    build_id: str
    name: str
    base_image_id: str
    max_idle_time_minutes: int
    def __init__(self, project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., build_id: _Optional[str] = ..., name: _Optional[str] = ..., base_image_id: _Optional[str] = ..., max_idle_time_minutes: _Optional[int] = ...) -> None: ...

class GetIDERequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class UpdateIDERequest(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class FindMatchingBuildRequest(_message.Message):
    __slots__ = ("project_id", "config", "base_image_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    config: _common_pb2.IDEConfig
    base_image_id: str
    def __init__(self, project_id: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., base_image_id: _Optional[str] = ...) -> None: ...

class DeleteIDERequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteIDEResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SuspendIDERequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ResumeIDERequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListIDERequest(_message.Message):
    __slots__ = ("project_id", "environment_id", "owned")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNED_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    environment_id: str
    owned: bool
    def __init__(self, project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., owned: bool = ...) -> None: ...

class ListIDEResponse(_message.Message):
    __slots__ = ("ides",)
    IDES_FIELD_NUMBER: _ClassVar[int]
    ides: _containers.RepeatedCompositeFieldContainer[IDE]
    def __init__(self, ides: _Optional[_Iterable[_Union[IDE, _Mapping]]] = ...) -> None: ...

class GetIDEBuildRequest(_message.Message):
    __slots__ = ("id", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class IDEStateChangedEvent(_message.Message):
    __slots__ = ("tenant_id", "ide_id", "project_id", "project_name", "environment_id", "environment_name", "status", "Deleted", "cluster_id", "cloud", "region", "instance_type")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    IDE_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    ide_id: str
    project_id: str
    project_name: str
    environment_id: str
    environment_name: str
    status: IDEStatus
    Deleted: _timestamp_pb2.Timestamp
    cluster_id: str
    cloud: _common_pb2.Cloud
    region: str
    instance_type: _common_pb2.DatafyInstanceType
    def __init__(self, tenant_id: _Optional[str] = ..., ide_id: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., status: _Optional[_Union[IDEStatus, _Mapping]] = ..., Deleted: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cluster_id: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., region: _Optional[str] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ...) -> None: ...

class IDEBuild(_message.Message):
    __slots__ = ("id", "project_id", "hash", "status", "type", "base_image_id", "result_image", "base_image", "container_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_IMAGE_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    hash: str
    status: IDEBuildStatus
    type: IDEBuildType
    base_image_id: str
    result_image: str
    base_image: str
    container_id: str
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ..., hash: _Optional[str] = ..., status: _Optional[_Union[IDEBuildStatus, _Mapping]] = ..., type: _Optional[_Union[IDEBuildType, str]] = ..., base_image_id: _Optional[str] = ..., result_image: _Optional[str] = ..., base_image: _Optional[str] = ..., container_id: _Optional[str] = ...) -> None: ...

class UpdateIDEBaseImageStateRequest(_message.Message):
    __slots__ = ("id", "build_id", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    build_id: str
    status: IDEBuildStatus
    def __init__(self, id: _Optional[str] = ..., build_id: _Optional[str] = ..., status: _Optional[_Union[IDEBuildStatus, _Mapping]] = ...) -> None: ...

class IDEBuildStatus(_message.Message):
    __slots__ = ("state", "not_ready_reason")
    STATE_FIELD_NUMBER: _ClassVar[int]
    NOT_READY_REASON_FIELD_NUMBER: _ClassVar[int]
    state: IDEBuildState
    not_ready_reason: _common_pb2.NotReadyReason
    def __init__(self, state: _Optional[_Union[IDEBuildState, str]] = ..., not_ready_reason: _Optional[_Union[_common_pb2.NotReadyReason, str]] = ...) -> None: ...

class IDEBuildStateChangedEvent(_message.Message):
    __slots__ = ("tenant_id", "build_id", "project_id", "project_name", "status", "type", "ide_base_image_id", "container_id", "cluster_id", "region", "created_by", "cloud", "instanceType")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IDE_BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    INSTANCETYPE_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    build_id: str
    project_id: str
    project_name: str
    status: IDEBuildStatus
    type: IDEBuildType
    ide_base_image_id: str
    container_id: str
    cluster_id: str
    region: str
    created_by: str
    cloud: _common_pb2.Cloud
    instanceType: _common_pb2.DatafyInstanceType
    def __init__(self, tenant_id: _Optional[str] = ..., build_id: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., status: _Optional[_Union[IDEBuildStatus, _Mapping]] = ..., type: _Optional[_Union[IDEBuildType, str]] = ..., ide_base_image_id: _Optional[str] = ..., container_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., region: _Optional[str] = ..., created_by: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., instanceType: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ...) -> None: ...

class CreateIDEBuildRequest(_message.Message):
    __slots__ = ("project_id", "config", "base_image_id", "iam_identity")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    config: _common_pb2.IDEConfig
    base_image_id: str
    iam_identity: str
    def __init__(self, project_id: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., base_image_id: _Optional[str] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class CreateIDEBuildResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListIDEBuildsRequest(_message.Message):
    __slots__ = ("project_id", "hash", "state")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    hash: str
    state: IDEBuildState
    def __init__(self, project_id: _Optional[str] = ..., hash: _Optional[str] = ..., state: _Optional[_Union[IDEBuildState, str]] = ...) -> None: ...

class ListIDEBuildsResponse(_message.Message):
    __slots__ = ("builds",)
    BUILDS_FIELD_NUMBER: _ClassVar[int]
    builds: _containers.RepeatedCompositeFieldContainer[IDEBuild]
    def __init__(self, builds: _Optional[_Iterable[_Union[IDEBuild, _Mapping]]] = ...) -> None: ...

class TailIDEBuildLogsRequest(_message.Message):
    __slots__ = ("project_id", "id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    id: str
    def __init__(self, project_id: _Optional[str] = ..., id: _Optional[str] = ..., **kwargs) -> None: ...

class UpdateIDEBaseImageStateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RebuildAllIDEBaseImagesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RebuildAllIDEBaseImagesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateIDEBaseImageRequest(_message.Message):
    __slots__ = ("name", "description", "iam_identity", "config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    iam_identity: str
    config: _common_pb2.IDEConfig
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., iam_identity: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ...) -> None: ...

class BuildIDEBaseImageRequest(_message.Message):
    __slots__ = ("id", "config", "description", "iam_identity")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    config: _common_pb2.IDEConfig
    description: str
    iam_identity: str
    def __init__(self, id: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., description: _Optional[str] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class BuildLocalIDEBaseImageRequest(_message.Message):
    __slots__ = ("id", "config", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    config: _common_pb2.IDEConfig
    description: str
    def __init__(self, id: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class BuildLocalIDEBaseImageResponse(_message.Message):
    __slots__ = ("id", "build_id", "config", "base_image", "result_image", "ide_builder_image", "private_cp_docker_auth", "private_dp_docker_auth", "dp_cloud")
    ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_FIELD_NUMBER: _ClassVar[int]
    RESULT_IMAGE_FIELD_NUMBER: _ClassVar[int]
    IDE_BUILDER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_CP_DOCKER_AUTH_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_DP_DOCKER_AUTH_FIELD_NUMBER: _ClassVar[int]
    DP_CLOUD_FIELD_NUMBER: _ClassVar[int]
    id: str
    build_id: str
    config: _common_pb2.IDEConfig
    base_image: str
    result_image: str
    ide_builder_image: str
    private_cp_docker_auth: str
    private_dp_docker_auth: str
    dp_cloud: _common_pb2.Cloud
    def __init__(self, id: _Optional[str] = ..., build_id: _Optional[str] = ..., config: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., base_image: _Optional[str] = ..., result_image: _Optional[str] = ..., ide_builder_image: _Optional[str] = ..., private_cp_docker_auth: _Optional[str] = ..., private_dp_docker_auth: _Optional[str] = ..., dp_cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ...) -> None: ...

class GetIDEBaseImageRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteIDEBaseImageRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteIDEBaseImageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListIDEBaseImagesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListIDEBaseImagesResponse(_message.Message):
    __slots__ = ("base_images",)
    BASE_IMAGES_FIELD_NUMBER: _ClassVar[int]
    base_images: _containers.RepeatedCompositeFieldContainer[IDEBaseImageWithoutConfig]
    def __init__(self, base_images: _Optional[_Iterable[_Union[IDEBaseImageWithoutConfig, _Mapping]]] = ...) -> None: ...

class IDEBaseImageWithoutConfig(_message.Message):
    __slots__ = ("id", "status", "description", "name", "from_image", "build_id", "result_image", "updated_at", "image_size_bytes", "iam_identity")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FROM_IMAGE_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_IMAGE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: IDEBaseImageState
    description: str
    name: str
    from_image: str
    build_id: str
    result_image: str
    updated_at: _timestamp_pb2.Timestamp
    image_size_bytes: int
    iam_identity: str
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[IDEBaseImageState, str]] = ..., description: _Optional[str] = ..., name: _Optional[str] = ..., from_image: _Optional[str] = ..., build_id: _Optional[str] = ..., result_image: _Optional[str] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., image_size_bytes: _Optional[int] = ..., iam_identity: _Optional[str] = ...) -> None: ...

class IDEBaseImage(_message.Message):
    __slots__ = ("id", "status", "description", "name", "IDEConfig", "from_image", "build_id", "result_image", "updated_at", "image_size_bytes", "iam_identity")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IDECONFIG_FIELD_NUMBER: _ClassVar[int]
    FROM_IMAGE_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_IMAGE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    IAM_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: IDEBaseImageState
    description: str
    name: str
    IDEConfig: _common_pb2.IDEConfig
    from_image: str
    build_id: str
    result_image: str
    updated_at: _timestamp_pb2.Timestamp
    image_size_bytes: int
    iam_identity: str
    def __init__(self, id: _Optional[str] = ..., status: _Optional[_Union[IDEBaseImageState, str]] = ..., description: _Optional[str] = ..., name: _Optional[str] = ..., IDEConfig: _Optional[_Union[_common_pb2.IDEConfig, _Mapping]] = ..., from_image: _Optional[str] = ..., build_id: _Optional[str] = ..., result_image: _Optional[str] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., image_size_bytes: _Optional[int] = ..., iam_identity: _Optional[str] = ...) -> None: ...
