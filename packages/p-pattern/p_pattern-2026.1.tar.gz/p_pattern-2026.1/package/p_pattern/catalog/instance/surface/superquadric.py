"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import math
import typing as h
from ctypes import c_double, c_size_t, c_void_p

import numpy as nmpy
from p_pattern.catalog.instance.c_extension import RegionImplementationInC
from p_pattern.task.formatting import FormattedAngle, FormattedExponent
from p_pattern.type.instance.parameter.position import position_h
from p_pattern.type.instance.surface import instance_t as _base_t
from p_pattern.type.model.parameter import parameter_h
from p_pattern.type.sampler.domain import domain_indexer_h

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
        c_double,
        c_double,
        c_void_p,
    ),
)


_SEMI_MINOR_AXIS, _MAJOR_MINOR_RATIO, _MINOR_EXPONENT, _MAJOR_EXPONENT, _ANGLE = range(
    5
)


class superquadric_t(_base_t):
    @property
    def educated_shape(self) -> tuple[parameter_h, ...]:
        """"""
        return (
            self.shape[_SEMI_MINOR_AXIS],
            self.shape[_SEMI_MINOR_AXIS] * self.shape[_MAJOR_MINOR_RATIO],
            self.shape[_MINOR_EXPONENT],
            self.shape[_MAJOR_EXPONENT],
            self.shape[_ANGLE],
            self.shape[_ANGLE] * 180.0 / math.pi,
        )

    def _CoarseBoundingBoxHalfLengths(self) -> tuple[int, ...]:
        """"""
        semi_major_axis = math.ceil(
            self.shape[_SEMI_MINOR_AXIS] * self.shape[_MAJOR_MINOR_RATIO]
        ).__int__()

        return semi_major_axis, semi_major_axis

    def _Region(self, grid_sites: tuple[array_t, ...], /) -> array_t:
        """
        Alternative, faster or not, implementation: compute only in the first quadrant,
        then copy 2 times by flipping, then rotate with scipy.ndimage.rotate or
        skimage.transform.rotate. Put max value in pixels outside the domain. This
        alternative is valid because the bbox is a square corresponding to the unrotated
        superquadric. (Does it change anything to the management of out-of-domain
        pixels?)
        """
        return Region(
            self.shape[_SEMI_MINOR_AXIS],
            self.shape[_MAJOR_MINOR_RATIO],
            self.shape[_MINOR_EXPONENT],
            self.shape[_MAJOR_EXPONENT],
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
                self.shape[_MINOR_EXPONENT],
                self.shape[_MAJOR_EXPONENT],
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
        return (
            f"{semi_minor_axis:.2f}x{semi_major_axis:.2f}"
            + FormattedExponent(self.shape[_MINOR_EXPONENT])
            + FormattedExponent(self.shape[_MAJOR_EXPONENT])
            + FormattedAngle(self.shape[_ANGLE])
        )


def Region(
    semi_minor_axis: float,
    major_minor_ratio: float | None,
    minor_exponent: float | None,
    major_exponent: float | None,
    angle: float | None,
    point: position_h,
    domain: domain_indexer_h,
    Region_C: h.Callable | None,
    grid_sites: tuple[array_t, ...],
    /,
) -> array_t:
    """"""
    if Region_C is None:
        centered_rows = grid_sites[0][domain] - point[0]
        centered_cols = grid_sites[1][domain] - point[1]

        if angle is None:
            # Circle.
            sq_1_level_map = (centered_rows**2 + centered_cols**2) * (
                1.0 / semi_minor_axis**2
            )
        else:
            cos = math.cos(angle)
            sin = math.sin(angle)
            rotated_rows = sin * centered_cols + cos * centered_rows
            rotated_cols = cos * centered_cols - sin * centered_rows

            if minor_exponent is None:
                # Ellipse.
                semi_major_axis = semi_minor_axis * major_minor_ratio
                sq_1_level_map = rotated_rows**2 * (
                    1.0 / semi_minor_axis**2
                ) + rotated_cols**2 * (1.0 / semi_major_axis**2)
            else:
                minor_power = nmpy.power(nmpy.fabs(rotated_rows), minor_exponent)
                major_power = nmpy.power(nmpy.fabs(rotated_cols), major_exponent)
                minor_factor = 1.0 / semi_minor_axis**minor_exponent
                major_factor = (
                    1.0 / (semi_minor_axis * major_minor_ratio) ** major_exponent
                )

                sq_1_level_map = minor_power * minor_factor + major_power * major_factor

        region = sq_1_level_map <= 1.0
    else:
        bbox_grid_rows = nmpy.array(
            grid_sites[0][domain], dtype=nmpy.float64, order="C"
        )
        bbox_grid_cols = nmpy.array(
            grid_sites[1][domain], dtype=nmpy.float64, order="C"
        )
        region = nmpy.empty_like(bbox_grid_rows, dtype=nmpy.bool_)
        if angle is None:
            # Circle.
            Region_C(
                bbox_grid_rows.ctypes.data,
                bbox_grid_cols.ctypes.data,
                bbox_grid_rows.size,
                *point,
                semi_minor_axis,
                region.ctypes.data,
            )
        elif minor_exponent is None:
            # Ellipse.
            Region_C(
                bbox_grid_rows.ctypes.data,
                bbox_grid_cols.ctypes.data,
                bbox_grid_rows.size,
                *point,
                semi_minor_axis,
                major_minor_ratio,
                angle,
                region.ctypes.data,
            )
        else:
            Region_C(
                bbox_grid_rows.ctypes.data,
                bbox_grid_cols.ctypes.data,
                bbox_grid_rows.size,
                *point,
                semi_minor_axis,
                major_minor_ratio,
                minor_exponent,
                major_exponent,
                angle,
                region.ctypes.data,
            )

    return region


def Normals(
    semi_minor_axis: float,
    major_minor_ratio: float,
    minor_exponent: float | None,
    major_exponent: float | None,
    angle: float,
    point: position_h,
    min_s: tuple[int, ...],
    contour: array_t,
    /,
) -> tuple[tuple[array_t, ...] | None, array_t | None]:
    """"""
    sites = contour.nonzero()
    if sites[0].size == 0:
        return None, None

    rotation = nmpy.empty((2, 2), dtype=nmpy.float64, order="C")
    rotation[0, 0] = nmpy.cos(angle)
    rotation[1, 0] = nmpy.sin(angle)
    rotation[0, 1] = -rotation[1, 0]
    rotation[1, 1] = rotation[0, 0]

    un_rotated_sites = (
        nmpy.transpose(sites).astype(nmpy.float64)
        + [[min_s[0] - point[0], min_s[1] - point[1]]]
    ) @ rotation

    normals = un_rotated_sites
    if minor_exponent is None:
        normals[:, 0] /= semi_minor_axis**2
        normals[:, 1] /= (semi_minor_axis * major_minor_ratio) ** 2
    else:
        row_signs = nmpy.sign(normals[:, 0])
        col_signs = nmpy.sign(normals[:, 1])
        normals[:, 0] = (
            nmpy.power(nmpy.fabs(normals[:, 0]), minor_exponent - 1.0) * row_signs
        )
        normals[:, 1] = (
            nmpy.power(nmpy.fabs(normals[:, 1]), major_exponent - 1.0) * col_signs
        )
        normals[:, 0] *= minor_exponent / semi_minor_axis**minor_exponent
        normals[:, 1] *= (
            major_exponent / (semi_minor_axis * major_minor_ratio) ** major_exponent
        )

    normals = normals @ rotation.transpose()
    normal_norms = nmpy.sqrt((normals**2).sum(axis=1, keepdims=True))
    # When the analytical normal expression is evaluated at (0,0), it
    # results in a null normal. This occurs whenever the contour "passes
    # through the center" (very thick contour and/or very thin object).
    normal_norms[normal_norms == 0.0] = 1.0
    normals /= normal_norms

    return sites, normals
