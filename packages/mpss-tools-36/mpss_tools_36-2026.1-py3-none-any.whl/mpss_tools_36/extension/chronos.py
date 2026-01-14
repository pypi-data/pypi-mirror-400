"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import time


def FormatedDuration(duration: float, /) -> str:
    """"""
    if duration >= 86400:
        return "1d+"

    output = time.strftime("%Hh%Mm%Ss", time.gmtime(duration))
    while output.startswith("00"):
        output = output[3:]

    if output.__len__() > 0:
        return output
    return "00s"
