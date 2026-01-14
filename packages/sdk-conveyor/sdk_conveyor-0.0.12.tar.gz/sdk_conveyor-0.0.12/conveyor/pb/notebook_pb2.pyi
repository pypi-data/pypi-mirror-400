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

class NotebookType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Python: _ClassVar[NotebookType]

class NotebookMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    web_ui: _ClassVar[NotebookMode]
    ide: _ClassVar[NotebookMode]

class NotebookState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NotebookState_Not_Ready: _ClassVar[NotebookState]
    NotebookState_Ready: _ClassVar[NotebookState]
    NotebookState_Deleted: _ClassVar[NotebookState]
    NotebookState_Stopped: _ClassVar[NotebookState]
    NotebookState_Failed: _ClassVar[NotebookState]
Python: NotebookType
web_ui: NotebookMode
ide: NotebookMode
NotebookState_Not_Ready: NotebookState
NotebookState_Ready: NotebookState
NotebookState_Deleted: NotebookState
NotebookState_Stopped: NotebookState
NotebookState_Failed: NotebookState

class NotebookSpec(_message.Message):
    __slots__ = ("id", "name", "owner", "project", "environment", "max_idle_time", "disk_size", "mode", "python_spec")
    class PythonSpec(_message.Message):
        __slots__ = ("image", "python_version", "command", "args", "aws_role", "instance_type", "instance_life_cycle", "env_variables", "azure_application_client_id")
        class EnvVariablesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: _common_pb2.EnvVarResolver
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.EnvVarResolver, _Mapping]] = ...) -> None: ...
        IMAGE_FIELD_NUMBER: _ClassVar[int]
        PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
        COMMAND_FIELD_NUMBER: _ClassVar[int]
        ARGS_FIELD_NUMBER: _ClassVar[int]
        AWS_ROLE_FIELD_NUMBER: _ClassVar[int]
        INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
        INSTANCE_LIFE_CYCLE_FIELD_NUMBER: _ClassVar[int]
        ENV_VARIABLES_FIELD_NUMBER: _ClassVar[int]
        AZURE_APPLICATION_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
        image: str
        python_version: str
        command: _containers.RepeatedScalarFieldContainer[str]
        args: _containers.RepeatedScalarFieldContainer[str]
        aws_role: str
        instance_type: str
        instance_life_cycle: str
        env_variables: _containers.MessageMap[str, _common_pb2.EnvVarResolver]
        azure_application_client_id: str
        def __init__(self, image: _Optional[str] = ..., python_version: _Optional[str] = ..., command: _Optional[_Iterable[str]] = ..., args: _Optional[_Iterable[str]] = ..., aws_role: _Optional[str] = ..., instance_type: _Optional[str] = ..., instance_life_cycle: _Optional[str] = ..., env_variables: _Optional[_Mapping[str, _common_pb2.EnvVarResolver]] = ..., azure_application_client_id: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    MAX_IDLE_TIME_FIELD_NUMBER: _ClassVar[int]
    DISK_SIZE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    PYTHON_SPEC_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    owner: str
    project: str
    environment: str
    max_idle_time: int
    disk_size: int
    mode: NotebookMode
    python_spec: NotebookSpec.PythonSpec
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., owner: _Optional[str] = ..., project: _Optional[str] = ..., environment: _Optional[str] = ..., max_idle_time: _Optional[int] = ..., disk_size: _Optional[int] = ..., mode: _Optional[_Union[NotebookMode, str]] = ..., python_spec: _Optional[_Union[NotebookSpec.PythonSpec, _Mapping]] = ...) -> None: ...

class CreateNotebookDataPlaneRequest(_message.Message):
    __slots__ = ("spec",)
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: NotebookSpec
    def __init__(self, spec: _Optional[_Union[NotebookSpec, _Mapping]] = ...) -> None: ...

class CreateNotebookDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteNotebookDataPlaneRequest(_message.Message):
    __slots__ = ("name", "environment", "project", "owner")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    name: str
    environment: str
    project: str
    owner: str
    def __init__(self, name: _Optional[str] = ..., environment: _Optional[str] = ..., project: _Optional[str] = ..., owner: _Optional[str] = ...) -> None: ...

class StartNotebookDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StartNotebookDataPlaneRequest(_message.Message):
    __slots__ = ("name", "environment", "project", "owner")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    name: str
    environment: str
    project: str
    owner: str
    def __init__(self, name: _Optional[str] = ..., environment: _Optional[str] = ..., project: _Optional[str] = ..., owner: _Optional[str] = ...) -> None: ...

class StopNotebookDataPlaneResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StopNotebookDataPlaneRequest(_message.Message):
    __slots__ = ("name", "environment", "project", "owner")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    name: str
    environment: str
    project: str
    owner: str
    def __init__(self, name: _Optional[str] = ..., environment: _Optional[str] = ..., project: _Optional[str] = ..., owner: _Optional[str] = ...) -> None: ...

class DeleteNotebookDataPlaneResponse(_message.Message):
    __slots__ = ("not_found",)
    NOT_FOUND_FIELD_NUMBER: _ClassVar[int]
    not_found: bool
    def __init__(self, not_found: bool = ...) -> None: ...

class GetNotebookSpecDataPlaneRequest(_message.Message):
    __slots__ = ("name", "environment", "project", "owner")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    name: str
    environment: str
    project: str
    owner: str
    def __init__(self, name: _Optional[str] = ..., environment: _Optional[str] = ..., project: _Optional[str] = ..., owner: _Optional[str] = ...) -> None: ...

class GetNotebookSpecDataPlaneResponse(_message.Message):
    __slots__ = ("spec",)
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: NotebookSpec
    def __init__(self, spec: _Optional[_Union[NotebookSpec, _Mapping]] = ...) -> None: ...

class Notebook(_message.Message):
    __slots__ = ("id", "name", "state", "project", "project_id", "environment", "environment_id", "max_idle_time", "failure_reason", "not_ready_reason", "created_at", "idle_time_minutes", "owner", "state_message", "mode")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_IDLE_TIME_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    NOT_READY_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    state: NotebookState
    project: str
    project_id: str
    environment: str
    environment_id: str
    max_idle_time: int
    failure_reason: _common_pb2.PodFailureReason
    not_ready_reason: _common_pb2.NotReadyReason
    created_at: _timestamp_pb2.Timestamp
    idle_time_minutes: int
    owner: str
    state_message: str
    mode: NotebookMode
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., state: _Optional[_Union[NotebookState, str]] = ..., project: _Optional[str] = ..., project_id: _Optional[str] = ..., environment: _Optional[str] = ..., environment_id: _Optional[str] = ..., max_idle_time: _Optional[int] = ..., failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., not_ready_reason: _Optional[_Union[_common_pb2.NotReadyReason, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., idle_time_minutes: _Optional[int] = ..., owner: _Optional[str] = ..., state_message: _Optional[str] = ..., mode: _Optional[_Union[NotebookMode, str]] = ...) -> None: ...

class CreateNotebookRequest(_message.Message):
    __slots__ = ("spec", "project_id", "environment_id")
    SPEC_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    spec: NotebookSpec
    project_id: str
    environment_id: str
    def __init__(self, spec: _Optional[_Union[NotebookSpec, _Mapping]] = ..., project_id: _Optional[str] = ..., environment_id: _Optional[str] = ...) -> None: ...

class CreateNotebookResponse(_message.Message):
    __slots__ = ("notebook_id", "owner", "environment_id", "project_id")
    NOTEBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    notebook_id: str
    owner: str
    environment_id: str
    project_id: str
    def __init__(self, notebook_id: _Optional[str] = ..., owner: _Optional[str] = ..., environment_id: _Optional[str] = ..., project_id: _Optional[str] = ...) -> None: ...

class DeleteNotebookRequest(_message.Message):
    __slots__ = ("notebook_id",)
    NOTEBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    notebook_id: str
    def __init__(self, notebook_id: _Optional[str] = ...) -> None: ...

class StartNotebookRequest(_message.Message):
    __slots__ = ("notebook_id",)
    NOTEBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    notebook_id: str
    def __init__(self, notebook_id: _Optional[str] = ...) -> None: ...

class StartNotebookResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StopNotebookRequest(_message.Message):
    __slots__ = ("notebook_id",)
    NOTEBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    notebook_id: str
    def __init__(self, notebook_id: _Optional[str] = ...) -> None: ...

class StopNotebookResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteNotebooksRequest(_message.Message):
    __slots__ = ("project", "environment")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    project: str
    environment: str
    def __init__(self, project: _Optional[str] = ..., environment: _Optional[str] = ...) -> None: ...

class DeleteNotebookResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteNotebooksResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNotebooksRequest(_message.Message):
    __slots__ = ("environment_id", "project_id", "owned")
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNED_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    project_id: str
    owned: bool
    def __init__(self, environment_id: _Optional[str] = ..., project_id: _Optional[str] = ..., owned: bool = ...) -> None: ...

class ListNotebooksResponse(_message.Message):
    __slots__ = ("notebooks",)
    NOTEBOOKS_FIELD_NUMBER: _ClassVar[int]
    notebooks: _containers.RepeatedCompositeFieldContainer[Notebook]
    def __init__(self, notebooks: _Optional[_Iterable[_Union[Notebook, _Mapping]]] = ...) -> None: ...

class FindNotebookRequest(_message.Message):
    __slots__ = ("notebook_id", "notebook_name", "project_id", "environment_id", "owner")
    NOTEBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOK_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    notebook_id: str
    notebook_name: str
    project_id: str
    environment_id: str
    owner: str
    def __init__(self, notebook_id: _Optional[str] = ..., notebook_name: _Optional[str] = ..., project_id: _Optional[str] = ..., environment_id: _Optional[str] = ..., owner: _Optional[str] = ...) -> None: ...

class FindNotebookResponse(_message.Message):
    __slots__ = ("spec", "state", "failure_reason", "not_ready_reason", "created_at", "idle_time_minutes")
    SPEC_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    NOT_READY_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    spec: NotebookSpec
    state: NotebookState
    failure_reason: _common_pb2.PodFailureReason
    not_ready_reason: _common_pb2.NotReadyReason
    created_at: _timestamp_pb2.Timestamp
    idle_time_minutes: int
    def __init__(self, spec: _Optional[_Union[NotebookSpec, _Mapping]] = ..., state: _Optional[_Union[NotebookState, str]] = ..., failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., not_ready_reason: _Optional[_Union[_common_pb2.NotReadyReason, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., idle_time_minutes: _Optional[int] = ...) -> None: ...

class ValidateNotebookRequest(_message.Message):
    __slots__ = ("spec",)
    SPEC_FIELD_NUMBER: _ClassVar[int]
    spec: NotebookSpec
    def __init__(self, spec: _Optional[_Union[NotebookSpec, _Mapping]] = ...) -> None: ...

class ValidateNotebookResult(_message.Message):
    __slots__ = ("valid", "errorList")
    class Error(_message.Message):
        __slots__ = ("detail",)
        DETAIL_FIELD_NUMBER: _ClassVar[int]
        detail: str
        def __init__(self, detail: _Optional[str] = ...) -> None: ...
    VALID_FIELD_NUMBER: _ClassVar[int]
    ERRORLIST_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    errorList: _containers.RepeatedCompositeFieldContainer[ValidateNotebookResult.Error]
    def __init__(self, valid: bool = ..., errorList: _Optional[_Iterable[_Union[ValidateNotebookResult.Error, _Mapping]]] = ...) -> None: ...

class GetNotebookBaseImageDockerCredentialsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNotebookBaseImageDockerCredentialsResponse(_message.Message):
    __slots__ = ("auth", "registry_url", "base_notebook_repo", "base_notebook_image_tag")
    AUTH_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_URL_FIELD_NUMBER: _ClassVar[int]
    BASE_NOTEBOOK_REPO_FIELD_NUMBER: _ClassVar[int]
    BASE_NOTEBOOK_IMAGE_TAG_FIELD_NUMBER: _ClassVar[int]
    auth: str
    registry_url: str
    base_notebook_repo: str
    base_notebook_image_tag: str
    def __init__(self, auth: _Optional[str] = ..., registry_url: _Optional[str] = ..., base_notebook_repo: _Optional[str] = ..., base_notebook_image_tag: _Optional[str] = ...) -> None: ...

class NotebookStateChangedEvent(_message.Message):
    __slots__ = ("tenant_id", "notebook_id", "state", "failure_reason", "not_ready_reason", "idle_time_minutes", "state_message", "image")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOK_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    NOT_READY_REASON_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    notebook_id: str
    state: NotebookState
    failure_reason: _common_pb2.PodFailureReason
    not_ready_reason: _common_pb2.NotReadyReason
    idle_time_minutes: int
    state_message: str
    image: str
    def __init__(self, tenant_id: _Optional[str] = ..., notebook_id: _Optional[str] = ..., state: _Optional[_Union[NotebookState, str]] = ..., failure_reason: _Optional[_Union[_common_pb2.PodFailureReason, str]] = ..., not_ready_reason: _Optional[_Union[_common_pb2.NotReadyReason, str]] = ..., idle_time_minutes: _Optional[int] = ..., state_message: _Optional[str] = ..., image: _Optional[str] = ...) -> None: ...
