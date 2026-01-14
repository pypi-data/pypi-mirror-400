"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

from mpss_tools_36.constant.data import (
    DELETION_DONE,
    REQUEST_CHECK,
    REQUEST_DELETE,
    REQUEST_GET,
    REQUEST_SET,
    REQUEST_SIZE,
    STORAGE_DONE,
)
from mpss_tools_36.constant.generic import REQUEST_STATUS
from mpss_tools_36.hint.data import server_status_h
from mpss_tools_36.hint.serializer import Deserializer_h, Serializer_h
from mpss_tools_36.type.line import line_end_t, line_t
from mpss_tools_36.type.server.data import server_t


@d.dataclass(slots=True, repr=False, eq=False)
class client_t:
    Serializer: Serializer_h | None = None
    Deserializer: Deserializer_h | None = None

    def __post_init__(self) -> None:
        """"""
        if self.Serializer is None:
            self.Serializer = lambda _: (_, None)
        if self.Deserializer is None:
            self.Deserializer = lambda _: (_, None)

    @classmethod
    def New(
        cls, *, server: server_t | None = None, server_line: line_t | None = None
    ) -> client_direct_t | client_remote_t:
        """"""
        if server is None:
            return client_remote_t(
                request_line_end=server_line.request, answer_line_end=server_line.answer
            )
        return client_direct_t(server=server)


@d.dataclass(slots=True, repr=False, eq=False)
class client_direct_t(client_t):
    server: server_t | None = None
    # None default added because base_t has attributes with defaults.

    def RequestedData(self, *names) -> h.Any | tuple[h.Any, ...]:
        """"""
        return self.server.RequestedData(*names)

    def Send(self, /, **data) -> None:
        """"""
        self.server.Store(**data)

    def RequestDeletion(self, *names) -> None:
        """"""
        self.server.Delete(*names)

    def ServerHasData(self, *names) -> bool | tuple[bool, ...]:
        """"""
        return self.server.Has(*names)

    def SizeOfServer(self) -> int:
        """"""
        return self.server.size

    def StatusOfServer(self) -> server_status_h:
        """"""
        return self.server.status


@d.dataclass(slots=True, repr=False, eq=False)
class client_remote_t(client_t):
    request_line_end: line_end_t | None = None
    answer_line_end: line_end_t | None = None
    # None default added because base_t has attributes with defaults.

    def RequestedData(self, *names) -> h.Any | tuple[h.Any, ...]:
        """"""
        if names.__len__() == 0:
            request = REQUEST_GET
        else:
            request = (REQUEST_GET, *names)
        self.request_line_end.put(request)

        serialized = self.answer_line_end.get()
        deserialized, issues = self.Deserializer(serialized)

        if issues is None:
            return deserialized

        raise RuntimeError(
            f"Un-deserializable object:\n{serialized}\n" + "\n".join(issues)
        )

    def Send(self, /, **data) -> None:
        """"""
        serialized, issues = self.Serializer(data)
        if issues is None:
            self.request_line_end.put((REQUEST_SET, serialized))
        else:
            raise RuntimeError(f"Un-serializable object:\n{data}\n" + "\n".join(issues))

        # Wait for setting confirmation for synchronization purposes. Thus, it will not
        # be possible to set again the same element before the current storage is
        # effective.
        acknowledgment = self.answer_line_end.get()
        if acknowledgment != STORAGE_DONE:
            raise RuntimeError(
                f"Unexpected storage acknowledgment received: {acknowledgment}"
            )

    def RequestDeletion(self, *names) -> None:
        """"""
        self.request_line_end.put((REQUEST_DELETE, *names))

        # Wait for deletion confirmation for synchronization purposes. Thus, the server
        # will not confirm the presence of in-the-course-of-deletion data.
        acknowledgment = self.answer_line_end.get()
        if acknowledgment != DELETION_DONE:
            raise RuntimeError(
                f"Unexpected deletion acknowledgment received: {acknowledgment}"
            )

    def ServerHasData(self, *names) -> bool | tuple[bool, ...]:
        """"""
        if names.__len__() == 0:
            request = REQUEST_CHECK
        else:
            request = (REQUEST_CHECK, *names)
        self.request_line_end.put(request)

        return self.answer_line_end.get()

    def SizeOfServer(self) -> int:
        """"""
        self.request_line_end.put(REQUEST_SIZE)
        return self.answer_line_end.get()

    def StatusOfServer(self) -> server_status_h:
        """"""
        self.request_line_end.put(REQUEST_STATUS)
        return self.answer_line_end.get()
