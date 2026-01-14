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

    folder = path_t(__file__).parent
    paths = site.getsitepackages() + [site.getusersitepackages()]
    for path in paths:
        if folder.is_relative_to(path):
            break
    else:
        beartype_this_package()

from p_pattern.version import __version__
