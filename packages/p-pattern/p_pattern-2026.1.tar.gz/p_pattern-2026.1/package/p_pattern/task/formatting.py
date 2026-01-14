"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import numpy as nmpy
from p_pattern.type.instance.parameter.position import position_h


def FormattedPoint(position: position_h, /) -> str:
    """"""
    lengths = position.__len__() * (3,)
    as_str = ",".join(
        f"{_crd:{_lgt}.2f}" for _crd, _lgt in zip(position, lengths, strict=True)
    )
    return f"+({as_str})"


def FormattedAngle(angle: float, /) -> str:
    """"""
    return f"/_{angle * 180.0 / nmpy.pi:5.1f}"


def FormattedExponent(exponent: float, /) -> str:
    """"""
    return f"^{exponent:.2f}"
