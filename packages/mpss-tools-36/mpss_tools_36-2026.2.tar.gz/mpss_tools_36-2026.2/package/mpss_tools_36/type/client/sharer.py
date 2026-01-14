"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

from mpss_tools_36.type.server.sharer import SHARING_PROXY, server_t


@d.dataclass(init=False, slots=True, repr=False, eq=False)
class proxy_t:
    @staticmethod
    def SharedInstanceProxy(name: str, /) -> h.Any:
        """"""
        address = server_t.Address()
        if address is None:
            return None

        sharer = server_t(address=address)
        sharer.connect()

        return getattr(sharer, SHARING_PROXY)(name)
