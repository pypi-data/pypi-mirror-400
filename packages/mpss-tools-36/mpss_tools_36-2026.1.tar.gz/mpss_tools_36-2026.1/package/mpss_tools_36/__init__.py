"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

try:
    from beartype.claw import beartype_this_package  # noqa
except ModuleNotFoundError:
    pass
else:
    import site
    from pathlib import Path as path_t

    paths = site.getsitepackages() + [site.getusersitepackages()]
    folder = path_t(__file__).parent
    if folder not in paths:
        beartype_this_package()

from mpss_tools_36.version import __version__
