"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

from mpss_tools_36.constant.generic import REQUEST_STATUS
from mpss_tools_36.constant.wrapper import (
    REQUEST_ATTRIBUTE,
    REQUEST_ATTRIBUTES,
    REQUEST_CALL,
    REQUEST_METHODS,
)
from mpss_tools_36.extension.data_class import NO_CHOICE
from mpss_tools_36.hint.serializer import Deserializer_h, Serializer_h
from mpss_tools_36.hint.wrapper import server_status_h
from mpss_tools_36.type.line import line_end_t, line_t
from mpss_tools_36.type.server.wrapper import server_t


@d.dataclass(slots=True, repr=False, eq=False)
class proxy_t:
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
    ) -> proxy_direct_t | proxy_remote_t:
        """"""
        if server is None:
            return proxy_remote_t(
                request_line_end=server_line.request, answer_line_end=server_line.answer
            )
        return proxy_direct_t(server=server)


@d.dataclass(slots=True, repr=False, eq=False)
class proxy_direct_t(proxy_t):
    server: server_t | None = None
    # None default added because base_t has attributes with defaults.

    def __getattr__(self, item: str, /) -> h.Callable:
        """"""
        return getattr(self.server.object, item)

    def __setattr__(self, item: str, value: h.Any, /) -> None:
        """"""
        setattr(self.server.object, item, value)

    def StatusOfServer(self) -> server_status_h:
        """"""
        return self.server.status


@d.dataclass(slots=True, repr=False, eq=False)
class proxy_remote_t(proxy_t):
    request_line_end: line_end_t | None = None
    answer_line_end: line_end_t | None = None
    # None default added because base_t has attributes with defaults.

    _object_attributes: tuple[str, ...] = d.field(init=False)
    _object_methods: tuple[str, ...] = d.field(init=False)
    _object_method_proxies: dict[str, h.Callable] = NO_CHOICE(dict)

    def __post_init__(self) -> None:
        """"""
        proxy_t.__post_init__(self)

        self._object_attributes = self._SendRequest(REQUEST_ATTRIBUTES)
        self._object_methods = self._SendRequest(REQUEST_METHODS)

    def __getattr__(self, item: str, /) -> h.Callable:
        """"""
        if item in self._object_attributes:
            return self._SendRequest((REQUEST_ATTRIBUTE, item))

        if item in self._object_methods:
            output = getattr(self._object_method_proxies, item, None)

            if output is None:

                def output(*args, **kwargs) -> h.Callable:
                    #
                    args_serialized, issues = self.Serializer(args)
                    if issues is not None:
                        raise RuntimeError(
                            f"Un-serializable object:\n{type(args).__name__}\n"
                            + "\n".join(issues)
                        )
                    kwargs_serialized, issues = self.Serializer(kwargs)
                    if issues is not None:
                        raise RuntimeError(
                            f"Un-serializable object:\n{type(kwargs).__name__}\n"
                            + "\n".join(issues)
                        )
                    return self._SendRequest(
                        (REQUEST_CALL, item, args_serialized, kwargs_serialized)
                    )

                self._object_method_proxies[item] = output

            return output

        raise AttributeError(f'Instance {self} has no attribute "{item}".')

    def __setattr__(self, item: str, value: h.Any, /) -> None:
        """"""
        try:
            attributes = object.__getattribute__(self, "_object_attributes")
        except AttributeError:
            attributes = ()
        if item in attributes:
            serialized, issues = self.Serializer((item, value))
            if issues is not None:
                raise RuntimeError(
                    f"Un-serializable object:\n{type(value).__name__}\n"
                    + "\n".join(issues)
                )
            _ = self._SendRequest((REQUEST_CALL, "__setattr__", serialized))
        else:
            object.__setattr__(self, item, value)

    def _SendRequest(self, request: str | tuple, /) -> h.Any:
        """"""
        self.request_line_end.put(request)

        serialized = self.answer_line_end.get()
        deserialized, issues = self.Deserializer(serialized)

        if issues is None:
            return deserialized

        raise RuntimeError(
            f"Un-deserializable object:\n{serialized}\n" + "\n".join(issues)
        )

    def StatusOfServer(self) -> server_status_h:
        """"""
        self.request_line_end.put(REQUEST_STATUS)
        return self.answer_line_end.get()
