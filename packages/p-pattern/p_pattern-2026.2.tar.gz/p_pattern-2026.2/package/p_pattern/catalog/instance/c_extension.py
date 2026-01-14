"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import platform as pltf
import typing as h
from ctypes import cdll
from pathlib import Path as path_t
from sys import platform as OS_TYPE

_EXTENSION_FOLDER = "c_extension"
_EXTENSION_EXTENSION = "so"


def RegionImplementationInC(from_module: str, arguments: tuple, /) -> h.Any:
    """"""
    path = path_t(from_module)
    # Keep in sync with make.sh.
    extension = (
        path.parent
        / _EXTENSION_FOLDER
        / f"{path.stem}-{OS_TYPE}-{pltf.machine()}.{_EXTENSION_EXTENSION}"
    )
    if extension.is_file():
        try:
            library = cdll.LoadLibrary(str(extension))
        except OSError:
            return None

        output = library.Region
        output.argtypes = arguments
        output.restype = None

        return output

    return None
