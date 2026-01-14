import atexit
from functools import lru_cache

import grpc
from grpc import Channel, RpcError, StatusCode

from conveyor.auth import get_grpc_credentials, get_grpc_target
from conveyor.auth.auth import validate_cli_version


@lru_cache(maxsize=None)
def connect() -> Channel:
    validate_cli_version()

    channel = grpc.secure_channel(
        target=get_grpc_target(),
        credentials=get_grpc_credentials(),
        compression=grpc.Compression.Gzip,
    )

    def cleanup():
        channel.close()

    atexit.register(cleanup)
    return channel


__all__ = ["connect", "Channel", "RpcError", "StatusCode"]
