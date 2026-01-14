"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

from p_pattern.constant.number import PI_ANGLE
from p_pattern.hint.instance import (
    parameter_h,
    parameter_interval_h,
    parameter_precision_h,
)


@d.dataclass(slots=True, repr=False, eq=False)
class parameter_t:
    """
    min, max: cannot be "infinity".
    min_inclusive, max_inclusive: used only if type is float.
    default_precision:
        - If type is int, None means 1.
        - Otherwise (float), None means "infinite".
    """

    type: type[parameter_h]
    min: parameter_h
    max: parameter_h
    min_inclusive: bool
    max_inclusive: bool
    default_interval: parameter_interval_h
    default_precision: parameter_precision_h

    interval: tuple[parameter_interval_h, parameter_precision_h] = ()

    @classmethod
    def NewAngle(cls, pi_factor: float, /) -> h.Self:
        """"""
        return cls(
            type=float,
            min=0.0,
            max=2.0 * PI_ANGLE,
            min_inclusive=True,
            max_inclusive=False,
            default_interval=(0.0, pi_factor * PI_ANGLE),
            default_precision=(0.5 * pi_factor) * 5.0 * PI_ANGLE / 180.0,
        )
