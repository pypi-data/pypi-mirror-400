from abc import ABC, abstractmethod

from conveyor import grpc
from conveyor.pb.datafy_pb2 import (
    GetProjectCredentialsRequest,
    GetProjectCredentialsResponse,
)
from conveyor.pb.datafy_pb2_grpc import ProjectServiceStub


class ProjectApi(ABC):

    @abstractmethod
    def get_registry_url(self) -> str:
        """Returns the URL of the container registry for your project."""
        raise NotImplementedError


class AwsProjectApi(ProjectApi):
    def __init__(self, creds: GetProjectCredentialsResponse.AwsProjectCredentials):
        self.registry_url = creds.registry_url
        self.region = creds.region

    def get_registry_url(self) -> str:
        return self.registry_url


class AzureProjectApi(ProjectApi):
    def __init__(self, creds: GetProjectCredentialsResponse.AzureProjectCredentials):
        self.registry_url = creds.registry_url

    def get_registry_url(self) -> str:
        return self.registry_url


def get_project_api(channel: grpc.Channel, project_id: str) -> ProjectApi:
    project_service: ProjectServiceStub = ProjectServiceStub(channel=channel)
    credentials = project_service.GetProjectCredentials(
        GetProjectCredentialsRequest(project_id=project_id)
    )

    kind = credentials.WhichOneof("spec")
    if kind == "aws_credentials":
        return AwsProjectApi(credentials.aws_credentials)
    elif kind == "azure_credentials":
        return AzureProjectApi(credentials.azure_credentials)
    else:
        raise ValueError(f"Received unknown credential type: {kind}")
