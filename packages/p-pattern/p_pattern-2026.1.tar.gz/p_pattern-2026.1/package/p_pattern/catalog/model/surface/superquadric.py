"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d

from p_pattern.constant.shape import (
    DEFAULT_POSITIVE_EXPONENT_DEFINITION,
    DEFAULT_RADII_RATIO_LARGER_DEFINITION,
    DEFAULT_RADIUS_DEFINITION,
)
from p_pattern.type.model.parameter import (
    parameter_h,
    parameter_interval_h,
    parameter_precision_h,
    parameter_t,
)
from p_pattern.type.model.surface import model_t as _base_t


@d.dataclass(slots=True, repr=False, eq=False)
class superquadric_t(_base_t):
    """
    minor_exponent: exponent corresponding to the minor axis ("minor" is not in the
    sense of "smallest").
    """

    def __post_init__(self) -> None:
        """"""
        _base_t.__post_init__(self)
        self.update(
            {
                "semi_minor_axis": DEFAULT_RADIUS_DEFINITION,
                "major_minor_ratio": DEFAULT_RADII_RATIO_LARGER_DEFINITION,
                "minor_exponent": DEFAULT_POSITIVE_EXPONENT_DEFINITION,
                "major_exponent": DEFAULT_POSITIVE_EXPONENT_DEFINITION,
                "angle": parameter_t.NewAngle(1.0),
            }
        )

    def SetShapeIntervals(
        self,
        ranges: dict[
            str,
            parameter_interval_h
            | tuple[parameter_h, parameter_h, parameter_precision_h],
        ],
        /,
    ) -> None:
        """"""
        if "exponent" in ranges:
            ranges = ranges.copy()
            ranges["minor_exponent"] = ranges["major_exponent"] = ranges["exponent"]
            del ranges["exponent"]

        _base_t.SetShapeIntervals(self, ranges)

    @staticmethod
    def ShapeHeader() -> tuple[str, ...]:
        """"""
        return (
            "Semi Minor Axis",
            "Semi Major Axis",
            "Exp of S.Min.A",
            "Exp of S.Maj.A",
            "Angle (radian)",
        )

    @classmethod
    def EducatedShapeHeader(cls) -> tuple[str, ...]:
        """"""
        return cls.ShapeHeader() + ("Angle (degree)",)
