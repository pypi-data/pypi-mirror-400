"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import time
import typing as h
from multiprocessing import Lock as NewLock

from mpss_tools_36.extension.chronos import FormatedDuration
from mpss_tools_36.extension.data_class import NO_CHOICE
from mpss_tools_36.hint.feedback import send_feedback_h
from mpss_tools_36.type.server.feedback import server_t as base_t


@d.dataclass(slots=True, repr=False, eq=False)
class server_t(base_t):
    previous_task_idx: int = NO_CHOICE(-1)
    lock: h.Any = NO_CHOICE(NewLock)

    @staticmethod
    def _SendFeedback(
        iterations: int,
        main_counter: int,
        /,
        *,
        task_idx: int = -1,
        n_iterations_per_task: int | h.Sequence[int] = 0,
        prefix: str = "",
        start_time: float = 0.0,
        period: float = 0.0,
        lock: h.Any = None,
    ) -> None:
        """
        Setting method attributes does not work with a class method.
        """
        if isinstance(n_iterations_per_task, int):
            n_iterations = n_iterations_per_task
        else:
            n_iterations = n_iterations_per_task[task_idx]
        if n_iterations == 0:
            return

        prologue = f"{prefix}{task_idx + 1}: "
        now = time.time()
        elapsed_time = now - start_time
        elapsed_time_formatted = FormatedDuration(elapsed_time)

        if (iterations is None) or (iterations == n_iterations):
            message = f"{prologue}DONE #{main_counter} +{elapsed_time_formatted}"
            with lock:
                print(f"{message: <50}", flush=True)
            return

        with lock:
            reference = getattr(server_t._SendFeedback, "reference", start_time)
        if now - reference < period:
            return

        if iterations > 0:
            total_time = (elapsed_time * n_iterations) / iterations
            remaining_time = FormatedDuration(total_time - elapsed_time)
        else:
            remaining_time = "???"
        message = (
            f"{prologue}{iterations}/{n_iterations} #{main_counter} "
            f"+{elapsed_time_formatted} -{remaining_time}"
        )

        with lock:
            setattr(server_t._SendFeedback, "reference", now)
            print(f"{message: <50}\r", end="", flush=True)

    def NewFeedbackSendingFunction(self) -> send_feedback_h | None:
        """"""
        start_time = time.time()  # Assign to variable to allow for proper closure.
        task_idx = self.previous_task_idx + 1
        self.previous_task_idx = task_idx

        def output(_, __) -> None:
            #
            self.__class__._SendFeedback(
                _,
                __,
                task_idx=task_idx,
                n_iterations_per_task=self.n_iterations_per_task,
                prefix=self.prefix,
                start_time=start_time,
                period=self.feedback_period,
                lock=self.lock,
            )

        return output

    def RunUntilExhausted(self, _, /) -> None:
        """"""
        pass
