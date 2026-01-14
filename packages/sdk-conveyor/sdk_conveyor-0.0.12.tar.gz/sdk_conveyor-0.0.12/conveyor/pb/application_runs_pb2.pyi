import datetime

from conveyor.pb.buf.validate import validate_pb2 as _validate_pb2
import conveyor.pb.common_pb2 as _common_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.api import httpbody_pb2 as _httpbody_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from conveyor.pb.tagger import tagger_pb2 as _tagger_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Phase(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified_Phase: _ClassVar[Phase]
    Pending: _ClassVar[Phase]
    Running: _ClassVar[Phase]
    Succeeded: _ClassVar[Phase]
    Failed: _ClassVar[Phase]
    Unknown: _ClassVar[Phase]
    Canceling: _ClassVar[Phase]
    Canceled: _ClassVar[Phase]

class NodePhase(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NodeUnspecified: _ClassVar[NodePhase]
    NodeStarted: _ClassVar[NodePhase]
    NodeStopped: _ClassVar[NodePhase]

class NodeFailureReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified_NodeFailureReason: _ClassVar[NodeFailureReason]
    Node_SpotTerminated: _ClassVar[NodeFailureReason]
    Node_UserTerminated: _ClassVar[NodeFailureReason]
    Node_MissedDeletion: _ClassVar[NodeFailureReason]

class DatafyApplicationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified_Type: _ClassVar[DatafyApplicationType]
    Spark: _ClassVar[DatafyApplicationType]
    Container: _ClassVar[DatafyApplicationType]
    Sensor: _ClassVar[DatafyApplicationType]
    Dbt: _ClassVar[DatafyApplicationType]

class DatafyServiceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DatafyServiceType_Unknown: _ClassVar[DatafyServiceType]
    Batch: _ClassVar[DatafyServiceType]
    Streaming: _ClassVar[DatafyServiceType]
    DatafyServiceType_Ide: _ClassVar[DatafyServiceType]
    DatafyServiceType_IdeBuild: _ClassVar[DatafyServiceType]

class DatafyIdeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DatafyIdeType_Unknown: _ClassVar[DatafyIdeType]
    Ide: _ClassVar[DatafyIdeType]
    ProjectIdeBuild: _ClassVar[DatafyIdeType]
    BaseImageBuild: _ClassVar[DatafyIdeType]

class SortedOn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SortedOn_None: _ClassVar[SortedOn]
    dag_id: _ClassVar[SortedOn]
    task_id: _ClassVar[SortedOn]
    type: _ClassVar[SortedOn]
    phase: _ClassVar[SortedOn]
    created: _ClassVar[SortedOn]
    execution_timestamp: _ClassVar[SortedOn]
    environment: _ClassVar[SortedOn]
    project_name: _ClassVar[SortedOn]
    scheduled_by: _ClassVar[SortedOn]
    manual_run_info_created_by: _ClassVar[SortedOn]
    manual_run_info_task_name: _ClassVar[SortedOn]

class SortedOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SortedOrder_None: _ClassVar[SortedOrder]
    Ascending: _ClassVar[SortedOrder]
    Descending: _ClassVar[SortedOrder]

class SparkHistoryEventLogFailure(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified_EventLogFailureReason: _ClassVar[SparkHistoryEventLogFailure]
    MultipleEventLogFiles: _ClassVar[SparkHistoryEventLogFailure]
    NoEventLogFiles: _ClassVar[SparkHistoryEventLogFailure]

class ScheduledBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ScheduledBy_Unknown: _ClassVar[ScheduledBy]
    ScheduledBy_Airflow: _ClassVar[ScheduledBy]
    ScheduledBy_Manual: _ClassVar[ScheduledBy]
    ScheduledBy_Streaming: _ClassVar[ScheduledBy]
    ScheduledBy_SDK: _ClassVar[ScheduledBy]
    ScheduledBy_ConveyorRun: _ClassVar[ScheduledBy]

class ApplicationPodType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Default: _ClassVar[ApplicationPodType]
    Driver: _ClassVar[ApplicationPodType]
    Submitter: _ClassVar[ApplicationPodType]

class SparkStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SparkStatus_Empty: _ClassVar[SparkStatus]
    SparkStatus_Completed: _ClassVar[SparkStatus]
    SparkStatus_Submitting: _ClassVar[SparkStatus]
    SparkStatus_SubmittingFailed: _ClassVar[SparkStatus]
    SparkStatus_Running: _ClassVar[SparkStatus]
    SparkStatus_Failed: _ClassVar[SparkStatus]

class OperatorVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OperatorVersion_Unknown: _ClassVar[OperatorVersion]
    V1: _ClassVar[OperatorVersion]
    V2: _ClassVar[OperatorVersion]

class SparkMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SparkMode_None: _ClassVar[SparkMode]
    cluster: _ClassVar[SparkMode]
    cluster_v2: _ClassVar[SparkMode]
    local: _ClassVar[SparkMode]

class CostRange(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CostRange_Unknown: _ClassVar[CostRange]
    LastWeek: _ClassVar[CostRange]
    LastMonth: _ClassVar[CostRange]
    LastQuarter: _ClassVar[CostRange]

class AirflowTaskStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AirflowTaskStatus_None: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_Queued: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_Running: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_Success: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_Restarting: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_Failed: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_UpForRetry: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_UpForReschedule: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_Skipped: _ClassVar[AirflowTaskStatus]
    AirflowTaskStatus_Deferred: _ClassVar[AirflowTaskStatus]
Unspecified_Phase: Phase
Pending: Phase
Running: Phase
Succeeded: Phase
Failed: Phase
Unknown: Phase
Canceling: Phase
Canceled: Phase
NodeUnspecified: NodePhase
NodeStarted: NodePhase
NodeStopped: NodePhase
Unspecified_NodeFailureReason: NodeFailureReason
Node_SpotTerminated: NodeFailureReason
Node_UserTerminated: NodeFailureReason
Node_MissedDeletion: NodeFailureReason
Unspecified_Type: DatafyApplicationType
Spark: DatafyApplicationType
Container: DatafyApplicationType
Sensor: DatafyApplicationType
Dbt: DatafyApplicationType
DatafyServiceType_Unknown: DatafyServiceType
Batch: DatafyServiceType
Streaming: DatafyServiceType
DatafyServiceType_Ide: DatafyServiceType
DatafyServiceType_IdeBuild: DatafyServiceType
DatafyIdeType_Unknown: DatafyIdeType
Ide: DatafyIdeType
ProjectIdeBuild: DatafyIdeType
BaseImageBuild: DatafyIdeType
SortedOn_None: SortedOn
dag_id: SortedOn
task_id: SortedOn
type: SortedOn
phase: SortedOn
created: SortedOn
execution_timestamp: SortedOn
environment: SortedOn
project_name: SortedOn
scheduled_by: SortedOn
manual_run_info_created_by: SortedOn
manual_run_info_task_name: SortedOn
SortedOrder_None: SortedOrder
Ascending: SortedOrder
Descending: SortedOrder
Unspecified_EventLogFailureReason: SparkHistoryEventLogFailure
MultipleEventLogFiles: SparkHistoryEventLogFailure
NoEventLogFiles: SparkHistoryEventLogFailure
ScheduledBy_Unknown: ScheduledBy
ScheduledBy_Airflow: ScheduledBy
ScheduledBy_Manual: ScheduledBy
ScheduledBy_Streaming: ScheduledBy
ScheduledBy_SDK: ScheduledBy
ScheduledBy_ConveyorRun: ScheduledBy
Default: ApplicationPodType
Driver: ApplicationPodType
Submitter: ApplicationPodType
SparkStatus_Empty: SparkStatus
SparkStatus_Completed: SparkStatus
SparkStatus_Submitting: SparkStatus
SparkStatus_SubmittingFailed: SparkStatus
SparkStatus_Running: SparkStatus
SparkStatus_Failed: SparkStatus
OperatorVersion_Unknown: OperatorVersion
V1: OperatorVersion
V2: OperatorVersion
SparkMode_None: SparkMode
cluster: SparkMode
cluster_v2: SparkMode
local: SparkMode
CostRange_Unknown: CostRange
LastWeek: CostRange
LastMonth: CostRange
LastQuarter: CostRange
AirflowTaskStatus_None: AirflowTaskStatus
AirflowTaskStatus_Queued: AirflowTaskStatus
AirflowTaskStatus_Running: AirflowTaskStatus
AirflowTaskStatus_Success: AirflowTaskStatus
AirflowTaskStatus_Restarting: AirflowTaskStatus
AirflowTaskStatus_Failed: AirflowTaskStatus
AirflowTaskStatus_UpForRetry: AirflowTaskStatus
AirflowTaskStatus_UpForReschedule: AirflowTaskStatus
AirflowTaskStatus_Skipped: AirflowTaskStatus
AirflowTaskStatus_Deferred: AirflowTaskStatus

class DownloadApplicationRunLogsByApplicationIdRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class GetApplicationRunsRequest(_message.Message):
    __slots__ = ("environment", "page", "limit", "dag_id", "task_id", "type", "phase", "until", "sorted_on", "sorted_order", "execution_timestamp_from", "execution_timestamp_until", "project_name", "environment_id", "project_id", "scheduled_by", "dag_run_id", "map_index")
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    UNTIL_FIELD_NUMBER: _ClassVar[int]
    SORTED_ON_FIELD_NUMBER: _ClassVar[int]
    SORTED_ORDER_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIMESTAMP_FROM_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIMESTAMP_UNTIL_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_BY_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    MAP_INDEX_FIELD_NUMBER: _ClassVar[int]
    environment: str
    page: int
    limit: int
    dag_id: str
    task_id: str
    type: _containers.RepeatedScalarFieldContainer[DatafyApplicationType]
    phase: _containers.RepeatedScalarFieldContainer[Phase]
    until: _timestamp_pb2.Timestamp
    sorted_on: SortedOn
    sorted_order: SortedOrder
    execution_timestamp_from: _timestamp_pb2.Timestamp
    execution_timestamp_until: _timestamp_pb2.Timestamp
    project_name: str
    environment_id: str
    project_id: str
    scheduled_by: _containers.RepeatedScalarFieldContainer[ScheduledBy]
    dag_run_id: str
    map_index: int
    def __init__(self, environment: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ..., dag_id: _Optional[str] = ..., task_id: _Optional[str] = ..., type: _Optional[_Iterable[_Union[DatafyApplicationType, str]]] = ..., phase: _Optional[_Iterable[_Union[Phase, str]]] = ..., until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., sorted_on: _Optional[_Union[SortedOn, str]] = ..., sorted_order: _Optional[_Union[SortedOrder, str]] = ..., execution_timestamp_from: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., execution_timestamp_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., project_name: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., scheduled_by: _Optional[_Iterable[_Union[ScheduledBy, str]]] = ..., dag_run_id: _Optional[str] = ..., map_index: _Optional[int] = ..., **kwargs) -> None: ...

class GetApplicationRunRequest(_message.Message):
    __slots__ = ("pod_id", "environment_id", "project_id", "application_id")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    environment_id: str
    project_id: str
    application_id: str
    def __init__(self, pod_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., application_id: _Optional[str] = ...) -> None: ...

class ApplicationRuns(_message.Message):
    __slots__ = ("application_runs", "page", "visible_pages")
    APPLICATION_RUNS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_PAGES_FIELD_NUMBER: _ClassVar[int]
    application_runs: _containers.RepeatedCompositeFieldContainer[ApplicationRun]
    page: int
    visible_pages: int
    def __init__(self, application_runs: _Optional[_Iterable[_Union[ApplicationRun, _Mapping]]] = ..., page: _Optional[int] = ..., visible_pages: _Optional[int] = ...) -> None: ...

class PodResources(_message.Message):
    __slots__ = ("requests",)
    class Resources(_message.Message):
        __slots__ = ("cpu", "memory")
        CPU_FIELD_NUMBER: _ClassVar[int]
        MEMORY_FIELD_NUMBER: _ClassVar[int]
        cpu: int
        memory: int
        def __init__(self, cpu: _Optional[int] = ..., memory: _Optional[int] = ...) -> None: ...
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: PodResources.Resources
    def __init__(self, requests: _Optional[_Union[PodResources.Resources, _Mapping]] = ...) -> None: ...

class AirflowTaskDetails(_message.Message):
    __slots__ = ("dag_id", "task_id", "execution_timestamp", "data_interval_start", "data_interval_end", "dag_run_id", "try_number", "map_index")
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_START_FIELD_NUMBER: _ClassVar[int]
    DATA_INTERVAL_END_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TRY_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MAP_INDEX_FIELD_NUMBER: _ClassVar[int]
    dag_id: str
    task_id: str
    execution_timestamp: _timestamp_pb2.Timestamp
    data_interval_start: _timestamp_pb2.Timestamp
    data_interval_end: _timestamp_pb2.Timestamp
    dag_run_id: str
    try_number: int
    map_index: int
    def __init__(self, dag_id: _Optional[str] = ..., task_id: _Optional[str] = ..., execution_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., data_interval_start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., data_interval_end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., dag_run_id: _Optional[str] = ..., try_number: _Optional[int] = ..., map_index: _Optional[int] = ...) -> None: ...

class ApplicationRun(_message.Message):
    __slots__ = ("application_id", "pod_id", "build_id", "environment", "environment_id", "project_name", "project_id", "pod_name", "spark_app_id", "spark_history_enabled", "airflow_info", "manual_run_info", "phase", "type", "created", "started", "finished", "tenant_id", "cloud_node_id", "failure_reason", "podResources", "container_name", "container_id", "cluster_id", "scheduled_by", "operator_version", "instance_type", "instance_lifecycle", "spark_executor_instance_type", "spark_executor_instance_lifecycle", "region", "app_name", "cloud", "aws_role", "azure_application_client_id", "spark_history_eventlog_failure", "spark_mode", "submitter_state", "requested_number_of_executors", "container_image", "spark_metrics_processed")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    SPARK_HISTORY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_INFO_FIELD_NUMBER: _ClassVar[int]
    MANUAL_RUN_INFO_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLOUD_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    PODRESOURCES_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_BY_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTOR_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTOR_INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    SPARK_HISTORY_EVENTLOG_FAILURE_FIELD_NUMBER: _ClassVar[int]
    SPARK_MODE_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_STATE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_NUMBER_OF_EXECUTORS_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    SPARK_METRICS_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    pod_id: str
    build_id: str
    environment: str
    environment_id: str
    project_name: str
    project_id: str
    pod_name: str
    spark_app_id: str
    spark_history_enabled: bool
    airflow_info: AirflowTaskDetails
    manual_run_info: _common_pb2.ManualRunInfo
    phase: Phase
    type: DatafyApplicationType
    created: _timestamp_pb2.Timestamp
    started: _timestamp_pb2.Timestamp
    finished: _timestamp_pb2.Timestamp
    tenant_id: str
    cloud_node_id: str
    failure_reason: _common_pb2.PodFailureReason
    podResources: PodResources
    container_name: str
    container_id: str
    cluster_id: str
    scheduled_by: ScheduledBy
    operator_version: OperatorVersion
    instance_type: _common_pb2.DatafyInstanceType
    instance_lifecycle: _common_pb2.InstanceLifecycle
    spark_executor_instance_type: _common_pb2.DatafyInstanceType
    spark_executor_instance_lifecycle: _common_pb2.InstanceLifecycle
    region: str
    app_name: str
    cloud: _common_pb2.Cloud
    aws_role: str
    azure_application_client_id: str
    spark_history_eventlog_failure: SparkHistoryEventLogFailure
    spark_mode: SparkMode
    submitter_state: PodState
    requested_number_of_executors: int
    container_image: str
    spark_metrics_processed: bool
    def __init__(self, application_id: _Optional[str] = ..., pod_id: _Optional[str] = ..., build_id: _Optional[str] = ..., environment: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., pod_name: _Optional[str] = ..., spark_app_id: _Optional[str] = ..., spark_history_enabled: bool = ..., airflow_info: _Optional[_Union[AirflowTaskDetails, _Mapping]] = ..., manual_run_info: _Optional[_Union[_common_pb2.ManualRunInfo, _Mapping]] = ..., phase: _Optional[_Union[Phase, str]] = ..., type: _Optional[_Union[DatafyApplicationType, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., tenant_id: _Optional[str] = ..., cloud_node_id: _Optional[str] = ..., failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., podResources: _Optional[_Union[PodResources, _Mapping]] = ..., container_name: _Optional[str] = ..., container_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., scheduled_by: _Optional[_Union[ScheduledBy, str]] = ..., operator_version: _Optional[_Union[OperatorVersion, str]] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., spark_executor_instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., spark_executor_instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., region: _Optional[str] = ..., app_name: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., spark_history_eventlog_failure: _Optional[_Union[SparkHistoryEventLogFailure, str]] = ..., spark_mode: _Optional[_Union[SparkMode, str]] = ..., submitter_state: _Optional[_Union[PodState, _Mapping]] = ..., requested_number_of_executors: _Optional[int] = ..., container_image: _Optional[str] = ..., spark_metrics_processed: bool = ...) -> None: ...

class GetApplicationRunMetricsRequest(_message.Message):
    __slots__ = ("pod_id", "environment_id", "project_id", "application_id")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    environment_id: str
    project_id: str
    application_id: str
    def __init__(self, pod_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., application_id: _Optional[str] = ...) -> None: ...

class GetSparkEventLogUrlDataPlaneMetricsRequest(_message.Message):
    __slots__ = ("spark_app_id",)
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    spark_app_id: str
    def __init__(self, spark_app_id: _Optional[str] = ...) -> None: ...

class GetSparkEventLogUrlResponse(_message.Message):
    __slots__ = ("url", "spark_app_id")
    URL_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    url: str
    spark_app_id: str
    def __init__(self, url: _Optional[str] = ..., spark_app_id: _Optional[str] = ...) -> None: ...

class GetSparkEventLogUrlRequest(_message.Message):
    __slots__ = ("driver_pod_id", "environment_id", "project_id", "application_id")
    DRIVER_POD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    driver_pod_id: str
    environment_id: str
    project_id: str
    application_id: str
    def __init__(self, driver_pod_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., application_id: _Optional[str] = ...) -> None: ...

class GetApplicationRunLogsRequest(_message.Message):
    __slots__ = ("pod_id", "next_token", "start_from_head", "environment_id", "project_id", "filter_pattern", "pod_type", "application_id")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_FROM_HEAD_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FILTER_PATTERN_FIELD_NUMBER: _ClassVar[int]
    POD_TYPE_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    next_token: str
    start_from_head: bool
    environment_id: str
    project_id: str
    filter_pattern: str
    pod_type: ApplicationPodType
    application_id: str
    def __init__(self, pod_id: _Optional[str] = ..., next_token: _Optional[str] = ..., start_from_head: bool = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., filter_pattern: _Optional[str] = ..., pod_type: _Optional[_Union[ApplicationPodType, str]] = ..., application_id: _Optional[str] = ...) -> None: ...

class GetApplicationRunAnalyzedByAiByApplicationIdRequest(_message.Message):
    __slots__ = ("application_id", "environment_id", "project_id")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    environment_id: str
    project_id: str
    def __init__(self, application_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetApplicationRunAnalyzedByAiByApplicationIdResponse(_message.Message):
    __slots__ = ("analysis_result",)
    ANALYSIS_RESULT_FIELD_NUMBER: _ClassVar[int]
    analysis_result: str
    def __init__(self, analysis_result: _Optional[str] = ...) -> None: ...

class GetDownloadApplicationRunLogsByApplicationIdUrlRequest(_message.Message):
    __slots__ = ("application_id", "environment_id", "project_id", "pod_type")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    POD_TYPE_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    environment_id: str
    project_id: str
    pod_type: ApplicationPodType
    def __init__(self, application_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., pod_type: _Optional[_Union[ApplicationPodType, str]] = ...) -> None: ...

class GetDownloadApplicationRunLogsByApplicationIdUrlResponse(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class GetSparkExecutorLogsRequest(_message.Message):
    __slots__ = ("batch_application_id", "streaming_application_id", "executor_id", "next_token", "start_from_head", "environment_id", "project_id", "filter_pattern")
    class StreamingApplicationId(_message.Message):
        __slots__ = ("streaming_id", "id")
        STREAMING_ID_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        streaming_id: str
        id: str
        def __init__(self, streaming_id: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...
    BATCH_APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    STREAMING_APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_FROM_HEAD_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FILTER_PATTERN_FIELD_NUMBER: _ClassVar[int]
    batch_application_id: str
    streaming_application_id: GetSparkExecutorLogsRequest.StreamingApplicationId
    executor_id: str
    next_token: str
    start_from_head: bool
    environment_id: str
    project_id: str
    filter_pattern: str
    def __init__(self, batch_application_id: _Optional[str] = ..., streaming_application_id: _Optional[_Union[GetSparkExecutorLogsRequest.StreamingApplicationId, _Mapping]] = ..., executor_id: _Optional[str] = ..., next_token: _Optional[str] = ..., start_from_head: bool = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., filter_pattern: _Optional[str] = ...) -> None: ...

class GetApplicationRunLogsResponse(_message.Message):
    __slots__ = ("logs", "next_token", "previous_token")
    LOGS_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_common_pb2.Log]
    next_token: str
    previous_token: str
    def __init__(self, logs: _Optional[_Iterable[_Union[_common_pb2.Log, _Mapping]]] = ..., next_token: _Optional[str] = ..., previous_token: _Optional[str] = ...) -> None: ...

class GetSparkExecutorLogsResponse(_message.Message):
    __slots__ = ("logs", "next_token", "previous_token")
    LOGS_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_common_pb2.Log]
    next_token: str
    previous_token: str
    def __init__(self, logs: _Optional[_Iterable[_Union[_common_pb2.Log, _Mapping]]] = ..., next_token: _Optional[str] = ..., previous_token: _Optional[str] = ...) -> None: ...

class GetApplicationRunDataPlaneLogsRequest(_message.Message):
    __slots__ = ("pod_name", "container_name", "container_id", "namespace", "next_token", "start_from_head", "start_timestamp", "end_timestamp", "filter_pattern")
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_FROM_HEAD_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FILTER_PATTERN_FIELD_NUMBER: _ClassVar[int]
    pod_name: str
    container_name: str
    container_id: str
    namespace: str
    next_token: str
    start_from_head: bool
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    filter_pattern: str
    def __init__(self, pod_name: _Optional[str] = ..., container_name: _Optional[str] = ..., container_id: _Optional[str] = ..., namespace: _Optional[str] = ..., next_token: _Optional[str] = ..., start_from_head: bool = ..., start_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., filter_pattern: _Optional[str] = ...) -> None: ...

class GetLatestDataPlaneLogsRequest(_message.Message):
    __slots__ = ("pod_name", "container_name", "container_id", "namespace", "start_timestamp", "end_timestamp", "filter_pattern", "limit")
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FILTER_PATTERN_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    pod_name: str
    container_name: str
    container_id: str
    namespace: str
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    filter_pattern: str
    limit: int
    def __init__(self, pod_name: _Optional[str] = ..., container_name: _Optional[str] = ..., container_id: _Optional[str] = ..., namespace: _Optional[str] = ..., start_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., filter_pattern: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class DownloadApplicationRunDataPlaneLogsRequest(_message.Message):
    __slots__ = ("pod_name", "container_name", "container_id", "namespace", "start_timestamp", "end_timestamp")
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    pod_name: str
    container_name: str
    container_id: str
    namespace: str
    start_timestamp: _timestamp_pb2.Timestamp
    end_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, pod_name: _Optional[str] = ..., container_name: _Optional[str] = ..., container_id: _Optional[str] = ..., namespace: _Optional[str] = ..., start_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetApplicationRunDataPlaneLogsResponse(_message.Message):
    __slots__ = ("logs", "next_token", "previous_token")
    LOGS_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_common_pb2.Log]
    next_token: str
    previous_token: str
    def __init__(self, logs: _Optional[_Iterable[_Union[_common_pb2.Log, _Mapping]]] = ..., next_token: _Optional[str] = ..., previous_token: _Optional[str] = ...) -> None: ...

class GetLatestDataPlaneLogsResponse(_message.Message):
    __slots__ = ("logs",)
    LOGS_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_common_pb2.Log]
    def __init__(self, logs: _Optional[_Iterable[_Union[_common_pb2.Log, _Mapping]]] = ...) -> None: ...

class GetApplicationRunDataPlaneMetricsRequest(_message.Message):
    __slots__ = ("pod_name", "pod_id", "environment", "container_name", "start_date", "end_date")
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    pod_name: str
    pod_id: str
    environment: str
    container_name: str
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    def __init__(self, pod_name: _Optional[str] = ..., pod_id: _Optional[str] = ..., environment: _Optional[str] = ..., container_name: _Optional[str] = ..., start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetApplicationRunDataPlaneMetricsResponse(_message.Message):
    __slots__ = ("start_date", "end_date", "cpu_metrics", "memory_metrics", "interval")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    CPU_METRICS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_METRICS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    cpu_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    memory_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    interval: int
    def __init__(self, start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cpu_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., memory_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., interval: _Optional[int] = ...) -> None: ...

class Metric(_message.Message):
    __slots__ = ("timestamp", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: float
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class SparkExecutorMetrics(_message.Message):
    __slots__ = ("pod_id", "pod_name", "cpu_metrics", "memory_metrics", "executor_id", "cpu_max", "memory_max")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    CPU_METRICS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_METRICS_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CPU_MAX_FIELD_NUMBER: _ClassVar[int]
    MEMORY_MAX_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    pod_name: str
    cpu_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    memory_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    executor_id: str
    cpu_max: int
    memory_max: int
    def __init__(self, pod_id: _Optional[str] = ..., pod_name: _Optional[str] = ..., cpu_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., memory_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., executor_id: _Optional[str] = ..., cpu_max: _Optional[int] = ..., memory_max: _Optional[int] = ...) -> None: ...

class GetApplicationRunMetricsResponse(_message.Message):
    __slots__ = ("start_date", "end_date", "cpu_metrics", "memory_metrics", "cpu_max", "memory_max", "interval", "spark_executor_metrics")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    CPU_METRICS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_METRICS_FIELD_NUMBER: _ClassVar[int]
    CPU_MAX_FIELD_NUMBER: _ClassVar[int]
    MEMORY_MAX_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTOR_METRICS_FIELD_NUMBER: _ClassVar[int]
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    cpu_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    memory_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    cpu_max: int
    memory_max: int
    interval: int
    spark_executor_metrics: _containers.RepeatedCompositeFieldContainer[SparkExecutorMetrics]
    def __init__(self, start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cpu_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., memory_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., cpu_max: _Optional[int] = ..., memory_max: _Optional[int] = ..., interval: _Optional[int] = ..., spark_executor_metrics: _Optional[_Iterable[_Union[SparkExecutorMetrics, _Mapping]]] = ...) -> None: ...

class SparkExecutor(_message.Message):
    __slots__ = ("pod_id", "pod_name", "environment", "spark_app_id", "application_id", "phase", "created", "started", "finished", "failure_reason", "tenant_id", "cloud_node_id", "podResources", "executor_id", "container_name", "container_id", "cluster_id")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLOUD_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    PODRESOURCES_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    pod_name: str
    environment: str
    spark_app_id: str
    application_id: str
    phase: Phase
    created: _timestamp_pb2.Timestamp
    started: _timestamp_pb2.Timestamp
    finished: _timestamp_pb2.Timestamp
    failure_reason: _common_pb2.PodFailureReason
    tenant_id: str
    cloud_node_id: str
    podResources: PodResources
    executor_id: str
    container_name: str
    container_id: str
    cluster_id: str
    def __init__(self, pod_id: _Optional[str] = ..., pod_name: _Optional[str] = ..., environment: _Optional[str] = ..., spark_app_id: _Optional[str] = ..., application_id: _Optional[str] = ..., phase: _Optional[_Union[Phase, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., tenant_id: _Optional[str] = ..., cloud_node_id: _Optional[str] = ..., podResources: _Optional[_Union[PodResources, _Mapping]] = ..., executor_id: _Optional[str] = ..., container_name: _Optional[str] = ..., container_id: _Optional[str] = ..., cluster_id: _Optional[str] = ...) -> None: ...

class GetSparkExecutorInfoRequest(_message.Message):
    __slots__ = ("driver_pod_id", "environment_id", "project_id", "application_id")
    DRIVER_POD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    driver_pod_id: str
    environment_id: str
    project_id: str
    application_id: str
    def __init__(self, driver_pod_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., application_id: _Optional[str] = ...) -> None: ...

class GetSparkExecutorInfoRequestResponse(_message.Message):
    __slots__ = ("executors",)
    EXECUTORS_FIELD_NUMBER: _ClassVar[int]
    executors: _containers.RepeatedCompositeFieldContainer[SparkExecutor]
    def __init__(self, executors: _Optional[_Iterable[_Union[SparkExecutor, _Mapping]]] = ...) -> None: ...

class GetSparkExecutorMetricsRequest(_message.Message):
    __slots__ = ("driver_pod_id", "environment_id", "project_id")
    DRIVER_POD_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    driver_pod_id: str
    environment_id: str
    project_id: str
    def __init__(self, driver_pod_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetSparkExecutorMetricsResponse(_message.Message):
    __slots__ = ("start_date", "end_date", "spark_executor_metrics", "interval")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTOR_METRICS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    spark_executor_metrics: _containers.RepeatedCompositeFieldContainer[SparkExecutorMetrics]
    interval: int
    def __init__(self, start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., spark_executor_metrics: _Optional[_Iterable[_Union[SparkExecutorMetrics, _Mapping]]] = ..., interval: _Optional[int] = ...) -> None: ...

class GetSparkExecutorRunDataPlaneMetricsRequest(_message.Message):
    __slots__ = ("pod_names", "pod_ids", "container_names", "environment", "start_date", "end_date")
    POD_NAMES_FIELD_NUMBER: _ClassVar[int]
    POD_IDS_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAMES_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    pod_names: _containers.RepeatedScalarFieldContainer[str]
    pod_ids: _containers.RepeatedScalarFieldContainer[str]
    container_names: _containers.RepeatedScalarFieldContainer[str]
    environment: str
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    def __init__(self, pod_names: _Optional[_Iterable[str]] = ..., pod_ids: _Optional[_Iterable[str]] = ..., container_names: _Optional[_Iterable[str]] = ..., environment: _Optional[str] = ..., start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetSparkExecutorDataPlaneMetricsResponse(_message.Message):
    __slots__ = ("start_date", "end_date", "spark_executor_metrics", "interval")
    class SparkExecutorMetrics(_message.Message):
        __slots__ = ("pod_id", "cpu_metrics", "memory_metrics")
        POD_ID_FIELD_NUMBER: _ClassVar[int]
        CPU_METRICS_FIELD_NUMBER: _ClassVar[int]
        MEMORY_METRICS_FIELD_NUMBER: _ClassVar[int]
        pod_id: str
        cpu_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
        memory_metrics: _containers.RepeatedCompositeFieldContainer[Metric]
        def __init__(self, pod_id: _Optional[str] = ..., cpu_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., memory_metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ...) -> None: ...
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTOR_METRICS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    spark_executor_metrics: _containers.RepeatedCompositeFieldContainer[GetSparkExecutorDataPlaneMetricsResponse.SparkExecutorMetrics]
    interval: int
    def __init__(self, start_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., spark_executor_metrics: _Optional[_Iterable[_Union[GetSparkExecutorDataPlaneMetricsResponse.SparkExecutorMetrics, _Mapping]]] = ..., interval: _Optional[int] = ...) -> None: ...

class GetStreamingApplicationsRequest(_message.Message):
    __slots__ = ("environment_name", "project_name", "environment_id", "project_id")
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_name: str
    project_name: str
    environment_id: str
    project_id: str
    def __init__(self, environment_name: _Optional[str] = ..., project_name: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetStreamingApplicationsResponse(_message.Message):
    __slots__ = ("streaming_applications",)
    STREAMING_APPLICATIONS_FIELD_NUMBER: _ClassVar[int]
    streaming_applications: _containers.RepeatedCompositeFieldContainer[StreamingApplication]
    def __init__(self, streaming_applications: _Optional[_Iterable[_Union[StreamingApplication, _Mapping]]] = ...) -> None: ...

class StreamingApplication(_message.Message):
    __slots__ = ("id", "name", "tenant_id", "cluster_id", "environment_name", "environment_id", "project_name", "project_id", "created", "deleted", "restarts_last_window", "alerting")
    class Alerting(_message.Message):
        __slots__ = ("enabled", "emails", "restarts_threshold", "restarts_window", "restarts_alert_cool_down")
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        EMAILS_FIELD_NUMBER: _ClassVar[int]
        RESTARTS_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
        RESTARTS_WINDOW_FIELD_NUMBER: _ClassVar[int]
        RESTARTS_ALERT_COOL_DOWN_FIELD_NUMBER: _ClassVar[int]
        enabled: bool
        emails: _containers.RepeatedScalarFieldContainer[str]
        restarts_threshold: int
        restarts_window: str
        restarts_alert_cool_down: str
        def __init__(self, enabled: bool = ..., emails: _Optional[_Iterable[str]] = ..., restarts_threshold: _Optional[int] = ..., restarts_window: _Optional[str] = ..., restarts_alert_cool_down: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    RESTARTS_LAST_WINDOW_FIELD_NUMBER: _ClassVar[int]
    ALERTING_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    tenant_id: str
    cluster_id: str
    environment_name: str
    environment_id: str
    project_name: str
    project_id: str
    created: _timestamp_pb2.Timestamp
    deleted: _timestamp_pb2.Timestamp
    restarts_last_window: int
    alerting: StreamingApplication.Alerting
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., tenant_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., deleted: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., restarts_last_window: _Optional[int] = ..., alerting: _Optional[_Union[StreamingApplication.Alerting, _Mapping]] = ...) -> None: ...

class GetStreamingApplicationRequest(_message.Message):
    __slots__ = ("id", "environment_id", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    environment_id: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class PodState(_message.Message):
    __slots__ = ("pod_id", "pod_name", "container_id", "container_name", "phase", "pod_failure_reason", "created", "started", "finished", "cloud_node_id")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    POD_FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    CLOUD_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    pod_name: str
    container_id: str
    container_name: str
    phase: Phase
    pod_failure_reason: _common_pb2.PodFailureReason
    created: _timestamp_pb2.Timestamp
    started: _timestamp_pb2.Timestamp
    finished: _timestamp_pb2.Timestamp
    cloud_node_id: str
    def __init__(self, pod_id: _Optional[str] = ..., pod_name: _Optional[str] = ..., container_id: _Optional[str] = ..., container_name: _Optional[str] = ..., phase: _Optional[_Union[Phase, str]] = ..., pod_failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cloud_node_id: _Optional[str] = ...) -> None: ...

class SparkPodState(_message.Message):
    __slots__ = ("pod_id", "pod_name", "container_id", "container_name", "phase", "pod_failure_reason", "created", "started", "finished", "cloud_node_id", "executor_id")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    POD_FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    CLOUD_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    pod_name: str
    container_id: str
    container_name: str
    phase: Phase
    pod_failure_reason: _common_pb2.PodFailureReason
    created: _timestamp_pb2.Timestamp
    started: _timestamp_pb2.Timestamp
    finished: _timestamp_pb2.Timestamp
    cloud_node_id: str
    executor_id: str
    def __init__(self, pod_id: _Optional[str] = ..., pod_name: _Optional[str] = ..., container_id: _Optional[str] = ..., container_name: _Optional[str] = ..., phase: _Optional[_Union[Phase, str]] = ..., pod_failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cloud_node_id: _Optional[str] = ..., executor_id: _Optional[str] = ...) -> None: ...

class SparkApplication(_message.Message):
    __slots__ = ("id", "streaming_id", "tenant_id", "cluster_id", "environment_name", "status", "created", "spark_app_id", "submitter_state", "driver_state", "environment_id", "project_id", "aws_role", "azure_application_client_id", "instance_type", "instance_lifecycle", "executor_instance_type", "executor_instance_lifecycle", "requested_number_of_executors")
    ID_FIELD_NUMBER: _ClassVar[int]
    STREAMING_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_STATE_FIELD_NUMBER: _ClassVar[int]
    DRIVER_STATE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_NUMBER_OF_EXECUTORS_FIELD_NUMBER: _ClassVar[int]
    id: str
    streaming_id: str
    tenant_id: str
    cluster_id: str
    environment_name: str
    status: SparkStatus
    created: _timestamp_pb2.Timestamp
    spark_app_id: str
    submitter_state: PodState
    driver_state: PodState
    environment_id: str
    project_id: str
    aws_role: str
    azure_application_client_id: str
    instance_type: _common_pb2.DatafyInstanceType
    instance_lifecycle: _common_pb2.InstanceLifecycle
    executor_instance_type: _common_pb2.DatafyInstanceType
    executor_instance_lifecycle: _common_pb2.InstanceLifecycle
    requested_number_of_executors: int
    def __init__(self, id: _Optional[str] = ..., streaming_id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., status: _Optional[_Union[SparkStatus, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., spark_app_id: _Optional[str] = ..., submitter_state: _Optional[_Union[PodState, _Mapping]] = ..., driver_state: _Optional[_Union[PodState, _Mapping]] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., executor_instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., executor_instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., requested_number_of_executors: _Optional[int] = ...) -> None: ...

class SparkApplicationEvent(_message.Message):
    __slots__ = ("id", "streaming_id", "tenant_id", "cluster_id", "status", "created", "spark_app_id", "scheduled_by", "airflow_info", "manual_run_info", "driver_instance_lifecycle", "executor_instance_lifecycle", "region", "mode", "container_image", "submitter_state", "driver_state", "environment_id", "environment_name", "project_id", "project_name", "build_id", "driver_instance_type", "executor_instance_type", "spark_executors_state", "requested_number_of_executors", "app_name", "cloud", "aws_role", "azure_application_client_id", "spark_history_event_log_failure")
    ID_FIELD_NUMBER: _ClassVar[int]
    STREAMING_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_BY_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_INFO_FIELD_NUMBER: _ClassVar[int]
    MANUAL_RUN_INFO_FIELD_NUMBER: _ClassVar[int]
    DRIVER_INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    SUBMITTER_STATE_FIELD_NUMBER: _ClassVar[int]
    DRIVER_STATE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVER_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXECUTOR_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTORS_STATE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_NUMBER_OF_EXECUTORS_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    SPARK_HISTORY_EVENT_LOG_FAILURE_FIELD_NUMBER: _ClassVar[int]
    id: str
    streaming_id: str
    tenant_id: str
    cluster_id: str
    status: SparkStatus
    created: _timestamp_pb2.Timestamp
    spark_app_id: str
    scheduled_by: ScheduledBy
    airflow_info: AirflowTaskDetails
    manual_run_info: _common_pb2.ManualRunInfo
    driver_instance_lifecycle: _common_pb2.InstanceLifecycle
    executor_instance_lifecycle: _common_pb2.InstanceLifecycle
    region: str
    mode: SparkMode
    container_image: str
    submitter_state: PodState
    driver_state: PodState
    environment_id: str
    environment_name: str
    project_id: str
    project_name: str
    build_id: str
    driver_instance_type: _common_pb2.DatafyInstanceType
    executor_instance_type: _common_pb2.DatafyInstanceType
    spark_executors_state: _containers.RepeatedCompositeFieldContainer[SparkPodState]
    requested_number_of_executors: int
    app_name: str
    cloud: _common_pb2.Cloud
    aws_role: str
    azure_application_client_id: str
    spark_history_event_log_failure: SparkHistoryEventLogFailure
    def __init__(self, id: _Optional[str] = ..., streaming_id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., status: _Optional[_Union[SparkStatus, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., spark_app_id: _Optional[str] = ..., scheduled_by: _Optional[_Union[ScheduledBy, str]] = ..., airflow_info: _Optional[_Union[AirflowTaskDetails, _Mapping]] = ..., manual_run_info: _Optional[_Union[_common_pb2.ManualRunInfo, _Mapping]] = ..., driver_instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., executor_instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., region: _Optional[str] = ..., mode: _Optional[_Union[SparkMode, str]] = ..., container_image: _Optional[str] = ..., submitter_state: _Optional[_Union[PodState, _Mapping]] = ..., driver_state: _Optional[_Union[PodState, _Mapping]] = ..., environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., project_id: _Optional[str] = ..., project_name: _Optional[str] = ..., build_id: _Optional[str] = ..., driver_instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., executor_instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., spark_executors_state: _Optional[_Iterable[_Union[SparkPodState, _Mapping]]] = ..., requested_number_of_executors: _Optional[int] = ..., app_name: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., spark_history_event_log_failure: _Optional[_Union[SparkHistoryEventLogFailure, str]] = ...) -> None: ...

class ContainerApplicationEvent(_message.Message):
    __slots__ = ("pod_id", "application_id", "tenant_id", "cluster_id", "environment_name", "environment_id", "project_name", "project_id", "build_id", "created", "started", "finished", "instance_type", "container_id", "container_name", "phase", "pod_failure_reason", "cloud_node_id", "scheduled_by", "airflow_info", "manual_run_info", "pod_name", "instance_lifecycle", "region", "app_name", "cloud", "taskType", "aws_role", "azure_application_client_id", "container_image")
    POD_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    POD_FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    CLOUD_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_BY_FIELD_NUMBER: _ClassVar[int]
    AIRFLOW_INFO_FIELD_NUMBER: _ClassVar[int]
    MANUAL_RUN_INFO_FIELD_NUMBER: _ClassVar[int]
    POD_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    TASKTYPE_FIELD_NUMBER: _ClassVar[int]
    AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
    AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    pod_id: str
    application_id: str
    tenant_id: str
    cluster_id: str
    environment_name: str
    environment_id: str
    project_name: str
    project_id: str
    build_id: str
    created: _timestamp_pb2.Timestamp
    started: _timestamp_pb2.Timestamp
    finished: _timestamp_pb2.Timestamp
    instance_type: _common_pb2.DatafyInstanceType
    container_id: str
    container_name: str
    phase: Phase
    pod_failure_reason: _common_pb2.PodFailureReason
    cloud_node_id: str
    scheduled_by: ScheduledBy
    airflow_info: AirflowTaskDetails
    manual_run_info: _common_pb2.ManualRunInfo
    pod_name: str
    instance_lifecycle: _common_pb2.InstanceLifecycle
    region: str
    app_name: str
    cloud: _common_pb2.Cloud
    taskType: DatafyApplicationType
    aws_role: str
    azure_application_client_id: str
    container_image: str
    def __init__(self, pod_id: _Optional[str] = ..., application_id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., build_id: _Optional[str] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., container_id: _Optional[str] = ..., container_name: _Optional[str] = ..., phase: _Optional[_Union[Phase, str]] = ..., pod_failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., cloud_node_id: _Optional[str] = ..., scheduled_by: _Optional[_Union[ScheduledBy, str]] = ..., airflow_info: _Optional[_Union[AirflowTaskDetails, _Mapping]] = ..., manual_run_info: _Optional[_Union[_common_pb2.ManualRunInfo, _Mapping]] = ..., pod_name: _Optional[str] = ..., instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., region: _Optional[str] = ..., app_name: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., taskType: _Optional[_Union[DatafyApplicationType, str]] = ..., aws_role: _Optional[str] = ..., azure_application_client_id: _Optional[str] = ..., container_image: _Optional[str] = ...) -> None: ...

class GetStreamingSparkApplicationRunsRequest(_message.Message):
    __slots__ = ("id", "limit", "page", "environment_id", "project_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    limit: int
    page: int
    environment_id: str
    project_id: str
    def __init__(self, id: _Optional[str] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetStreamingSparkApplicationRunsResponse(_message.Message):
    __slots__ = ("spark_applications", "visible_pages")
    SPARK_APPLICATIONS_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_PAGES_FIELD_NUMBER: _ClassVar[int]
    spark_applications: _containers.RepeatedCompositeFieldContainer[SparkApplication]
    visible_pages: int
    def __init__(self, spark_applications: _Optional[_Iterable[_Union[SparkApplication, _Mapping]]] = ..., visible_pages: _Optional[int] = ...) -> None: ...

class GetStreamingSparkApplicationLogsRequest(_message.Message):
    __slots__ = ("streaming_id", "id", "environment_id", "project_id", "next_token", "start_from_head", "filter_pattern", "pod_type")
    STREAMING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_FROM_HEAD_FIELD_NUMBER: _ClassVar[int]
    FILTER_PATTERN_FIELD_NUMBER: _ClassVar[int]
    POD_TYPE_FIELD_NUMBER: _ClassVar[int]
    streaming_id: str
    id: str
    environment_id: str
    project_id: str
    next_token: str
    start_from_head: bool
    filter_pattern: str
    pod_type: ApplicationPodType
    def __init__(self, streaming_id: _Optional[str] = ..., id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., next_token: _Optional[str] = ..., start_from_head: bool = ..., filter_pattern: _Optional[str] = ..., pod_type: _Optional[_Union[ApplicationPodType, str]] = ...) -> None: ...

class GetStreamingSparkApplicationLogsResponse(_message.Message):
    __slots__ = ("logs", "next_token", "previous_token")
    LOGS_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[_common_pb2.Log]
    next_token: str
    previous_token: str
    def __init__(self, logs: _Optional[_Iterable[_Union[_common_pb2.Log, _Mapping]]] = ..., next_token: _Optional[str] = ..., previous_token: _Optional[str] = ...) -> None: ...

class GetStreamingSparkApplicationRunExecutorRequest(_message.Message):
    __slots__ = ("streaming_id", "id", "environment_id", "project_id")
    STREAMING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    streaming_id: str
    id: str
    environment_id: str
    project_id: str
    def __init__(self, streaming_id: _Optional[str] = ..., id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetStreamingSparkApplicationRunExecutorResponse(_message.Message):
    __slots__ = ("spark_executors",)
    class SparkExecutor(_message.Message):
        __slots__ = ("pod_state", "executor_id")
        POD_STATE_FIELD_NUMBER: _ClassVar[int]
        EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
        pod_state: PodState
        executor_id: str
        def __init__(self, pod_state: _Optional[_Union[PodState, _Mapping]] = ..., executor_id: _Optional[str] = ...) -> None: ...
    SPARK_EXECUTORS_FIELD_NUMBER: _ClassVar[int]
    spark_executors: _containers.RepeatedCompositeFieldContainer[GetStreamingSparkApplicationRunExecutorResponse.SparkExecutor]
    def __init__(self, spark_executors: _Optional[_Iterable[_Union[GetStreamingSparkApplicationRunExecutorResponse.SparkExecutor, _Mapping]]] = ...) -> None: ...

class GetStreamingSparkApplicationRunMetricsRequest(_message.Message):
    __slots__ = ("streaming_id", "id", "environment_id", "project_id", "start", "end")
    STREAMING_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    streaming_id: str
    id: str
    environment_id: str
    project_id: str
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    def __init__(self, streaming_id: _Optional[str] = ..., id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CalculateSparkMetricDataPlaneRequest(_message.Message):
    __slots__ = ("application_id", "environment_id", "project_id", "task_id", "dag_id", "build_id", "spark_app_id", "finished_epoch_seconds")
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    SPARK_APP_ID_FIELD_NUMBER: _ClassVar[int]
    FINISHED_EPOCH_SECONDS_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    environment_id: str
    project_id: str
    task_id: str
    dag_id: str
    build_id: str
    spark_app_id: str
    finished_epoch_seconds: int
    def __init__(self, application_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., task_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., build_id: _Optional[str] = ..., spark_app_id: _Optional[str] = ..., finished_epoch_seconds: _Optional[int] = ...) -> None: ...

class ProcessSparkMetricsRequest(_message.Message):
    __slots__ = ("application_run_info_list_url", "signed_headers")
    class SignedHeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    APPLICATION_RUN_INFO_LIST_URL_FIELD_NUMBER: _ClassVar[int]
    SIGNED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    application_run_info_list_url: str
    signed_headers: _containers.ScalarMap[str, str]
    def __init__(self, application_run_info_list_url: _Optional[str] = ..., signed_headers: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ProcessSparkMetricsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCostsForProjectRequest(_message.Message):
    __slots__ = ("project_id", "range")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    range: CostRange
    def __init__(self, project_id: _Optional[str] = ..., range: _Optional[_Union[CostRange, str]] = ...) -> None: ...

class DailyCost(_message.Message):
    __slots__ = ("date", "allocated", "batch", "streaming", "clusterOverhead", "ide", "other")
    DATE_FIELD_NUMBER: _ClassVar[int]
    ALLOCATED_FIELD_NUMBER: _ClassVar[int]
    BATCH_FIELD_NUMBER: _ClassVar[int]
    STREAMING_FIELD_NUMBER: _ClassVar[int]
    CLUSTEROVERHEAD_FIELD_NUMBER: _ClassVar[int]
    IDE_FIELD_NUMBER: _ClassVar[int]
    OTHER_FIELD_NUMBER: _ClassVar[int]
    date: _timestamp_pb2.Timestamp
    allocated: float
    batch: float
    streaming: float
    clusterOverhead: float
    ide: float
    other: float
    def __init__(self, date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., allocated: _Optional[float] = ..., batch: _Optional[float] = ..., streaming: _Optional[float] = ..., clusterOverhead: _Optional[float] = ..., ide: _Optional[float] = ..., other: _Optional[float] = ...) -> None: ...

class GetCostsForProjectResponse(_message.Message):
    __slots__ = ("costs",)
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[DailyCost]
    def __init__(self, costs: _Optional[_Iterable[_Union[DailyCost, _Mapping]]] = ...) -> None: ...

class GetCostsForEnvironmentRequest(_message.Message):
    __slots__ = ("environment_id", "range")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    range: CostRange
    def __init__(self, environment_id: _Optional[str] = ..., range: _Optional[_Union[CostRange, str]] = ...) -> None: ...

class GetCostsForEnvironmentResponse(_message.Message):
    __slots__ = ("costs",)
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[DailyCost]
    def __init__(self, costs: _Optional[_Iterable[_Union[DailyCost, _Mapping]]] = ...) -> None: ...

class GetGlobalCostsPerDayRequest(_message.Message):
    __slots__ = ("range",)
    RANGE_FIELD_NUMBER: _ClassVar[int]
    range: CostRange
    def __init__(self, range: _Optional[_Union[CostRange, str]] = ...) -> None: ...

class GetGlobalCostsPerDayResponse(_message.Message):
    __slots__ = ("costs",)
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[DailyCost]
    def __init__(self, costs: _Optional[_Iterable[_Union[DailyCost, _Mapping]]] = ...) -> None: ...

class GetTopMostExpensiveProjectsRequest(_message.Message):
    __slots__ = ("range",)
    RANGE_FIELD_NUMBER: _ClassVar[int]
    range: CostRange
    def __init__(self, range: _Optional[_Union[CostRange, str]] = ...) -> None: ...

class GetTopMostExpensiveProjectsResponse(_message.Message):
    __slots__ = ("costs",)
    class Cost(_message.Message):
        __slots__ = ("project_name", "project_id", "current_allocated_cost", "previous_allocated_cost")
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        CURRENT_ALLOCATED_COST_FIELD_NUMBER: _ClassVar[int]
        PREVIOUS_ALLOCATED_COST_FIELD_NUMBER: _ClassVar[int]
        project_name: str
        project_id: str
        current_allocated_cost: float
        previous_allocated_cost: float
        def __init__(self, project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., current_allocated_cost: _Optional[float] = ..., previous_allocated_cost: _Optional[float] = ...) -> None: ...
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[GetTopMostExpensiveProjectsResponse.Cost]
    def __init__(self, costs: _Optional[_Iterable[_Union[GetTopMostExpensiveProjectsResponse.Cost, _Mapping]]] = ...) -> None: ...

class GetTopMostExpensiveEnvironmentsRequest(_message.Message):
    __slots__ = ("range",)
    RANGE_FIELD_NUMBER: _ClassVar[int]
    range: CostRange
    def __init__(self, range: _Optional[_Union[CostRange, str]] = ...) -> None: ...

class GetTopMostExpensiveEnvironmentsResponse(_message.Message):
    __slots__ = ("costs",)
    class Cost(_message.Message):
        __slots__ = ("environment_name", "environment_id", "current_allocated_cost", "previous_allocated_cost")
        ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
        ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
        CURRENT_ALLOCATED_COST_FIELD_NUMBER: _ClassVar[int]
        PREVIOUS_ALLOCATED_COST_FIELD_NUMBER: _ClassVar[int]
        environment_name: str
        environment_id: str
        current_allocated_cost: float
        previous_allocated_cost: float
        def __init__(self, environment_name: _Optional[str] = ..., environment_id: _Optional[str] = ..., current_allocated_cost: _Optional[float] = ..., previous_allocated_cost: _Optional[float] = ...) -> None: ...
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[GetTopMostExpensiveEnvironmentsResponse.Cost]
    def __init__(self, costs: _Optional[_Iterable[_Union[GetTopMostExpensiveEnvironmentsResponse.Cost, _Mapping]]] = ...) -> None: ...

class GetTopMostChangedProjectsRequest(_message.Message):
    __slots__ = ("range",)
    RANGE_FIELD_NUMBER: _ClassVar[int]
    range: CostRange
    def __init__(self, range: _Optional[_Union[CostRange, str]] = ...) -> None: ...

class GetTopMostChangedProjectsResponse(_message.Message):
    __slots__ = ("costs",)
    class Cost(_message.Message):
        __slots__ = ("project_name", "project_id", "previous_cost", "current_cost")
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
        PREVIOUS_COST_FIELD_NUMBER: _ClassVar[int]
        CURRENT_COST_FIELD_NUMBER: _ClassVar[int]
        project_name: str
        project_id: str
        previous_cost: float
        current_cost: float
        def __init__(self, project_name: _Optional[str] = ..., project_id: _Optional[str] = ..., previous_cost: _Optional[float] = ..., current_cost: _Optional[float] = ...) -> None: ...
    COSTS_FIELD_NUMBER: _ClassVar[int]
    costs: _containers.RepeatedCompositeFieldContainer[GetTopMostChangedProjectsResponse.Cost]
    def __init__(self, costs: _Optional[_Iterable[_Union[GetTopMostChangedProjectsResponse.Cost, _Mapping]]] = ...) -> None: ...

class NodeState(_message.Message):
    __slots__ = ("node_name", "node_id", "cloud_node_id", "instance_type", "cloud_instance_type", "instance_lifecycle", "phase", "created", "finished", "tenant_id", "failure_reason", "architecture", "cluster_id", "region", "availability_zone", "compute_type", "cloud", "node_type", "storage_type", "storage_size_bytes", "storage_iops")
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    CLOUD_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLOUD_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_ZONE_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLOUD_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    STORAGE_IOPS_FIELD_NUMBER: _ClassVar[int]
    node_name: str
    node_id: str
    cloud_node_id: str
    instance_type: _common_pb2.DatafyInstanceType
    cloud_instance_type: str
    instance_lifecycle: _common_pb2.InstanceLifecycle
    phase: NodePhase
    created: _timestamp_pb2.Timestamp
    finished: _timestamp_pb2.Timestamp
    tenant_id: str
    failure_reason: NodeFailureReason
    architecture: str
    cluster_id: str
    region: str
    availability_zone: str
    compute_type: str
    cloud: _common_pb2.Cloud
    node_type: _common_pb2.NodeType
    storage_type: str
    storage_size_bytes: int
    storage_iops: int
    def __init__(self, node_name: _Optional[str] = ..., node_id: _Optional[str] = ..., cloud_node_id: _Optional[str] = ..., instance_type: _Optional[_Union[_common_pb2.DatafyInstanceType, str]] = ..., cloud_instance_type: _Optional[str] = ..., instance_lifecycle: _Optional[_Union[_common_pb2.InstanceLifecycle, str]] = ..., phase: _Optional[_Union[NodePhase, str]] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., tenant_id: _Optional[str] = ..., failure_reason: _Optional[_Union[NodeFailureReason, str]] = ..., architecture: _Optional[str] = ..., cluster_id: _Optional[str] = ..., region: _Optional[str] = ..., availability_zone: _Optional[str] = ..., compute_type: _Optional[str] = ..., cloud: _Optional[_Union[_common_pb2.Cloud, str]] = ..., node_type: _Optional[_Union[_common_pb2.NodeType, str]] = ..., storage_type: _Optional[str] = ..., storage_size_bytes: _Optional[int] = ..., storage_iops: _Optional[int] = ...) -> None: ...

class GetRecentlyFailedTasksRequest(_message.Message):
    __slots__ = ("environment_id", "project_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class GetRecentlyFailedTasksResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[AirflowTaskInstanceWithRun]
    def __init__(self, tasks: _Optional[_Iterable[_Union[AirflowTaskInstanceWithRun, _Mapping]]] = ...) -> None: ...

class GetTasksForDagRunRequest(_message.Message):
    __slots__ = ("environment_id", "project_id", "dag_id", "dag_run_id", "task_id")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_ID_FIELD_NUMBER: _ClassVar[int]
    DAG_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    dag_id: str
    dag_run_id: str
    task_id: str
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., dag_id: _Optional[str] = ..., dag_run_id: _Optional[str] = ..., task_id: _Optional[str] = ...) -> None: ...

class AirflowTaskInstanceWithRun(_message.Message):
    __slots__ = ("task_instance", "last_run")
    TASK_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    LAST_RUN_FIELD_NUMBER: _ClassVar[int]
    task_instance: _common_pb2.AirflowTaskInstance
    last_run: ApplicationRun
    def __init__(self, task_instance: _Optional[_Union[_common_pb2.AirflowTaskInstance, _Mapping]] = ..., last_run: _Optional[_Union[ApplicationRun, _Mapping]] = ...) -> None: ...

class GetTasksForDagRunResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[AirflowTaskInstanceWithRun]
    def __init__(self, tasks: _Optional[_Iterable[_Union[AirflowTaskInstanceWithRun, _Mapping]]] = ...) -> None: ...
