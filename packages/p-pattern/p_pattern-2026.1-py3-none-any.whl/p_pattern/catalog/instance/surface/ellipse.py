"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import math
from ctypes import c_double, c_size_t, c_void_p

import numpy as nmpy
from p_pattern.catalog.instance.c_extension import RegionImplementationInC
from p_pattern.catalog.instance.surface.superquadric import Normals, Region
from p_pattern.task.formatting import FormattedAngle
from p_pattern.type.instance.surface import instance_t as _base_t
from p_pattern.type.model.parameter import parameter_h

array_t = nmpy.ndarray

_Region_C = RegionImplementationInC(
    __file__,
    (
        c_void_p,
        c_void_p,
        c_size_t,
        c_double,
        c_double,
        c_double,
        c_double,
        c_double,
        c_void_p,
    ),
)

_SEMI_MINOR_AXIS, _MAJOR_MINOR_RATIO, _ANGLE = range(3)


class ellipse_t(_base_t):
    @property
    def educated_shape(self) -> tuple[parameter_h, ...]:
        """"""
        return (
            self.shape[_SEMI_MINOR_AXIS],
            self.shape[_SEMI_MINOR_AXIS] * self.shape[_MAJOR_MINOR_RATIO],
            self.shape[_ANGLE],
            self.shape[_ANGLE] * 180.0 / math.pi,
        )

    def _CoarseBoundingBoxHalfLengths(self) -> tuple[int, ...]:
        """"""
        s_min_a_2 = float(self.shape[_SEMI_MINOR_AXIS]) ** 2
        s_maj_a_2 = s_min_a_2 * self.shape[_MAJOR_MINOR_RATIO] ** 2

        cos_2 = math.cos(self.shape[_ANGLE]) ** 2
        sin_2 = math.sin(self.shape[_ANGLE]) ** 2

        half_length_row = math.ceil(
            math.sqrt(s_min_a_2 * cos_2 + s_maj_a_2 * sin_2)
        ).__int__()
        half_length_col = math.ceil(
            math.sqrt(s_min_a_2 * sin_2 + s_maj_a_2 * cos_2)
        ).__int__()

        return half_length_row, half_length_col

    def _Region(self, grid_sites: tuple[array_t, ...], /) -> array_t:
        """"""
        return Region(
            self.shape[_SEMI_MINOR_AXIS],
            self.shape[_MAJOR_MINOR_RATIO],
            None,
            None,
            self.shape[_ANGLE],
            self.position,
            self.bbox.domain,
            _Region_C,
            grid_sites,
        )

    def Normals(self) -> tuple[tuple[array_t, ...] | None, array_t | None]:
        """"""
        cache_entry = self.Normals.__name__

        if cache_entry not in self._cache:
            self._cache[cache_entry] = Normals(
                self.shape[_SEMI_MINOR_AXIS],
                self.shape[_MAJOR_MINOR_RATIO],
                None,
                None,
                self.shape[_ANGLE],
                self.position,
                self.bbox.min_s,
                self.Contour(),
            )

        return self._cache[cache_entry]

    def _RadiusForSimilarPositions(self, /, *, fraction: float = 0.1) -> float:
        """"""
        return (
            0.5
            * fraction
            * self.shape[_SEMI_MINOR_AXIS]
            * (1.0 + self.shape[_MAJOR_MINOR_RATIO])
        )

    def FormattedShape(self) -> str:
        """"""
        semi_minor_axis = self.shape[_SEMI_MINOR_AXIS]
        semi_major_axis = semi_minor_axis * self.shape[_MAJOR_MINOR_RATIO]
        return f"{semi_minor_axis:.2f}x{semi_major_axis:.2f}" + FormattedAngle(
            self.shape[_ANGLE]
        )
