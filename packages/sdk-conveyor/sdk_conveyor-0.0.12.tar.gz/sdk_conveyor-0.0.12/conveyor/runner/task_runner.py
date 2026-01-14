import logging
import signal
from abc import ABC, abstractmethod
from functools import partial
from typing import Optional, cast

from google.protobuf.timestamp_pb2 import Timestamp

from conveyor import grpc
from conveyor.pb.datafy_pb2 import (
    CancelApplicationRequest,
    ListBuildsRequest,
    ListEnvironmentsRequest,
    ListProjectsRequest,
    RunApplicationLogsRequest,
)
from conveyor.pb.datafy_pb2_grpc import EnvironmentServiceStub, ProjectServiceStub
from conveyor.project import get_project_api

from .task_state import ApplicationRunResult, ApplicationRunTaskState, TaskState

logger = logging.getLogger(__name__)


class CancelledException(BaseException):
    """Raised when the log streaming was interrupted."""


class TaskRunner(ABC):

    def start(self) -> None:
        """Runs your task."""
        self.start_run(grpc.connect())

    @abstractmethod
    def start_run(self, channel: grpc.Channel) -> TaskState:
        raise NotImplementedError


class TaskRunnerImpl(TaskRunner, ABC):
    def __init__(
        self,
        project_name: str,
        environment_name: str,
    ):
        self.project_name = project_name
        self._project_id: Optional[str] = None
        self.environment_name = environment_name
        self._environment_id: Optional[str] = None

    def start(self) -> None:
        """Runs your task."""
        self.start_run(grpc.connect())

    @abstractmethod
    def start_run(self, channel: grpc.Channel) -> ApplicationRunTaskState:
        raise NotImplementedError

    @classmethod
    def find_project_id(cls, channel: grpc.Channel, project_name: str) -> str:
        project_service = ProjectServiceStub(channel)
        list_projects_response = project_service.ListProjects(
            ListProjectsRequest(name=project_name)
        )
        if not list_projects_response.projects:
            raise Exception(f"No project found to match the name: {project_name}.")
        if len(list_projects_response.projects) > 1:
            raise Exception(f"Multiple projects found to match the name: {project_name}.")
        return list_projects_response.projects[0].id

    @classmethod
    def find_environment_id(cls, channel: grpc.Channel, environment_name: str) -> str:
        environment_service = EnvironmentServiceStub(channel)
        list_environments_response = environment_service.ListEnvironments(
            ListEnvironmentsRequest(name=environment_name)
        )
        if not list_environments_response.environments:
            raise Exception(f"No environment found to match the name: {environment_name}.")
        if len(list_environments_response.environments) > 1:
            raise Exception(f"Multiple environments found to match the name: {environment_name}.")
        return list_environments_response.environments[0].id

    def find_build_id(self, channel: grpc.Channel, project_name: str) -> str:
        project_service = ProjectServiceStub(channel)
        builds_response = project_service.ListBuilds(
            ListBuildsRequest(project_id=self.find_project_id(channel, project_name))
        )
        builds = builds_response.builds
        if len(builds) == 0:
            raise Exception("No builds found")
        else:
            return builds[0].id

    def image(self, channel: grpc.Channel, *, project_name: str, build_id: str) -> str:
        project_api = get_project_api(channel, self.find_project_id(channel, project_name))
        return (
            f"{project_api.get_registry_url()}/datafy/data-plane/project/{project_name}:{build_id}"
        )

    def project_id(self, channel: grpc.Channel) -> str:
        if self._project_id is None:
            self._project_id = self.find_project_id(channel, self.project_name)
        return cast(str, self._project_id)

    def environment_id(self, channel: grpc.Channel) -> str:
        if self._environment_id is None:
            self._environment_id = self.find_environment_id(channel, self.environment_name)
        return cast(str, self._environment_id)

    def run(self) -> ApplicationRunResult:
        channel = grpc.connect()
        task_state = self.start_run(channel)

        logger.debug("Fetching the logs")
        req = RunApplicationLogsRequest(
            environment_id=self.environment_id(channel),
            project_id=self.project_id(channel),
            application_run_id=task_state.application_run_id,
        )
        # This block makes sure we handle an interrupt while the job is running and cancel it
        # We throw and catch a cancelled exception since otherwise we would wait until the job is canceled on kubernetes
        # which by default takes up to 30s
        try:
            signal.signal(
                signal.SIGINT,
                partial(
                    self.handle_interrupt_manual_run,
                    channel,
                    task_state.application_run_id,
                ),
            )
            self.tail_logs_with_retry(channel, req)
        except CancelledException:
            return ApplicationRunResult(
                task_name=task_state.task_name,
                environment_id=req.environment_id,
                project_id=req.project_id,
                application_run_id=task_state.application_run_id,
                failed=True,
                failure_reason="You cancelled the application",
            )
        return task_state.get_application_run_result(channel)

    @classmethod
    def tail_logs_with_retry(cls, channel: grpc.Channel, req: RunApplicationLogsRequest) -> int:
        """Returns the exit code of the container application."""
        tries = 0
        latest_message_timestamp: Optional[Timestamp] = None
        while True:
            environment_service = EnvironmentServiceStub(channel)
            try:
                logs_response = environment_service.GetApplicationLogs(
                    cls.copy_logs_request_with_timestamp(req, latest_message_timestamp)
                )
                for log in logs_response:
                    match log.WhichOneof("response"):
                        case "log_line":
                            latest_message_timestamp = log.log_line.timestamp
                            print(log.log_line.log)
                        case "heartbeat":
                            continue
                        case "exit_code":
                            logger.debug(f"Got exit code {log.exit_code}")
                            return log.exit_code
                return 0
            except Exception as e:
                logger.debug(f"Got exception while tailing logs, reconnecting... {e}")
                tries += 1
                if tries >= 10:
                    logger.debug("Tried ten times, stopping")
                    raise e

    def handle_interrupt_manual_run(
        self, channel: grpc.Channel, application_run_id: str, sig, frame
    ) -> None:
        logger.debug(
            f"Received interrupt, cancelling the application run with id {application_run_id}"
        )
        try:
            environment_service = EnvironmentServiceStub(channel)
            environment_service.CancelApplication(
                CancelApplicationRequest(
                    environment_id=self.environment_id(channel),
                    project_id=self.project_id(channel),
                    application_run_id=application_run_id,
                )
            )
        except grpc.RpcError as e:
            logger.debug(f"Encountered error while cancelling the application:\n{e}")
        raise CancelledException()

    @classmethod
    def copy_logs_request_with_timestamp(
        cls,
        req: RunApplicationLogsRequest,
        latest_message_timestamp: Optional[Timestamp],
    ) -> RunApplicationLogsRequest:
        return RunApplicationLogsRequest(
            environment_id=req.environment_id,
            project_id=req.project_id,
            application_run_id=req.application_run_id,
            start_from=latest_message_timestamp,
        )
