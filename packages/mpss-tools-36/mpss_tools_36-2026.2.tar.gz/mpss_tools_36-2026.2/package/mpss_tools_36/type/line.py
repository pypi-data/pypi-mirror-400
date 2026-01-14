"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from multiprocessing import Queue as NewQueue

line_end_t = type(NewQueue())


class line_t(h.NamedTuple):
    request: line_end_t
    answer: line_end_t
