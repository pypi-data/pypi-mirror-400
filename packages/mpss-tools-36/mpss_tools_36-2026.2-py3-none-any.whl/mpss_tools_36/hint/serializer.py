"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

original_h = h.Any
serialized_h = bytes | str
issues_h = list[str] | None

Serializer_h = h.Callable[[original_h], tuple[serialized_h, issues_h]]
Deserializer_h = h.Callable[[serialized_h], tuple[original_h, issues_h]]
