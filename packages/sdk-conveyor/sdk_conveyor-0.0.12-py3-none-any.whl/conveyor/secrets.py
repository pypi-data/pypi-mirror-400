"""This file is intended to reflect the structure of data-plane/airflow/src/conveyor_airflow_plugins/secrets.py
If you modify a function signature or add an implementation in this file,
please implement the corresponding change there as well.
"""

import logging
import numbers
from typing import Any, Mapping, Optional, Union

from conveyor.pb.common_pb2 import (
    AwsSecretsManagerResolver,
    AwsSSMParameterStoreResolver,
    AzureKeyVaultResolver,
    EnvVarResolver,
)


class SecretValue:
    def render(self) -> EnvVarResolver:
        raise NotImplementedError


class AWSSecretsManagerValue(SecretValue):
    def __init__(self, name: str, path: Optional[str] = None):
        self.name: str = name
        self.path: Optional[str] = path

    def render(self) -> EnvVarResolver:
        return EnvVarResolver(
            aws_secrets_manager=AwsSecretsManagerResolver(
                name=self.name,
                path=self.path,
            )
        )


class AWSParameterStoreValue(SecretValue):
    def __init__(self, name: str, path: Optional[str] = None):
        self.name: str = name
        self.path: Optional[str] = path

    def render(self) -> EnvVarResolver:
        return EnvVarResolver(
            aws_s_s_m_parameter_store=AwsSSMParameterStoreResolver(
                name=self.name,
                path=self.path,
            )
        )


class AzureKeyVaultValue(SecretValue):
    def __init__(self, name: str, vault: str, vault_type: str = "secret"):
        self.name: str = name
        self.vault = vault
        self.vault_type = vault_type

    def render(self) -> EnvVarResolver:
        return EnvVarResolver(
            azure_key_vault=AzureKeyVaultResolver(
                name=self.name,
                key_vault_name=self.vault,
                type=self.vault_type,
            )
        )


def render_env_vars_crd(
    env_vars: Optional[Mapping[str, Union[str, bool, numbers.Real, SecretValue]]] = None,
) -> Mapping[str, EnvVarResolver]:
    results: dict[str, Any] = {}

    if env_vars:
        for key in env_vars:
            if (env_value := env_vars[key]) is None:
                logging.warning(
                    f"Environment variable with key '{key}' has value None, converting it to an empty value.",
                )
                results[key] = EnvVarResolver(value="")
            elif isinstance(env_value, (str, bool, numbers.Real)):
                results[key] = EnvVarResolver(value=str(env_value))
            elif isinstance(env_value, SecretValue):
                results[key] = env_value.render()
            else:
                raise Exception(f"Unknown environment variable type: {env_value}")
    return results
