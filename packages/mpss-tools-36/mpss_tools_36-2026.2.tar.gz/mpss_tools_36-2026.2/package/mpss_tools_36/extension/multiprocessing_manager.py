"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as s
from multiprocessing import process
from multiprocessing.managers import BaseProxy as base_t
from multiprocessing.managers import Token, dispatch, listener_client
from traceback import format_exc


def public_attributes(obj) -> list[str]:
    """"""
    return [
        f".{_}"
        for _ in dir(obj)
        if ((_.__len__() < 2) or (_[:2] != "__")) and not callable(getattr(obj, _))
    ]


def public_methods(obj) -> list[str]:
    """"""
    return [
        _
        for _ in dir(obj)
        if ((_.__len__() < 2) or (_[:2] != "__")) and callable(getattr(obj, _))
    ]


def serve_client(self, conn):
    """"""
    recv = conn.recv
    send = conn.send
    id_to_obj = self.id_to_obj

    while not self.stop_event.is_set():
        method_or_attribute_name = obj = None
        try:
            ident, method_or_attribute_name, args, kwargs = recv()
            try:
                obj, exposed, type_ids = id_to_obj[ident]
            except KeyError as ke:
                try:
                    obj, exposed, type_ids = self.id_to_local_proxy_obj[ident]
                except KeyError:
                    raise ke

            if is_attribute := (method_or_attribute_name[0] == "."):
                method_or_attribute_name = method_or_attribute_name[1:]
                if args.__len__() > 0:
                    setattr(obj, method_or_attribute_name, args[0])
                    actual_method_or_result = None
                else:
                    actual_method_or_result = getattr(obj, method_or_attribute_name)
            else:
                actual_method_or_result = getattr(obj, method_or_attribute_name)

            try:
                if is_attribute:
                    res = actual_method_or_result
                else:
                    res = actual_method_or_result(*args, **kwargs)
            except Exception as e:
                msg = ("#ERROR", e)
            else:
                typeid = type_ids and type_ids.get(method_or_attribute_name, None)
                if typeid:
                    ident_proxy, exposed_proxy = self.create(conn, typeid, res)
                    token = Token(typeid, self.address, ident_proxy)
                    msg = ("#PROXY", (exposed_proxy, token))
                else:
                    msg = ("#RETURN", res)
        except AttributeError:
            if method_or_attribute_name is None:
                msg = ("#TRACEBACK", format_exc())
            else:
                try:
                    fallback_func = self.fallback_mapping[method_or_attribute_name]
                    result = fallback_func(self, conn, ident, obj, *args, **kwargs)
                    msg = ("#RETURN", result)
                except:
                    msg = ("#TRACEBACK", format_exc())
        except EOFError:
            s.exit(0)
        except:
            msg = ("#TRACEBACK", format_exc())

        try:
            try:
                send(msg)
            except:
                send(("#UNSERIALIZABLE", format_exc()))
        except:
            conn.close()
            s.exit(1)


def create(self, c, typeid, /, *args, **kwargs):
    """"""
    with self.mutex:
        NewObject, exposed, method_to_typeid, _ = self.registry[typeid]

        if NewObject is None:
            if kwargs or (len(args) != 1):
                raise ValueError("Without callable, must have one non-keyword argument")
            obj = args[0]
        else:
            obj = NewObject(*args, **kwargs)

        if exposed is None:
            exposed = public_methods(obj) + public_attributes(obj)
        if method_to_typeid is not None:
            if not isinstance(method_to_typeid, dict):
                raise TypeError(
                    "Method_to_typeid {0!r}: type {1!s}, not dict".format(
                        method_to_typeid, type(method_to_typeid)
                    )
                )
            exposed = list(exposed) + list(method_to_typeid)

        ident = "%x" % id(obj)  # convert to string because xmlrpclib
        # only has 32 bit signed integers

        self.id_to_obj[ident] = (obj, set(exposed), method_to_typeid)
        if ident not in self.id_to_refcount:
            self.id_to_refcount[ident] = 0

    self.incref(c, ident)
    return ident, tuple(exposed)


def MakeProxyTypeWithAttributes(name, exposed, _cache={}):
    """"""
    exposed = tuple(exposed)
    try:
        return _cache[(name, exposed)]
    except KeyError:
        pass

    dic = {}

    for meth in exposed:
        if meth[0] == ".":
            exec(
                """@property
def %s(self):
            return self._callmethod(%r, (), {})"""
                % (meth[1:], meth),
                dic,
            )
            exec(
                """@%s.setter
def %s(self, value):
            self._callmethod(%r, (value,), {})"""
                % (meth[1:], meth[1:], meth),
                dic,
            )
        else:
            exec(
                """def %s(self, /, *args, **kwargs):
            return self._callmethod(%r, args, kwargs)"""
                % (meth, meth),
                dic,
            )

    ProxyType = type(name, (base_t,), dic)
    ProxyType._exposed_ = exposed
    _cache[(name, exposed)] = ProxyType

    return ProxyType


def ProxyWithAttributes(
    token,
    serializer,
    manager=None,
    authkey=None,
    exposed=None,
    incref=True,
    manager_owned=False,
):
    """"""
    _Client = listener_client[serializer][1]

    if exposed is None:
        conn = _Client(token.address, authkey=authkey)
        try:
            exposed = dispatch(conn, None, "get_methods", (token,))
        finally:
            conn.close()

    if authkey is None and manager is not None:
        authkey = manager._authkey
    if authkey is None:
        authkey = process.current_process().authkey

    ProxyType = MakeProxyTypeWithAttributes(
        "ProxyWithAttributes[%s]" % token.typeid, exposed
    )
    proxy = ProxyType(
        token,
        serializer,
        manager=manager,
        authkey=authkey,
        incref=incref,
        manager_owned=manager_owned,
    )
    proxy._isauto = True

    return proxy
