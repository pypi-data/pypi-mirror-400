import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from conveyor import grpc
from conveyor.auth import get_api_url
from conveyor.pb.application_runs_pb2 import (
    ApplicationRun,
    GetApplicationRunRequest,
    Phase,
)
from conveyor.pb.application_runs_pb2_grpc import ApplicationRunsServiceStub
from conveyor.pb.common_pb2 import PodFailureReason
from conveyor.pb.datafy_pb2 import CancelApplicationRequest
from conveyor.pb.datafy_pb2_grpc import EnvironmentServiceStub

logger = logging.getLogger(__name__)


class ApplicationRunResult:
    def __init__(
        self,
        *,
        task_name: str,
        environment_id: str,
        project_id: str,
        application_run_id: str,
        failed: bool,
        failure_reason: str,
    ):
        self.task_name = task_name
        self.environment_id = environment_id
        self.project_id = project_id
        self.application_run_id = application_run_id
        self.failed = failed
        self.failure_reason = failure_reason

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self

    def has_failed(self) -> bool:
        return self.failed

    def get_failure_reason(self) -> str:
        return self.failure_reason

    def conveyor_url(self) -> str:
        return f"{get_api_url()}/projects/{self.project_id}/environments/{self.environment_id}/apprun/{self.application_run_id}/logs/default"


class TaskState(ABC):

    @abstractmethod
    def get_application_run_result(self, channel: grpc.Channel) -> ApplicationRunResult:
        raise NotImplementedError

    @abstractmethod
    def cancel(self, channel: grpc.Channel) -> bool:
        raise NotImplementedError

    @abstractmethod
    def has_finished(self, channel: grpc.Channel) -> bool:
        raise NotImplementedError

    @abstractmethod
    def has_failed(self, channel: grpc.Channel) -> bool:
        raise NotImplementedError


class ApplicationRunTaskState(TaskState):
    def __init__(
        self,
        *,
        task_name: str,
        application_run_id: str,
        environment_id: str,
        project_id: str,
    ):
        self.task_name = task_name
        self.application_run_id = application_run_id
        self.environment_id = environment_id
        self.project_id = project_id
        self.created = datetime.now(timezone.utc)

    def get_application_run_result(self, channel: grpc.Channel) -> ApplicationRunResult:
        app_run = self.get_application_run(channel)

        return ApplicationRunResult(
            task_name=self.task_name,
            environment_id=self.environment_id,
            project_id=self.project_id,
            application_run_id=self.application_run_id,
            failed=self._is_failed_state(app_run),
            failure_reason=self._message_for_failure_reason(app_run),
        )

    def has_finished(self, channel: grpc.Channel) -> bool:
        logger.debug(f"Checking if job with id: {self.application_run_id} has finished")
        try:
            app_run = self.get_application_run(channel)
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
                if self.created + timedelta(seconds=60) < datetime.now(timezone.utc):
                    raise Exception("The job was not found after 1 minute")
                logger.debug(f"Job not found, we assume it has not started yet")
                return False
            raise rpc_error

        return self._is_finished_state(app_run)

    def has_failed(self, channel: grpc.Channel) -> bool:
        app_run = self.get_application_run(channel)
        return self._is_failed_state(app_run)

    @staticmethod
    def _is_failed_state(app_run: ApplicationRun) -> bool:
        return app_run.phase == Phase.Failed or app_run.phase == Phase.Canceled

    def get_application_run(self, channel: grpc.Channel) -> ApplicationRun:
        service = ApplicationRunsServiceStub(channel)
        return service.GetApplicationRunByApplicationId(
            GetApplicationRunRequest(application_id=self.application_run_id)
        )

    @staticmethod
    def _is_finished_state(app_run: ApplicationRun) -> bool:
        phase = app_run.phase
        return phase == Phase.Succeeded or phase == Phase.Canceled or phase == Phase.Failed

    def cancel(self, channel: grpc.Channel) -> bool:
        environment_service = EnvironmentServiceStub(channel)
        environment_service.CancelApplication(
            CancelApplicationRequest(
                environment_id=self.environment_id,
                application_run_id=self.application_run_id,
            )
        )
        return self.get_application_run(channel).phase == Phase.Failed

    @staticmethod
    def _message_for_failure_reason(app_run: ApplicationRun) -> str:
        # The returned messages reflect those shown by the UI
        match app_run.failure_reason:
            case PodFailureReason.Unspecified_PodFailureReason:
                return "Application error"
            case PodFailureReason.OutOfMemory:
                return "Out of memory error"
            case PodFailureReason.ImagePullBackOff:
                return "Image pull backoff"
            case PodFailureReason.EvictedDiskPressure:
                return "Not enough disk space left on the host"
            case PodFailureReason.ContainerCreatingForTooLong:
                return "The application was in the creation state for longer than 30 minutes"
            case PodFailureReason.StartError:
                return (
                    "The application failed to start due to an issue with the command or entrypoint"
                )
            case PodFailureReason.SpotNodeInterrupt:
                return "The application was killed due to a spot interruption"
            case PodFailureReason.DeletedWhilePending:
                return "The node the pod was going to be scheduled on has disappeared for an unknown reason"
            case PodFailureReason.DeletedWhileRunning:
                return "The node the pod was running on has disappeared for an unknown reason while the node was running"
            case PodFailureReason.ContainerErrorSigTerm:
                return "The application was stopped due to a signal term"
            case PodFailureReason.ContainerErrorSigKill:
                return "The application was stopped due to a signal kill"
            case PodFailureReason.InvalidImageName:
                return "The image name of the container is invalid"
            case PodFailureReason.ExecutionTimeout:
                return "Your application exceeded its execution timeout"
            case PodFailureReason.TooManyExecutorFailures:
                return "Your Spark application was stopped because there were too many executor failures"
            case PodFailureReason.SecretFailureCouldNotAssumeIamRole:
                return "The provided IAM role cannot be assumed, please check your role's trust relationship"
            case PodFailureReason.SecretFailureNoAccess:
                return "The provided IAM Identity does not have access to all secrets"
            case PodFailureReason.SecretFailureNoIamRoleProvided:
                return "No IAM role provided, but it is required when using secrets"
            case PodFailureReason.SecretFailureDoesNotExist:
                return "One of the requested secrets does not exist"
            case PodFailureReason.SecretFailureInvalidName:
                return "The secret name contains unsupported characters, ensure the secret name only uses alphanumeric characters or -/_+=.@!"
            case PodFailureReason.SecretFailureAzureClientIdDoesNotExist:
                return "The provided Azure Client ID does not exist in Azure"
            case PodFailureReason.SecretFailureNoAzureClientIdProvided:
                return "No Azure Client ID provided, but it is required when using secrets"
            case PodFailureReason.SecretFailureNoFederatedIdentityCredentialProvided:
                return "No federated identity credential exists for the Azure Client ID"
            case _:
                return ""
