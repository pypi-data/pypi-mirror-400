"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d

from p_pattern.constant.shape import DEFAULT_RADIUS_DEFINITION
from p_pattern.type.model.parameter import parameter_t
from p_pattern.type.model.surface import model_t as _base_t


@d.dataclass(slots=True, repr=False, eq=False)
class square_t(_base_t):
    def __post_init__(self) -> None:
        """"""
        _base_t.__post_init__(self)
        self.update(
            {"half_side": DEFAULT_RADIUS_DEFINITION, "angle": parameter_t.NewAngle(0.5)}
        )

    @staticmethod
    def ShapeHeader() -> tuple[str, ...]:
        """"""
        return "Radius", "Angle (radian)"

    @classmethod
    def EducatedShapeHeader(cls) -> tuple[str, ...]:
        """"""
        return cls.ShapeHeader() + ("Angle (degree)",)
