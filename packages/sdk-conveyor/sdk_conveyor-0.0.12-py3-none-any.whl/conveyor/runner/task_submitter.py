from __future__ import annotations

import logging
import signal
import time
from collections.abc import Iterable, Iterator
from functools import partial

from conveyor import grpc

from .task_runner import CancelledException, TaskRunner
from .task_state import ApplicationRunResult, TaskState

logger = logging.getLogger(__name__)


class TaskSubmitter:

    def __init__(self, *tasks: TaskRunner):
        self.tasks = tasks

    @classmethod
    def from_list(cls, tasks: Iterable[TaskRunner]) -> TaskSubmitter:
        return cls(*tasks)

    def start(self) -> None:
        """Starts running each of the specified tasks without waiting for them to finish.
        Returns as soon as all tasks have been submitted to your cluster.
        """
        for task in self.tasks:
            task.start_run(grpc.connect())

    def run(self) -> Iterator[ApplicationRunResult]:
        """Runs the collection of tasks. Whenever a task finishes, its accompanying ApplicationRunResult is emitted.

        Returns:
        -- The iterator that produces the results for your tasks.
        """
        channel = grpc.connect()
        try:
            task_states: list[TaskState] = [task.start_run(channel) for task in self.tasks]
            signal.signal(
                signal.SIGINT,
                partial(self.handle_interrupt_manual_runs, channel, task_states),
            )

            while task_states:
                running_task_states: list[TaskState] = []
                for state in task_states:
                    if state.has_finished(channel):
                        yield state.get_application_run_result(channel)
                    else:
                        running_task_states.append(state)
                if running_task_states:
                    time.sleep(10)
                task_states = running_task_states
            return
        except CancelledException:
            return

    @staticmethod
    def handle_interrupt_manual_runs(channel, task_states: Iterable[TaskState], sig, frame) -> None:
        logger.debug(f"Received interrupt, cancelling all running applications")
        for task_state in task_states:
            task_state.cancel(channel)
        raise CancelledException()
