"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import functools as f
import multiprocessing as prll
import types as t
import typing as h

from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from mpss_tools_36.type.client.sharer import proxy_t
from mpss_tools_36.type.server.sharer import server_t


def MakeShareable(singleton: h.Any, /, *, name: str | None = None) -> None:
    """"""
    if (name is None) or (name == ""):
        function = ToggleShareability
    else:
        function = f.partial(ToggleShareability, name=name)

    _CheckAttributeAddition(singleton, "ToggleShareability")
    singleton.ToggleShareability = t.MethodType(function, singleton)


def ToggleShareability(
    singleton: h.Any, state: bool, /, *, name: str | None = None
) -> None:
    """
    The singleton creation should be functionally equivalent to:
    from mpss_tools_36.api.sharer import proxy_t
    if multiprocessing.current_process().name == "MainProcess":
        singleton = singleton_t(name=SINGLETON_NAME)
    else:
        singleton = proxy_t.SharedInstanceProxy(SINGLETON_NAME)
    However, with the fork process start method, subprocesses will not re-import the
    singleton-creation module. Instead, the singleton instance will be duplicated and
    "passed" to sub-processes, preventing the sharing mechanism from being triggered by
    re-importation. As a workaround, a sharing proxy should be created and added to the
    singleton instance.
    """
    assert prll.current_process().name == MAIN_PROCESS_NAME

    if state:
        has_server_attribute = hasattr(singleton, "server")
        if has_server_attribute and (singleton.server is not None):
            return

        if not has_server_attribute:
            _CheckAttributeAddition(singleton, "server")

        if not hasattr(singleton, "name"):
            _CheckAttributeAddition(singleton, "name")
            if (name is None) or (name == ""):
                name = f"{type(singleton).__name__}-{id(singleton)}"
            singleton.name = name

        singleton.server = server_t.New(instance=singleton, name=singleton.name)
        singleton.server.Start()

        if prll.get_start_method() == "fork":
            if not hasattr(singleton, "proxy"):
                _CheckAttributeAddition(singleton, "proxy")
            singleton.proxy = proxy_t.SharedInstanceProxy(singleton.name)
    else:
        if (not hasattr(singleton, "server")) or (singleton.server is None):
            return

        singleton.server.Stop()
        singleton.server = None
        if hasattr(singleton, "proxy"):
            singleton.proxy = None


def _CheckAttributeAddition(obj: h.Any, attribute: str, /) -> None:
    """"""
    try:
        setattr(obj, attribute, None)
    except AttributeError:
        if hasattr(obj, "__slots__"):
            reason = " because it has slots"
        else:
            reason = ""
        raise AttributeError(
            f'Object {obj} has no "{attribute}" attribute, '
            f"and does not accept its addition{reason}."
        )
