"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h
from multiprocessing import Queue as NewQueue
from multiprocessing import current_process as CurrentProcess
from queue import Empty as EmptyError
from threading import Thread as thread_t

from mpss_tools_36.constant.generic import REQUEST_STOP
from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from mpss_tools_36.extension.data_class import NO_CHOICE
from mpss_tools_36.hint.serializer import Deserializer_h, Serializer_h
from mpss_tools_36.type.line import line_end_t, line_t


@d.dataclass(slots=True, repr=False, eq=False)
class server_t:
    name: str

    Serializer: Serializer_h | None = None
    Deserializer: Deserializer_h | None = None
    lock: h.Any = NO_CHOICE(None)

    _lines: list[line_t] = NO_CHOICE(list)
    _thread: thread_t | None = NO_CHOICE(None)

    def __post_init__(self) -> None:
        """"""
        if self.Serializer is None:
            self.Serializer = lambda _: (_, None)
        if self.Deserializer is None:
            self.Deserializer = lambda _: (_, None)

    def NewLine(self) -> line_t:
        """"""
        assert self._thread is None

        output = line_t(request=NewQueue(), answer=NewQueue())

        self._lines.append(output)

        return output

    def Start(self, /, *, n_tasks: int = 0) -> tuple[line_t, ...] | None:
        """"""
        assert CurrentProcess().name == MAIN_PROCESS_NAME
        assert self._thread is None

        if n_tasks > 0:
            output = tuple(self.NewLine() for _ in range(n_tasks))
        else:
            assert self._lines.__len__() > 0
            output = None

        self._thread = thread_t(target=self._Run)
        self._thread.start()

        return output

    def _Run(self) -> None:
        """"""
        raise NotImplementedError

    @staticmethod
    def ActiveRequests(
        active_lines: list[line_t], /
    ) -> list[tuple[line_end_t, line_end_t, str | tuple]]:
        """"""
        output = []

        for line in tuple(active_lines):
            request_line_end = line.request
            try:
                request = request_line_end.get(False)
            except EmptyError:
                pass
            else:
                output.append((request_line_end, line.answer, request))

        return output

    def Stop(self, *_, **__) -> None:
        """"""
        assert CurrentProcess().name == MAIN_PROCESS_NAME
        assert self._thread is not None

        # There are necessarily lines (see Start).
        self._lines[0].request.put(REQUEST_STOP)
        self._thread.join()
        self._thread = None

        for line_ends in self._lines:
            for line_end in line_ends:
                line_end.close()
                line_end.join_thread()
        self._lines.clear()
