"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d

from p_pattern.constant.shape import DEFAULT_RADIUS_DEFINITION
from p_pattern.type.model.surface import model_t as _base_t


@d.dataclass(slots=True, repr=False, eq=False)
class circle_t(_base_t):
    def __post_init__(self) -> None:
        """"""
        _base_t.__post_init__(self)
        self["radius"] = DEFAULT_RADIUS_DEFINITION

    @staticmethod
    def ShapeHeader() -> tuple[str, ...]:
        """"""
        return ("Radius",)

    @classmethod
    def EducatedShapeHeader(cls) -> tuple[str, ...]:
        """"""
        return cls.ShapeHeader()
