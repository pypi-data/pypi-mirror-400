"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

# name, size, {datum_name: datum_type_as_str}, is_read_only, is_running.
server_status_h = tuple[str, int, dict[str, str], bool, bool]


class client_p(h.Protocol):
    def RequestedData(self, *names) -> h.Any | tuple[h.Any, ...]: ...

    def Send(self, /, **data) -> None: ...

    def RequestDeletion(self, *names) -> None: ...

    def ServerHasData(self, *names) -> bool | tuple[bool, ...]: ...

    def SizeOfServer(self) -> int: ...

    def StatusOfServer(self) -> server_status_h: ...
