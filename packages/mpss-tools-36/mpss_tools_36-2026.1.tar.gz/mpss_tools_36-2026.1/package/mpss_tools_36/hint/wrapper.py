"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

# name, object_type_as_str, is_running.
server_status_h = tuple[str, str, bool]


class client_p(h.Protocol):
    def StatusOfServer(self) -> server_status_h: ...
