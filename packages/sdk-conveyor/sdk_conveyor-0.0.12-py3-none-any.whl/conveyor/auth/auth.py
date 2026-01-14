import json
import logging
import os
import subprocess
import webbrowser
from typing import TYPE_CHECKING, Optional

import grpc
from packaging.version import Version
from packaging.version import parse as parse_version

if TYPE_CHECKING:
    from subprocess import CompletedProcess

logger = logging.getLogger(__name__)


class _ElectronNotAsNode:
    """Workaround for https://github.com/microsoft/vscode/issues/224498"""

    __slots__ = "value"

    def __enter__(self):
        self.value = os.environ.pop("ELECTRON_RUN_AS_NODE", None)

    def __exit__(self, type_, value, traceback):
        if self.value is not None:
            os.environ["ELECTRON_RUN_AS_NODE"] = value


def _get_token(timeout: int = 60) -> Optional[str]:
    try:
        proc = subprocess.Popen(
            ("conveyor", "auth", "get", "--no-browser"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        logger.error(
            "The Conveyor CLI is not installed, please follow the instructions at https://docs.conveyordata.com/get-started/installation#install-the-cli"
        )
        return None

    if (io := proc.stderr) and (message := io.readline()):
        # Parse error message to obtain login URL (if needed)
        url = str(message).split(": ")[-1]
        # Use main process to open URL, using a subprocess for this does not always work (f.e. in Jupyter)
        with _ElectronNotAsNode():
            webbrowser.open_new_tab(url)

    try:
        outs, errs = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        _log_error(f"Unable to authenticate after waiting {timeout} seconds.", outs, errs)
        return None

    try:
        return json.loads(outs).get("access_token")
    except json.decoder.JSONDecodeError:
        if "could not authorize the CLI within a minute" in outs:
            # The CLI has an internal timeout of 60 seconds
            logger.error("Unable to authenticate after waiting 60 seconds.")
        elif "Received a non-tty input device for the login flow" in outs:
            # When running in CI, there is no user interaction possible to get credentials
            _log_error("Unable to obtain login credentials.", outs, errs)
        else:
            # Something else went wrong
            _log_error("Error decoding the JSON response for login.", outs, errs)
        return None


def _log_error(message: str, outs: Optional[str], errs: Optional[str]) -> None:
    if outs:
        message += f"\nMessage: {outs}"
    if errs:
        message += f"\nError: {errs}"
    logger.error(message)


def get_api_url() -> str:
    completed: CompletedProcess = subprocess.run(
        ("conveyor", "auth", "config"),
        capture_output=True,
        timeout=10,
        text=True,
        env=os.environ,
    )
    return json.loads(completed.stdout).get("api")


def get_grpc_target() -> str:
    api_url = get_api_url()
    return api_url.replace("https://", "")


def get_grpc_credentials() -> grpc.ChannelCredentials:
    try:
        access_token = _get_token()
    except Exception as e:
        logger.error(f"Failed to get Conveyor token due to {str(e)}")
        access_token = None

    if not access_token:
        exit(1)

    ssl = grpc.ssl_channel_credentials()
    token = grpc.access_token_call_credentials(access_token)
    return grpc.composite_channel_credentials(ssl, token)


def _validate_version(version: str) -> None:
    stripped_version = version
    # Our dev builds add an extra git hash which is not recognized by the version parser so we remove it
    if "-" in stripped_version:
        stripped_version = stripped_version.split("-")[0]

    minimum_version = "1.18.10"
    if parse_version(stripped_version) < Version(minimum_version):
        raise SystemExit(
            Exception(
                f"Your Conveyor CLI is too old to work with the Python SDK.\n"
                f"The minimal version is {minimum_version}, you are using {version}."
            )
        )


def validate_cli_version() -> None:
    completed: CompletedProcess = subprocess.run(
        ("conveyor", "--version"),
        capture_output=True,
        timeout=10,
        text=True,
        env=os.environ,
    )
    version = completed.stdout.replace("conveyor version", "").strip()
    _validate_version(version)
