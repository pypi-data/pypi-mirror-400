"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d

from p_pattern.constant.shape import (
    DEFAULT_RADII_RATIO_LARGER_DEFINITION,
    DEFAULT_RADIUS_DEFINITION,
)
from p_pattern.type.model.parameter import parameter_t
from p_pattern.type.model.surface import model_t as _base_t


@d.dataclass(slots=True, repr=False, eq=False)
class ellipse_t(_base_t):
    def __post_init__(self) -> None:
        """"""
        _base_t.__post_init__(self)
        self.update(
            {
                "semi_minor_axis": DEFAULT_RADIUS_DEFINITION,
                "major_minor_ratio": DEFAULT_RADII_RATIO_LARGER_DEFINITION,
                "angle": parameter_t.NewAngle(1.0),
            }
        )

    @staticmethod
    def ShapeHeader() -> tuple[str, ...]:
        """"""
        return "Semi Minor Axis", "Semi Major Axis", "Angle (radian)"

    @classmethod
    def EducatedShapeHeader(cls) -> tuple[str, ...]:
        """"""
        return cls.ShapeHeader() + ("Angle (degree)",)
