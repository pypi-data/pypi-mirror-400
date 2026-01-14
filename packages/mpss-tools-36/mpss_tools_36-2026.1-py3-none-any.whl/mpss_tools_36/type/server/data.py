"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h
from multiprocessing import Lock as NewLock
from multiprocessing import current_process as CurrentProcess
from multiprocessing.shared_memory import SharedMemory as shared_memory_t

import numpy as nmpy
from logger_36.api.memory import ObjectSize
from mpss_tools_36.constant.data import (
    DELETION_DONE,
    REQUEST_CHECK,
    REQUEST_DELETE,
    REQUEST_GET,
    REQUEST_SET,
    REQUEST_SIZE,
    STORAGE_DONE,
)
from mpss_tools_36.constant.generic import REQUEST_CLOSE, REQUEST_STATUS, REQUEST_STOP
from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from mpss_tools_36.extension.data_class import NO_CHOICE
from mpss_tools_36.hint.data import server_status_h
from mpss_tools_36.task.numpy_sharing import DisposeOriginalSharedArray, NewSharedArray
from mpss_tools_36.type.line import line_t
from mpss_tools_36.type.server.generic import server_t as base_t

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class server_t(base_t):
    """
    Numpy arrays must be set (using REQUEST_SET_NUMPY) and requested alone.

    The type of data can be h.Any at instantiation time, in which case it is considered
    as an object which will be converted into an attribute-name/attribute-value
    dictionary.
    """

    data: dict[str, h.Any] | h.Any = d.field(default_factory=dict)
    is_read_only: bool = True

    _shared_array_memory: dict[str, shared_memory_t] = NO_CHOICE(dict)

    @property
    def size(self) -> int:
        """"""
        return ObjectSize(self) + self.shared_size

    @property
    def shared_size(self) -> int:
        """"""
        return sum(_.size for _ in self._shared_array_memory.values())

    @property
    def status(self) -> server_status_h:
        """"""
        shared_array_memory = {
            _.name: f"SHARED:{_.size:_}" for _ in self._shared_array_memory.values()
        }

        return (
            self.name,
            self.size,
            {
                _: f"{type(__).__module__}.{type(__).__name__}"
                for _, __ in self.data.items()
            }
            | shared_array_memory,
            self.is_read_only,
            self._thread is not None,
        )

    def __post_init__(self) -> None:
        """"""
        assert CurrentProcess().name == MAIN_PROCESS_NAME

        base_t.__post_init__(self)

        if not self.is_read_only:
            self.lock = NewLock()

        if isinstance(self.data, dict):
            return

        data = {}
        for attribute in dir(self.data):
            if attribute[0] != "_":
                data[attribute] = getattr(self.data, attribute)
        self.data = data

    def _Run(self) -> None:
        """"""
        active_lines = list(self._lines)  # Work on a copy.
        while active_lines.__len__() > 0:
            for request_line_end, answer_line_end, request in base_t.ActiveRequests(
                active_lines
            ):
                if isinstance(request, tuple):
                    request, *arguments = request
                else:
                    arguments = ()
                # assert isinstance(request, str)

                if request == REQUEST_GET:
                    # arguments must be a typing.Sequence of str.
                    data = self.RequestedData(*arguments)
                    serialized, issues = self.Serializer(data)
                    if issues is None:
                        answer_line_end.put(serialized)
                    else:
                        raise RuntimeError(
                            f"Un-serializable object:\n{type(data).__name__}\n"
                            + "\n".join(issues)
                        )
                elif request == REQUEST_SET:
                    # arguments must be a typing.Sequence with a single, serialized
                    # dict[str, typing.Any].
                    deserialized, issues = self.Deserializer(arguments[0])
                    if issues is None:
                        self.Store(**deserialized)
                        answer_line_end.put(STORAGE_DONE)  # For synchronization.
                    else:
                        raise RuntimeError(
                            f"Un-deserializable object:\n{arguments[0]}\n"
                            + "\n".join(issues)
                        )
                elif request == REQUEST_DELETE:
                    # arguments must be a typing.Sequence of str.
                    self.Delete(*arguments)
                    answer_line_end.put(DELETION_DONE)  # For synchronization.
                elif request == REQUEST_CHECK:
                    # arguments must be a typing.Sequence of str.
                    answer_line_end.put(self.Has(*arguments))
                elif request == REQUEST_SIZE:
                    answer_line_end.put(self.size)
                elif request == REQUEST_STATUS:
                    answer_line_end.put(self.status)
                elif request == REQUEST_CLOSE:
                    active_lines.remove(
                        line_t(request=request_line_end, answer=answer_line_end)
                    )
                elif request == REQUEST_STOP:
                    active_lines.clear()
                    break
                else:
                    raise ValueError(
                        f'Unknown request "{request}" sent to '
                        f'data server "{self.name}".'
                    )

    def Has(self, *names) -> bool | tuple[bool, ...]:
        """"""
        if (n_names := names.__len__()) == 0:
            return self.data.__len__() > 0

        if n_names == 1:
            return names[0] in self.data

        return tuple(_ in self.data for _ in names)

    def RequestedData(self, *names) -> h.Any | tuple[h.Any, ...]:
        """
        If called indirectly (as a result of a request from a subprocess), returned data
        must be serialized.
        """
        if (n_names := names.__len__()) == 0:
            return self.data

        if n_names == 1:
            return self.data[names[0]]

        return tuple(self.data[_] for _ in names)

    def Store(self, /, **data) -> None:
        """
        If called indirectly (as a result of a request from a subprocess), data in
        arguments have been serialized.
        """
        if self.is_read_only:
            raise RuntimeError(
                f'Attempt to modify read-only data server "{self.name}".'
            )

        for name, value in data.items():
            if isinstance(value, array_t):
                if name in self._shared_array_memory:
                    DisposeOriginalSharedArray(self._shared_array_memory[name])
                _, sharing_name, shared_memory = NewSharedArray(value)
                self.data[name] = sharing_name
                self._shared_array_memory[name] = shared_memory
            else:
                self.data[name] = value

    def Delete(self, *names) -> None:
        """"""
        if names.__len__() == 0:
            names = tuple(self.data.keys())

        for name in names:
            if name in self._shared_array_memory:
                DisposeOriginalSharedArray(self._shared_array_memory[name])
                del self._shared_array_memory[name]
            del self.data[name]

    def DisposeSharedResources(self) -> None:
        """"""
        assert CurrentProcess().name == MAIN_PROCESS_NAME

        for shared_memory in self._shared_array_memory.values():
            DisposeOriginalSharedArray(shared_memory)
        self._shared_array_memory.clear()

    def Stop(self, /, *, should_dispose_shared_resources: bool = True) -> None:
        """"""
        base_t.Stop(self)

        if should_dispose_shared_resources:
            self.DisposeSharedResources()
