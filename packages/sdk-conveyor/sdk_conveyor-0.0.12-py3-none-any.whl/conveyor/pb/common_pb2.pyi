import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from conveyor.pb.tagger import tagger_pb2 as _tagger_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Cloud(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    None_: _ClassVar[Cloud]
    AWS: _ClassVar[Cloud]
    AZURE: _ClassVar[Cloud]

class InstanceLifecycle(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    InstanceLifecycle_Unknown: _ClassVar[InstanceLifecycle]
    on_demand: _ClassVar[InstanceLifecycle]
    spot: _ClassVar[InstanceLifecycle]

class NodeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NodeType_Unknown: _ClassVar[NodeType]
    NodeType_Standard: _ClassVar[NodeType]
    NodeType_Overhead: _ClassVar[NodeType]
    NodeType_Ide: _ClassVar[NodeType]

class PodFailureReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified_PodFailureReason: _ClassVar[PodFailureReason]
    OutOfMemory: _ClassVar[PodFailureReason]
    ImagePullBackOff: _ClassVar[PodFailureReason]
    EvictedDiskPressure: _ClassVar[PodFailureReason]
    ContainerCreatingForTooLong: _ClassVar[PodFailureReason]
    StartError: _ClassVar[PodFailureReason]
    SpotNodeInterrupt: _ClassVar[PodFailureReason]
    KubeletOutOfResources: _ClassVar[PodFailureReason]
    DeletedWhilePending: _ClassVar[PodFailureReason]
    DeletedWhileRunning: _ClassVar[PodFailureReason]
    ContainerStatusUnknown: _ClassVar[PodFailureReason]
    CreateContainerError: _ClassVar[PodFailureReason]
    ContainerErrorSigTerm: _ClassVar[PodFailureReason]
    ContainerErrorSigKill: _ClassVar[PodFailureReason]
    InvalidImageName: _ClassVar[PodFailureReason]
    ExecutionTimeout: _ClassVar[PodFailureReason]
    TooManyExecutorFailures: _ClassVar[PodFailureReason]
    SecretFailureCouldNotAssumeIamRole: _ClassVar[PodFailureReason]
    SecretFailureNoAccess: _ClassVar[PodFailureReason]
    SecretFailureNoIamRoleProvided: _ClassVar[PodFailureReason]
    SecretFailureDoesNotExist: _ClassVar[PodFailureReason]
    SecretFailureInvalidName: _ClassVar[PodFailureReason]
    SecretFailureAzureClientIdDoesNotExist: _ClassVar[PodFailureReason]
    SecretFailureNoAzureClientIdProvided: _ClassVar[PodFailureReason]
    SecretFailureNoFederatedIdentityCredentialProvided: _ClassVar[PodFailureReason]

class DatafyInstanceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DatafyInstanceType_Unknown: _ClassVar[DatafyInstanceType]
    mx_nano: _ClassVar[DatafyInstanceType]
    mx_micro: _ClassVar[DatafyInstanceType]
    mx_small: _ClassVar[DatafyInstanceType]
    mx_medium: _ClassVar[DatafyInstanceType]
    mx_large: _ClassVar[DatafyInstanceType]
    mx_xlarge: _ClassVar[DatafyInstanceType]
    mx_2xlarge: _ClassVar[DatafyInstanceType]
    mx_4xlarge: _ClassVar[DatafyInstanceType]
    cx_nano: _ClassVar[DatafyInstanceType]
    cx_micro: _ClassVar[DatafyInstanceType]
    cx_small: _ClassVar[DatafyInstanceType]
    cx_medium: _ClassVar[DatafyInstanceType]
    cx_large: _ClassVar[DatafyInstanceType]
    cx_xlarge: _ClassVar[DatafyInstanceType]
    cx_2xlarge: _ClassVar[DatafyInstanceType]
    cx_4xlarge: _ClassVar[DatafyInstanceType]
    rx_xlarge: _ClassVar[DatafyInstanceType]
    rx_2xlarge: _ClassVar[DatafyInstanceType]
    rx_4xlarge: _ClassVar[DatafyInstanceType]
    g5_xlarge: _ClassVar[DatafyInstanceType]
    g5_2xlarge: _ClassVar[DatafyInstanceType]
    g5_4xlarge: _ClassVar[DatafyInstanceType]
    g4dn_xlarge: _ClassVar[DatafyInstanceType]
    g4dn_2xlarge: _ClassVar[DatafyInstanceType]
    g4dn_4xlarge: _ClassVar[DatafyInstanceType]
    g6_xlarge: _ClassVar[DatafyInstanceType]
    g6_2xlarge: _ClassVar[DatafyInstanceType]
    g6_4xlarge: _ClassVar[DatafyInstanceType]

class NotReadyReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NotReadyReason_Empty: _ClassVar[NotReadyReason]
    NotReadyReason_WaitingForNode: _ClassVar[NotReadyReason]
    NotReadyReason_Initializing: _ClassVar[NotReadyReason]
    NotReadyReason_SysboxInstall: _ClassVar[NotReadyReason]
    NotReadyReason_PullingImage: _ClassVar[NotReadyReason]

class AirflowTaskInstanceState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AirflowTaskInstanceState_None: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_Queued: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_Running: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_Success: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_Restarting: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_Failed: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_UpForRetry: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_UpstreamFailed: _ClassVar[AirflowTaskInstanceState]
    AirflowTaskInstanceState_Skipped: _ClassVar[AirflowTaskInstanceState]

class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    State_Unknown: _ClassVar[State]
    CreatePending: _ClassVar[State]
    Creating: _ClassVar[State]
    Created: _ClassVar[State]
    CreateFailed: _ClassVar[State]
    UpdatePending: _ClassVar[State]
    Updating: _ClassVar[State]
    Updated: _ClassVar[State]
    UpdateFailed: _ClassVar[State]
    DeletePending: _ClassVar[State]
    Deleting: _ClassVar[State]
    Deleted: _ClassVar[State]
    DeleteFailed: _ClassVar[State]

class Color(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COLOR_NONE: _ClassVar[Color]
    COLOR_MAGENTA: _ClassVar[Color]
    COLOR_RED: _ClassVar[Color]
    COLOR_VOLCANO: _ClassVar[Color]
    COLOR_ORANGE: _ClassVar[Color]
    COLOR_GOLD: _ClassVar[Color]
    COLOR_LIME: _ClassVar[Color]
    COLOR_GREEN: _ClassVar[Color]
    COLOR_CYAN: _ClassVar[Color]
    COLOR_BLUE: _ClassVar[Color]
    COLOR_GEEKBLUE: _ClassVar[Color]
    COLOR_PURPLE: _ClassVar[Color]
None_: Cloud
AWS: Cloud
AZURE: Cloud
InstanceLifecycle_Unknown: InstanceLifecycle
on_demand: InstanceLifecycle
spot: InstanceLifecycle
NodeType_Unknown: NodeType
NodeType_Standard: NodeType
NodeType_Overhead: NodeType
NodeType_Ide: NodeType
Unspecified_PodFailureReason: PodFailureReason
OutOfMemory: PodFailureReason
ImagePullBackOff: PodFailureReason
EvictedDiskPressure: PodFailureReason
ContainerCreatingForTooLong: PodFailureReason
StartError: PodFailureReason
SpotNodeInterrupt: PodFailureReason
KubeletOutOfResources: PodFailureReason
DeletedWhilePending: PodFailureReason
DeletedWhileRunning: PodFailureReason
ContainerStatusUnknown: PodFailureReason
CreateContainerError: PodFailureReason
ContainerErrorSigTerm: PodFailureReason
ContainerErrorSigKill: PodFailureReason
InvalidImageName: PodFailureReason
ExecutionTimeout: PodFailureReason
TooManyExecutorFailures: PodFailureReason
SecretFailureCouldNotAssumeIamRole: PodFailureReason
SecretFailureNoAccess: PodFailureReason
SecretFailureNoIamRoleProvided: PodFailureReason
SecretFailureDoesNotExist: PodFailureReason
SecretFailureInvalidName: PodFailureReason
SecretFailureAzureClientIdDoesNotExist: PodFailureReason
SecretFailureNoAzureClientIdProvided: PodFailureReason
SecretFailureNoFederatedIdentityCredentialProvided: PodFailureReason
DatafyInstanceType_Unknown: DatafyInstanceType
mx_nano: DatafyInstanceType
mx_micro: DatafyInstanceType
mx_small: DatafyInstanceType
mx_medium: DatafyInstanceType
mx_large: DatafyInstanceType
mx_xlarge: DatafyInstanceType
mx_2xlarge: DatafyInstanceType
mx_4xlarge: DatafyInstanceType
cx_nano: DatafyInstanceType
cx_micro: DatafyInstanceType
cx_small: DatafyInstanceType
cx_medium: DatafyInstanceType
cx_large: DatafyInstanceType
cx_xlarge: DatafyInstanceType
cx_2xlarge: DatafyInstanceType
cx_4xlarge: DatafyInstanceType
rx_xlarge: DatafyInstanceType
rx_2xlarge: DatafyInstanceType
rx_4xlarge: DatafyInstanceType
g5_xlarge: DatafyInstanceType
g5_2xlarge: DatafyInstanceType
g5_4xlarge: DatafyInstanceType
g4dn_xlarge: DatafyInstanceType
g4dn_2xlarge: DatafyInstanceType
g4dn_4xlarge: DatafyInstanceType
g6_xlarge: DatafyInstanceType
g6_2xlarge: DatafyInstanceType
g6_4xlarge: DatafyInstanceType
NotReadyReason_Empty: NotReadyReason
NotReadyReason_WaitingForNode: NotReadyReason
NotReadyReason_Initializing: NotReadyReason
NotReadyReason_SysboxInstall: NotReadyReason
NotReadyReason_PullingImage: NotReadyReason
AirflowTaskInstanceState_None: AirflowTaskInstanceState
AirflowTaskInstanceState_Queued: AirflowTaskInstanceState
AirflowTaskInstanceState_Running: AirflowTaskInstanceState
AirflowTaskInstanceState_Success: AirflowTaskInstanceState
AirflowTaskInstanceState_Restarting: AirflowTaskInstanceState
AirflowTaskInstanceState_Failed: AirflowTaskInstanceState
AirflowTaskInstanceState_UpForRetry: AirflowTaskInstanceState
AirflowTaskInstanceState_UpstreamFailed: AirflowTaskInstanceState
AirflowTaskInstanceState_Skipped: AirflowTaskInstanceState
State_Unknown: State
CreatePending: State
Creating: State
Created: State
CreateFailed: State
UpdatePending: State
Updating: State
Updated: State
UpdateFailed: State
DeletePending: State
Deleting: State
Deleted: State
DeleteFailed: State
COLOR_NONE: Color
COLOR_MAGENTA: Color
COLOR_RED: Color
COLOR_VOLCANO: Color
COLOR_ORANGE: Color
COLOR_GOLD: Color
COLOR_LIME: Color
COLOR_GREEN: Color
COLOR_CYAN: Color
COLOR_BLUE: Color
COLOR_GEEKBLUE: Color
COLOR_PURPLE: Color

class EnvVarResolver(_message.Message):
    __slots__ = ("value", "aws_secrets_manager", "aws_s_s_m_parameter_store", "azure_key_vault")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    AWS_SECRETS_MANAGER_FIELD_NUMBER: _ClassVar[int]
    AWS_S_S_M_PARAMETER_STORE_FIELD_NUMBER: _ClassVar[int]
    AZURE_KEY_VAULT_FIELD_NUMBER: _ClassVar[int]
    value: str
    aws_secrets_manager: AwsSecretsManagerResolver
    aws_s_s_m_parameter_store: AwsSSMParameterStoreResolver
    azure_key_vault: AzureKeyVaultResolver
    def __init__(self, value: _Optional[str] = ..., aws_secrets_manager: _Optional[_Union[AwsSecretsManagerResolver, _Mapping]] = ..., aws_s_s_m_parameter_store: _Optional[_Union[AwsSSMParameterStoreResolver, _Mapping]] = ..., azure_key_vault: _Optional[_Union[AzureKeyVaultResolver, _Mapping]] = ...) -> None: ...

class AzureKeyVaultResolver(_message.Message):
    __slots__ = ("name", "key_vault_name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_VAULT_NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    key_vault_name: str
    type: str
    def __init__(self, name: _Optional[str] = ..., key_vault_name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class AwsSecretsManagerResolver(_message.Message):
    __slots__ = ("name", "path")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class AwsSSMParameterStoreResolver(_message.Message):
    __slots__ = ("name", "path")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class ContainerLogsResponse(_message.Message):
    __slots__ = ("log_line", "heartbeat", "exit_code")
    class LogLineType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NewLine: _ClassVar[ContainerLogsResponse.LogLineType]
        Raw: _ClassVar[ContainerLogsResponse.LogLineType]
    NewLine: ContainerLogsResponse.LogLineType
    Raw: ContainerLogsResponse.LogLineType
    class LogLine(_message.Message):
        __slots__ = ("log", "timestamp", "type")
        LOG_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        log: str
        timestamp: _timestamp_pb2.Timestamp
        type: ContainerLogsResponse.LogLineType
        def __init__(self, log: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[_Union[ContainerLogsResponse.LogLineType, str]] = ...) -> None: ...
    LOG_LINE_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    log_line: ContainerLogsResponse.LogLine
    heartbeat: _timestamp_pb2.Timestamp
    exit_code: int
    def __init__(self, log_line: _Optional[_Union[ContainerLogsResponse.LogLine, _Mapping]] = ..., heartbeat: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., exit_code: _Optional[int] = ...) -> None: ...

class VSCodeConfig(_message.Message):
    __slots__ = ("extensions",)
    EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    extensions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, extensions: _Optional[_Iterable[str]] = ...) -> None: ...

class BuildStep(_message.Message):
    __slots__ = ("name", "cmd")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    name: str
    cmd: str
    def __init__(self, name: _Optional[str] = ..., cmd: _Optional[str] = ...) -> None: ...

class IDEConfig(_message.Message):
    __slots__ = ("vscode", "build_steps")
    VSCODE_FIELD_NUMBER: _ClassVar[int]
    BUILD_STEPS_FIELD_NUMBER: _ClassVar[int]
    vscode: VSCodeConfig
    build_steps: _containers.RepeatedCompositeFieldContainer[BuildStep]
    def __init__(self, vscode: _Optional[_Union[VSCodeConfig, _Mapping]] = ..., build_steps: _Optional[_Iterable[_Union[BuildStep, _Mapping]]] = ...) -> None: ...

class Log(_message.Message):
    __slots__ = ("timestamp", "message")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    message: str
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class AirflowTaskInstance(_message.Message):
    __slots__ = ("dag_id", "task_id", "dag_run_id", "try_number", "map_index", "state", "data_interval_start", "data_interval_end", "start_date", "operator")
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TRY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MAP_INDEX_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_START_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_END_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    dag_id: str
    task_id: str
    dag_run_id: str
    try_number: int
    map_index: int
    state: AirflowTaskInstanceState
    data_interval_start: _timestamp_pb2.Timestamp
    data_interval_end: _timestamp_pb2.Timestamp
    start_date: _timestamp_pb2.Timestamp
    operator: str
    def __init__(self, dag_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., try_number: _Optional[int] = ..., map_index: _Optional[int] = ..., state: _Optional[_Union[AirflowTaskInstanceState, str]] = ..., data_interval_start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., data_interval_end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., operator: _Optional[str] = ...) -> None: ...

class BuildImageDetails(_message.Message):
    __slots__ = ("image", "base_image", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    BASE_IMAGE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    image: str
    base_image: str
    labels: _containers.ScalarMap[str, str]
    def __init__(self, image: _Optional[str] = ..., base_image: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ManualRunInfo(_message.Message):
    __slots__ = ("created_by", "task_name")
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    created_by: str
    task_name: str
    def __init__(self, created_by: _Optional[str] = ..., task_name: _Optional[str] = ...) -> None: ...
