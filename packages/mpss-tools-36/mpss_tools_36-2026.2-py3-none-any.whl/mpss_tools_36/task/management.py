"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import multiprocessing as prll
import time
import typing as h

from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from mpss_tools_36.type.server.feedback import server_t


def SetStartMethod(name: str, /) -> bool:
    """"""
    assert prll.current_process().name == MAIN_PROCESS_NAME
    assert name in ("fork", "forkserver", "spawn"), name

    if name not in prll.get_all_start_methods():
        return False

    if prll.get_start_method() != name:
        prll.set_start_method(name, force=True)

    return True


def StartAndTrackTasks(
    tasks: h.Sequence[prll.Process],
    /,
    *,
    should_return_elapsed_time: bool = False,
    prefix: str = "",
    feedback_server: server_t | None = None,
) -> float | None:
    """"""
    assert prll.current_process().name == MAIN_PROCESS_NAME

    feedback_server_exists = feedback_server is not None

    if feedback_server_exists:
        feedback_server.ReportTaskStarting(tasks.__len__())
        prefix = feedback_server.prefix

    if should_return_elapsed_time:
        reference = time.time()
    else:
        reference = None

    for task in tasks:
        task.start()

    if feedback_server_exists:
        feedback_server.ReportTaskStarting(tasks)
        feedback_server.RunUntilExhausted(tasks)

    for task_id, task in enumerate(tasks, start=1):
        if task.exitcode is None:
            task.join()
        if task.exitcode != 0:
            print(
                f"{prefix}Task {task_id}/{task.name} "
                f"exited with error code {task.exitcode}."
            )

    if should_return_elapsed_time:
        return time.time() - reference
    return None
