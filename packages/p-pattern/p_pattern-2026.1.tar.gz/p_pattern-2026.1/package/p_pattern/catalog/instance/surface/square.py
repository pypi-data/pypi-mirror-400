"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import numpy as nmpy
from p_pattern.catalog.instance.surface.rectangle import (
    CoarseBoundingBoxHalfLengths,
    Normals,
    Region,
)
from p_pattern.task.formatting import FormattedAngle
from p_pattern.type.instance.surface import instance_t as _base_t
from p_pattern.type.model.parameter import parameter_h

array_t = nmpy.ndarray

_HALF_SIDE, _ANGLE = range(2)


class square_t(_base_t):
    @property
    def educated_shape(self) -> tuple[parameter_h, ...]:
        """"""
        return (
            self.shape[_HALF_SIDE],
            self.shape[_ANGLE],
            self.shape[_ANGLE] * 180.0 / nmpy.pi,
        )

    def _CoarseBoundingBoxHalfLengths(self) -> tuple[int, ...]:
        """"""
        return CoarseBoundingBoxHalfLengths(
            self.shape[_HALF_SIDE], 1.0, self.shape[_ANGLE]
        )

    def _Region(self, grid_sites: tuple[array_t, ...], /) -> array_t:
        """"""
        return Region(
            self.shape[_HALF_SIDE],
            1.0,
            self.shape[_ANGLE],
            self.position,
            self.bbox.domain,
            grid_sites,
        )

    def Normals(self) -> tuple[tuple[array_t, ...] | None, array_t | None]:
        """"""
        cache_entry = self.Normals.__name__

        if cache_entry not in self._cache:
            self._cache[cache_entry] = Normals(
                1.0,
                self.shape[_ANGLE],
                self.position,
                self.bbox.min_s,
                self.crosses_border,
                self.Contour(),
            )

        return self._cache[cache_entry]

    def _RadiusForSimilarPositions(self, /, *, fraction: float = 0.1) -> float:
        """"""
        return 0.5 * fraction * self.shape[_HALF_SIDE] * (1.0 + 1.0)

    def FormattedShape(self) -> str:
        """"""
        return f"{self.shape[_HALF_SIDE]:.2f}" + FormattedAngle(self.shape[_ANGLE])
