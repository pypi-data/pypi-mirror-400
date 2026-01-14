import json
import logging
import subprocess
from typing import Optional, Sequence

from conveyor.auth import validate_cli_version

logger = logging.getLogger(__name__)


class ProjectBuilder:
    def __init__(
        self,
        *,
        project_path: str,
        build_args: Optional[Sequence[str]] = None,
        secret_args: Optional[Sequence[str]] = None,
    ):
        """Initialize the project builder.

        Keyword arguments:
        project_path -- The file path to your project root, this can be relative to the current file.
        build_args (optional) -- A sequence of optional build arguments to be passed to the Docker context.
            Each element of the sequence should typically be of the form `key=value`.
        secret_args (optional) -- A sequence of optional secret arguments to be passed to the Docker context.
            Each element of the sequence should typically be of the form `id=mysecret,env=MY_SECRET`.
        """
        self._project_path = project_path
        self._all_args = self._construct_build_args(build_args, secret_args)

    @classmethod
    def _construct_build_args(
        cls, build_args: Optional[Sequence[str]], secret_args: Optional[Sequence[str]]
    ) -> Sequence[str]:
        args: list[str] = []

        if build_args is None:
            build_args = []

        if secret_args is None:
            secret_args = []

        for arg in build_args:
            args.append("--build-arg")
            args.append(arg)

        for arg in secret_args:
            args.append("--secret")
            args.append(arg)

        return args

    def build(self) -> str:
        """Trigger the container build process for your project.

        Returns:
        -- The build ID belonging to the produced build artefact.
        """
        validate_cli_version()
        proc = subprocess.run(
            args=("conveyor", "build", "-ojson", *self._all_args),
            stdout=subprocess.PIPE,
            text=True,
            cwd=self._project_path,
        )
        if proc.returncode == 0:
            build_id = json.loads(proc.stdout)["id"]
            logger.info(f"Build successful with id: {build_id}")
            return build_id
        else:
            raise Exception("The build failed")
