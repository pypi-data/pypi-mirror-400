"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h
from multiprocessing import Lock as NewLock
from multiprocessing import current_process as CurrentProcess

from mpss_tools_36.constant.generic import REQUEST_CLOSE, REQUEST_STATUS, REQUEST_STOP
from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from mpss_tools_36.constant.wrapper import (
    REQUEST_ATTRIBUTE,
    REQUEST_ATTRIBUTES,
    REQUEST_CALL,
    REQUEST_METHODS,
)
from mpss_tools_36.hint.wrapper import server_status_h
from mpss_tools_36.type.line import line_t
from mpss_tools_36.type.server.generic import server_t as base_t


@d.dataclass(slots=True, repr=False, eq=False)
class server_t(base_t):
    object: h.Any = None
    # None default added because base_t has attributes with defaults.

    @property
    def status(self) -> server_status_h:
        """"""
        return self.name, type(self.object).__name__, self._thread is not None

    def __post_init__(self) -> None:
        """"""
        assert CurrentProcess().name == MAIN_PROCESS_NAME
        base_t.__post_init__(self)
        self.lock = NewLock()

    def _Run(self) -> None:
        """"""
        active_lines = list(self._lines)  # Work on a copy.
        while active_lines.__len__() > 0:
            for request_line_end, answer_line_end, request in base_t.ActiveRequests(
                active_lines
            ):
                if isinstance(request, tuple):
                    request, what, *remaining = request
                else:
                    what = remaining = None
                # assert isinstance(request, str)

                output, still_to_be_sent = None, True
                if request == REQUEST_CALL:
                    if (n_remining := remaining.__len__()) == 0:
                        args, kwargs = (), {}
                    else:
                        args, issues = self.Deserializer(remaining[0])
                        if issues is not None:
                            raise RuntimeError(
                                f"Un-deserializable object:\n{remaining[0]}\n"
                                + "\n".join(issues)
                            )
                        if n_remining > 1:
                            kwargs, issues = self.Deserializer(remaining[1])
                            if issues is not None:
                                raise RuntimeError(
                                    f"Un-deserializable object:\n{remaining[1]}\n"
                                    + "\n".join(issues)
                                )
                        else:
                            kwargs = {}
                    output = getattr(self.object, what)(*args, **kwargs)
                elif request == REQUEST_ATTRIBUTE:
                    output = getattr(self.object, what)
                elif request == REQUEST_ATTRIBUTES:
                    output = tuple(
                        _
                        for _ in dir(self.object)
                        if not isinstance(getattr(self.object, _), h.Callable)
                    )
                elif request == REQUEST_METHODS:
                    output = tuple(
                        _
                        for _ in dir(self.object)
                        if isinstance(getattr(self.object, _), h.Callable)
                    )
                elif request == REQUEST_STATUS:
                    answer_line_end.put(self.status)
                    still_to_be_sent = False
                elif request == REQUEST_CLOSE:
                    active_lines.remove(
                        line_t(request=request_line_end, answer=answer_line_end)
                    )
                    still_to_be_sent = False
                elif request == REQUEST_STOP:
                    active_lines.clear()
                    break
                else:
                    raise ValueError(
                        f'Unknown request "{request}" sent to '
                        f'data server "{self.name}".'
                    )

                if still_to_be_sent:
                    serialized, issues = self.Serializer(output)
                    if issues is None:
                        answer_line_end.put(serialized)
                    else:
                        raise RuntimeError(
                            f"Un-serializable object:\n{type(output).__name__}\n"
                            + "\n".join(issues)
                        )
