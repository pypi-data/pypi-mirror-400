"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import multiprocessing as prll
import os as o
import tempfile as tmpf
import time
import types as t
import typing as h
from multiprocessing.managers import BaseManager as base_t
from pathlib import Path as path_t
from threading import Thread as thread_t

from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from mpss_tools_36.extension.data_class import NO_CHOICE
from mpss_tools_36.extension.multiprocessing_manager import (
    ProxyWithAttributes,
    create,
    serve_client,
)

LOCAL_HOST = "127.0.0.1"
PROXY_CONNEXION_PORT = "PROXY_CONNEXION_PORT"
PROXY_CONNEXION_EXTENSION = ".connexion"
SHARING_PROXY = "SharingProxy"


@d.dataclass(init=False, slots=True, repr=False, eq=False)
class server_t(base_t):
    _instances: h.ClassVar[dict[str, h.Any]] = {}

    # The default values below are actually not used since init=False.
    lock: h.Any | None = NO_CHOICE(None)

    _thread: thread_t | None = NO_CHOICE(None)

    @classmethod
    def _AddInstance(cls, instance: h.Any, name: str, /) -> None:
        """"""
        assert prll.current_process().name == MAIN_PROCESS_NAME
        assert name not in cls._instances
        cls._instances[name] = instance

    @classmethod
    def _GetInstance(cls, name: str, /) -> h.Any:
        """"""
        return cls._instances[name]

    def __init__(self, *args, **kwargs) -> None:
        """"""
        cls = self.__class__
        cls.register(
            SHARING_PROXY, callable=cls._GetInstance, proxytype=ProxyWithAttributes
        )
        base_t.__init__(self, *args, **kwargs)
        self._thread = self.lock = None  # Because default __init__ is not used.

    @classmethod
    def New(cls, /, *, instance: h.Any = None, name: str | None = None) -> h.Self:
        """"""
        assert prll.current_process().name == MAIN_PROCESS_NAME

        if instance is not None:
            assert name is not None
            cls._AddInstance(instance, name)

        return cls(address=(LOCAL_HOST, 0))

    def Add(self, instance: h.Any, name: str, /) -> None:
        """"""
        assert prll.current_process().name == MAIN_PROCESS_NAME
        self.__class__._AddInstance(instance, name)

    def Start(self) -> None:
        """"""
        assert prll.current_process().name == MAIN_PROCESS_NAME

        server = self.get_server()
        server.serve_client = t.MethodType(serve_client, server)
        server.create = t.MethodType(create, server)

        self.lock = prll.Lock()

        self._thread = thread_t(target=server.serve_forever, daemon=True)
        self._thread.start()

        port = str(server.address[1])
        if prll.get_start_method() != "spawn":
            o.environ[PROXY_CONNEXION_PORT] = port
        else:
            # With the "spawn" start method, changes to os.environ are not inherited.
            with tmpf.NamedTemporaryFile(
                prefix=f"{PROXY_CONNEXION_PORT}-{time.time_ns()}-",
                suffix=PROXY_CONNEXION_EXTENSION,
                delete=False,
                mode="w",
            ) as accessor:
                accessor.write(port)

    @classmethod
    def Address(cls) -> tuple[str, int] | None:
        """"""
        if prll.get_start_method() != "spawn":
            port = o.environ.get(PROXY_CONNEXION_PORT, None)
            if port is None:
                return None
            return LOCAL_HOST, int(port)

        path = cls.PathOfPort()
        if path is None:
            return None
        return LOCAL_HOST, int(path.read_text())

    @staticmethod
    def PathOfPort() -> path_t | None:
        """"""
        paths = sorted(
            path_t(tmpf.gettempdir()).glob(
                f"{PROXY_CONNEXION_PORT}-*-*{PROXY_CONNEXION_EXTENSION}"
            )
        )
        if paths.__len__() > 0:
            return paths[-1]
        return None

    def Stop(self) -> None:
        """"""
        assert prll.current_process().name == MAIN_PROCESS_NAME

        cls = self.__class__

        cls._instances.clear()
        self._thread = None

        if prll.get_start_method() != "spawn":
            # del o.environ[PROXY_CONNEXION_PORT]  # Raises KeyError(?)
            o.environ[PROXY_CONNEXION_PORT] = ""
        else:
            cls.PathOfPort().unlink()
