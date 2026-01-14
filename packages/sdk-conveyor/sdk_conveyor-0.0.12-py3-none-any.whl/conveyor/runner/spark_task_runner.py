import logging
from datetime import timedelta
from typing import Any, Literal, Mapping, Optional, Sequence, Union

import google.protobuf.duration as pb_duration

from conveyor import grpc
from conveyor.pb.datafy_pb2 import (
    DatafyProjectInfo,
    RunApplicationRequest,
    RunApplicationResponse,
    SparkSpec,
)
from conveyor.pb.datafy_pb2_grpc import EnvironmentServiceStub, ProjectServiceStub
from conveyor.secrets import SecretValue, render_env_vars_crd
from conveyor.types import InstanceLifecycle, InstanceType

from .task_runner import TaskRunnerImpl
from .task_state import ApplicationRunTaskState

logger = logging.getLogger(__name__)


class SparkTaskRunner(TaskRunnerImpl):

    def __init__(
        self,
        *,
        task_name: str,
        project_name: str,
        environment_name: str,
        build_id: Optional[str] = None,
        application: str = "",
        application_args: Optional[Sequence[Any]] = None,
        conf: Optional[Mapping[str, str]] = None,
        env_vars: Optional[Mapping[str, Union[str, SecretValue]]] = None,
        iam_identity: Optional[str] = None,
        num_executors: Optional[int] = None,
        driver_instance_type: InstanceType = InstanceType.mx_small,
        executor_instance_type: InstanceType = InstanceType.mx_small,
        instance_lifecycle: InstanceLifecycle = InstanceLifecycle.spot,
        s3_committer: Optional[Literal["file", "magic"]] = "file",
        abfs_committer: Optional[Literal["file", "manifest"]] = "file",
        executor_disk_size: Optional[int] = None,
        mode: Optional[Literal["local", "cluster", "cluster-v2"]] = "cluster-v2",
        aws_availability_zone: Optional[str] = None,
        verbose: bool = False,
        execution_timeout: Optional[timedelta] = None,
    ):
        super().__init__(
            project_name=project_name,
            environment_name=environment_name,
        )
        self.task_name = task_name
        self.build_id = build_id
        self.application = application
        self.application_args = application_args or []
        self.conf = conf or {}
        self.env_vars = env_vars
        self.iam_identity = iam_identity
        self.num_executors = num_executors
        self.driver_instance_type = driver_instance_type
        self.executor_instance_type = executor_instance_type
        self.instance_lifecycle = instance_lifecycle
        self.s3_committer = s3_committer
        self.abfs_committer = abfs_committer
        self.executor_disk_size = executor_disk_size
        self.mode = mode
        self.aws_availability_zone = aws_availability_zone
        self.verbose = verbose
        self._timeout: timedelta = timedelta() if execution_timeout is None else execution_timeout

    def start_run(self, channel: grpc.Channel) -> ApplicationRunTaskState:
        request = self.generate_request(channel)
        environment_service = EnvironmentServiceStub(channel)
        response: RunApplicationResponse = environment_service.RunApplication(request)
        return ApplicationRunTaskState(
            task_name=request.task_name,
            application_run_id=response.application_run_id,
            environment_id=request.environment_id,
            project_id=request.spark_spec.datafy_project_info.project_id,
        )

    def generate_request(self, channel: grpc.Channel) -> RunApplicationRequest:
        build_id = self.build_id
        if build_id is None:
            build_id = self.find_build_id(channel, self.project_name)

        spark_spec: SparkSpec = SparkSpec(
            image=self.image(channel, build_id=build_id, project_name=self.project_name),
            application=self.application,
            application_args=self.application_args,
            spark_config=self.conf,
            env_variables=render_env_vars_crd(self.env_vars),
            aws_role=self.iam_identity,
            azure_application_client_id=self.iam_identity,
            datafy_project_info=DatafyProjectInfo(
                project_id=self.project_id(channel),
                project_name=self.project_name,
                build_id=build_id,
                environment_id=self.environment_id(channel),
            ),
            mode=self.mode,
            aws_availability_zone=self.aws_availability_zone,
            scheduled_by="SDK",
            instance_life_cycle=InstanceLifecycle.Name(self.instance_lifecycle),
            driver_instance_type=InstanceType.Name(self.driver_instance_type).replace("_", "."),
            executor_instance_type=InstanceType.Name(self.executor_instance_type).replace("_", "."),
            executor_disk_size=self.executor_disk_size,
            number_of_executors=(2 if self.num_executors is None else int(self.num_executors)),
            s3_committer=self.s3_committer,
            abfs_committer=self.abfs_committer,
            verbose=self.verbose,
        )
        return RunApplicationRequest(
            environment_id=self.environment_id(channel),
            spark_spec=spark_spec,
            task_name=self.task_name,
            timeout=pb_duration.from_timedelta(self._timeout),
        )
