import logging
from datetime import timedelta
from typing import Any, Collection, Mapping, Optional, Sequence, Union, cast

import google.protobuf.duration as pb_duration

from conveyor import grpc
from conveyor.pb.datafy_pb2 import (
    ContainerSpec,
    DatafyProjectInfo,
    RunApplicationRequest,
    RunApplicationResponse,
)
from conveyor.pb.datafy_pb2_grpc import EnvironmentServiceStub, ProjectServiceStub
from conveyor.secrets import SecretValue, render_env_vars_crd
from conveyor.types import InstanceLifecycle, InstanceType

from .task_runner import TaskRunnerImpl
from .task_state import ApplicationRunTaskState

logger = logging.getLogger(__name__)


class ContainerTaskRunner(TaskRunnerImpl):

    def __init__(
        self,
        *,
        task_name: str,
        project_name: str,
        environment_name: str,
        build_id: Optional[str] = None,
        command: Optional[Sequence[str]] = None,
        arguments: Optional[Sequence[str]] = None,
        args: Optional[Sequence[str]] = None,
        env_vars: Optional[Mapping[str, Union[str, SecretValue]]] = None,
        iam_identity: Optional[str] = None,
        instance_type: InstanceType = InstanceType.mx_micro,
        instance_lifecycle: InstanceLifecycle = InstanceLifecycle.spot,
        disk_size: Optional[int] = None,
        disk_mount_path: Optional[str] = None,
        show_output: bool = True,
        execution_timeout: Optional[timedelta] = None,
    ):
        super().__init__(
            project_name=project_name,
            environment_name=environment_name,
        )
        self.task_name = task_name
        self.build_id = build_id
        self.command = command
        self.arguments = self._choose_arguments(args, arguments)
        self.env_vars = env_vars
        self.iam_identity = iam_identity
        self.instance_type = instance_type
        self.instance_lifecycle = instance_lifecycle
        self.disk_size = disk_size
        self.disk_mount_path = disk_mount_path
        self.show_output = show_output
        self._timeout: timedelta = timedelta() if execution_timeout is None else execution_timeout

    @staticmethod
    def _choose_arguments(
        args: Optional[Sequence[str]], arguments: Optional[Sequence[str]]
    ) -> Optional[Sequence[str]]:
        if args is not None:
            import warnings

            warnings.warn(
                "The `args` parameter is deprecated, please use `arguments` instead",
                DeprecationWarning,
            )

        return args if args is not None else arguments

    def start_run(self, channel: grpc.Channel) -> ApplicationRunTaskState:
        request = self.generate_request(channel)
        environment_service = EnvironmentServiceStub(channel)
        response: RunApplicationResponse = environment_service.RunApplication(request)
        return ApplicationRunTaskState(
            task_name=request.task_name,
            application_run_id=response.application_run_id,
            environment_id=request.environment_id,
            project_id=request.container_spec.datafy_project_info.project_id,
        )

    def generate_request(self, channel: grpc.Channel) -> RunApplicationRequest:
        build_id = self.build_id
        if build_id is None:
            build_id = self.find_build_id(channel, self.project_name)

        container_spec: ContainerSpec = ContainerSpec(
            datafy_project_info=DatafyProjectInfo(
                project_id=self.project_id(channel),
                project_name=self.project_name,
                build_id=build_id,
                environment_id=self.environment_id(channel),
            ),
            image=self.image(channel, build_id=build_id, project_name=self.project_name),
            command=self._ensure_string_sequence(self.command),
            args=self._ensure_string_sequence(self.arguments),
            env_variables=render_env_vars_crd(self.env_vars),
            instance_type=InstanceType.Name(self.instance_type).replace("_", "."),
            instance_life_cycle=InstanceLifecycle.Name(self.instance_lifecycle),
            aws_role=self.iam_identity,
            azure_application_client_id=self.iam_identity,
            scheduled_by="SDK",
            disk_size=self.disk_size,
            disk_mount_path=self.disk_mount_path,
        )
        return RunApplicationRequest(
            environment_id=self.environment_id(channel),
            container_spec=container_spec,
            task_name=self.task_name,
            timeout=pb_duration.from_timedelta(self._timeout),
        )

    @staticmethod
    def _ensure_string_sequence(
        value: Optional[Union[Any, Collection[Any]]],
    ) -> Optional[Sequence[str]]:
        if value is None:
            return None
        if isinstance(value, str):
            return [value]
        if isinstance(value, Collection):
            return [str(element) for element in value]
        else:
            return [str(value)]
