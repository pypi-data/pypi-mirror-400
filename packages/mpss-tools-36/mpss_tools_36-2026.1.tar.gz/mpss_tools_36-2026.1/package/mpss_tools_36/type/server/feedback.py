"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import functools as f
import time
import typing as h
from multiprocessing import Value as shared_value_t
from multiprocessing import current_process as CurrentProcess
from threading import Thread as thread_t

from mpss_tools_36.constant.feedback import DONE, POLLING_PERIOD, TO_DO, UNKNOWN_VALUE
from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from mpss_tools_36.extension.chronos import FormatedDuration
from mpss_tools_36.extension.data_class import NO_CHOICE
from mpss_tools_36.hint.feedback import send_feedback_h
from mpss_tools_36.hint.process import process_h


@d.dataclass(slots=True, repr=False, eq=False)
class server_t:
    n_iterations_per_task: int | h.Sequence[int]

    prefix: str = ""
    feedback_period: int | float = 3.0
    print_report: bool = False

    _message_template: str = d.field(init=False)
    _shared_iterations_per_task: list[h.Any] = NO_CHOICE(list)
    _shared_main_counter_per_task: list[h.Any] = NO_CHOICE(list)
    _thread: thread_t | None = NO_CHOICE(None)

    def __post_init__(self) -> None:
        """"""
        assert CurrentProcess().name == MAIN_PROCESS_NAME

        self._message_template = (
            self.prefix + "|{}{: >6.2f}% {}| @ {}s/it #{} +{} -{}:{}"
        )

    def NewFeedbackSendingFunction(self) -> send_feedback_h:
        """"""
        shared_iterations, shared_main_counter = (
            shared_value_t("Q"),
            shared_value_t("Q"),
        )
        self._shared_iterations_per_task.append(shared_iterations)
        self._shared_main_counter_per_task.append(shared_main_counter)

        return f.partial(_SendFeedback, shared_iterations, shared_main_counter)

    def Start(self) -> None:
        """
        For sequential processing.
        """
        process = CurrentProcess()
        assert process.name == MAIN_PROCESS_NAME
        assert self._thread is None

        self._thread = thread_t(target=self.RunUntilExhausted, args=((process,),))
        self._thread.start()

    def RunUntilExhausted(self, tasks: h.Sequence[process_h], /) -> None:
        """
        For parallel processing (when called directly).
        """
        reference = start_time = time.time()

        n_tasks = self._shared_iterations_per_task.__len__()
        if n_tasks == 0:  # I.e., NewFeedbackSendingFunction has never been called.
            return

        assert n_tasks == tasks.__len__()

        if isinstance(self.n_iterations_per_task, int):
            self.n_iterations_per_task = n_tasks * (self.n_iterations_per_task,)
        else:
            assert self.n_iterations_per_task.__len__() == n_tasks, (
                self.n_iterations_per_task.__len__(),
                n_tasks,
            )
        n_iterations_total = float(sum(self.n_iterations_per_task))
        if n_iterations_total == 0.0:
            return

        # See below about format.
        half_bar = 20 * TO_DO
        message = self._message_template.format(
            half_bar,
            0.0,
            half_bar,
            UNKNOWN_VALUE,
            UNKNOWN_VALUE,
            "00",
            UNKNOWN_VALUE,
            n_tasks,
        )
        message_length = message.__len__()
        print(f"{message}\r", end="", flush=True)

        while True:
            n_iterations_completed, total_main_counter = 0.0, 0
            n_active_tasks = n_tasks
            for task, n_iterations, shared_iterations, shared_main_counter in zip(
                tasks,
                self.n_iterations_per_task,
                self._shared_iterations_per_task,
                self._shared_main_counter_per_task,
                strict=True,
            ):
                iterations = shared_iterations.value
                if (iterations < 0) or (
                    (iterations < n_iterations) and not task.is_alive()
                ):
                    iterations = n_iterations
                    shared_iterations.value = n_iterations
                n_iterations_completed += iterations
                total_main_counter += shared_main_counter.value

                if iterations == n_iterations:
                    n_active_tasks -= 1

            if n_active_tasks == 0:
                break

            now = time.time()
            if now - reference < self.feedback_period:
                time.sleep(POLLING_PERIOD)
                continue
            reference = now

            completion = n_iterations_completed / n_iterations_total

            elapsed_time = now - start_time
            if completion > 0.0:
                remaining_time = (elapsed_time / completion) - elapsed_time
                remaining_time = FormatedDuration(remaining_time)
            else:
                remaining_time = UNKNOWN_VALUE
            if n_iterations_completed > 0.0:
                period = n_tasks * elapsed_time / n_iterations_completed
                period = f"{period:.2f}"
            else:
                period = UNKNOWN_VALUE

            # Below, "X"=DONE and "-"=TO_DO.
            # 48 = 20_X_or_- (as in [:20])
            #    + 6_percent (as in 6.2f) + 1_% + 1_space
            #    + 20_X_or_- (as in [-20:]).
            n_completed = int(round(48.0 * completion))
            bar = f"{n_completed * DONE}{(48 - n_completed) * TO_DO}"
            message = self._message_template.format(
                bar[:20],
                100.0 * completion,
                bar[-20:],
                period,
                total_main_counter,
                FormatedDuration(elapsed_time),
                remaining_time,
                n_active_tasks,
            )
            message_length = max(message_length, message.__len__())
            print(f"{message: <{message_length}}\r", end="", flush=True)

        if self.print_report:
            elapsed_time = time.time() - start_time
            period = n_tasks * elapsed_time / n_iterations_total
            message = (
                f"{self.prefix}Summary: "
                f"{period:.2f}s/it "
                f"#{total_main_counter} "
                f"+{FormatedDuration(elapsed_time)}"
            )
            print(f"{message: <{message_length}}", flush=True)
        else:
            space = " "
            print(f"{space: <{message_length}}\r", end="", flush=True)

    def Stop(self) -> None:
        """
        For sequential processing.
        Safe to call on an un-started server.
        """
        assert CurrentProcess().name == MAIN_PROCESS_NAME

        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def ReportTaskStarting(self, tasks: int | h.Sequence[process_h], /) -> None:
        """"""
        if isinstance(tasks, int):
            print(f"{self.prefix}Starting {tasks} tasks...", flush=True)
        else:
            pids = tuple(_.pid for _ in tasks)
            print(f"{self.prefix}All tasks started: {str(pids)[1:-1]}.", flush=True)


def _SendFeedback(
    shared_iterations: h.Any,
    shared_main_counter: h.Any,
    iterations: int,
    main_counter: int,
    /,
) -> None:
    """"""
    shared_iterations.value = iterations
    shared_main_counter.value = main_counter
