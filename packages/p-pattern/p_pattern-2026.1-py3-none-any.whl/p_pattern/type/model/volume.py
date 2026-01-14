"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d

from p_pattern.type.model.generic import model_t as _base_t


@d.dataclass(slots=True, repr=False, eq=False)
class model_t(_base_t):
    def __post_init__(self) -> None:
        """"""
        self.dimension = 3

    @staticmethod
    def PositionHeader() -> tuple[str, ...]:
        """"""
        return "Row", "Col", "Dep"
