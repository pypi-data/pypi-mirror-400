"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import math
from ctypes import c_double, c_size_t, c_void_p

import numpy as nmpy
from p_pattern.catalog.instance.c_extension import RegionImplementationInC
from p_pattern.task.formatting import FormattedAngle
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
        c_void_p,
    ),
)

_HALF_SMALL_LENGTH, _LARGE_SMALL_RATIO, _ANGLE = range(3)


class rectangle_t(_base_t):
    @property
    def educated_shape(self) -> tuple[parameter_h, ...]:
        """"""
        return (
            self.shape[_HALF_SMALL_LENGTH],
            self.shape[_HALF_SMALL_LENGTH] * self.shape[_LARGE_SMALL_RATIO],
            self.shape[_ANGLE],
            self.shape[_ANGLE] * 180.0 / math.pi,
        )

    def _CoarseBoundingBoxHalfLengths(self) -> tuple[int, ...]:
        """"""
        return CoarseBoundingBoxHalfLengths(*self.shape)

    def _Region(self, grid_sites: tuple[array_t, ...], /) -> array_t:
        """"""
        return Region(*self.shape, self.position, self.bbox.domain, grid_sites)

    def Normals(self) -> tuple[tuple[array_t, ...] | None, array_t | None]:
        """"""
        cache_entry = self.Normals.__name__

        if cache_entry not in self._cache:
            self._cache[cache_entry] = Normals(
                self.shape[_LARGE_SMALL_RATIO],
                self.shape[_ANGLE],
                self.position,
                self.bbox.min_s,
                self.crosses_border,
                self.Contour(),
            )

        return self._cache[cache_entry]

    def _RadiusForSimilarPositions(self, /, *, fraction: float = 0.1) -> float:
        """"""
        return (
            0.5
            * fraction
            * self.shape[_HALF_SMALL_LENGTH]
            * (1.0 + self.shape[_LARGE_SMALL_RATIO])
        )

    def FormattedShape(self) -> str:
        """"""
        half_small_length = self.shape[_HALF_SMALL_LENGTH]
        half_large_length = half_small_length * self.shape[_LARGE_SMALL_RATIO]
        return f"{half_small_length:.2f}x{half_large_length:.2f}" + FormattedAngle(
            self.shape[_ANGLE]
        )


def CoarseBoundingBoxHalfLengths(
    semi_minor_axis: float, major_minor_ratio: float, angle: float, /
) -> tuple[int, ...]:
    """"""
    s_min_a_2 = semi_minor_axis
    s_maj_a_2 = s_min_a_2 * major_minor_ratio

    abs_cos = abs(math.cos(angle))
    abs_sin = abs(math.sin(angle))

    half_length_row = math.ceil(s_min_a_2 * abs_cos + s_maj_a_2 * abs_sin).__int__()
    half_length_col = math.ceil(s_min_a_2 * abs_sin + s_maj_a_2 * abs_cos).__int__()

    return half_length_row, half_length_col


def Region(
    semi_minor_axis: float,
    major_minor_ratio: float,
    angle: float,
    point: position_h,
    domain: domain_indexer_h,
    grid_sites: tuple[array_t, ...],
    /,
) -> array_t:
    """"""
    if _Region_C is None:
        centered_rows = grid_sites[0][domain] - point[0]
        centered_cols = grid_sites[1][domain] - point[1]

        cos = math.cos(angle)
        sin = math.sin(angle)
        rotated_rows = sin * centered_cols + cos * centered_rows
        rotated_cols = cos * centered_cols - sin * centered_rows

        semi_major_axis = semi_minor_axis * major_minor_ratio
        sq_1_level_map = nmpy.fmax(
            nmpy.fabs(rotated_rows * (1.0 / semi_minor_axis)),
            nmpy.fabs(rotated_cols * (1.0 / semi_major_axis)),
        )
        region = sq_1_level_map <= 1.0
    else:
        bbox_grid_rows = nmpy.array(
            grid_sites[0][domain], dtype=nmpy.float64, order="C"
        )
        bbox_grid_cols = nmpy.array(
            grid_sites[1][domain], dtype=nmpy.float64, order="C"
        )
        region = nmpy.empty_like(bbox_grid_rows, dtype=nmpy.bool_)
        _Region_C(
            bbox_grid_rows.ctypes.data,
            bbox_grid_cols.ctypes.data,
            bbox_grid_rows.size,
            *point,
            semi_minor_axis,
            major_minor_ratio,
            angle,
            region.ctypes.data,
        )

    return region


def Normals(
    major_minor_ratio: float,
    angle: float,
    point: position_h,
    min_s: tuple[int, ...],
    crosses_border: bool,
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
    site_norms = nmpy.sqrt((un_rotated_sites**2).sum(axis=1))
    if crosses_border:
        # The line below is useless in general. It is necessary when the shape is
        # partially outside the image domain, with its center on the border. In this
        # case, the analytical normal expression is evaluated at (0,0), which results in
        # a null normal.
        site_norms[site_norms == 0.0] = 1.0

    site_angles = nmpy.arccos(un_rotated_sites[:, 0] / site_norms)
    limit_angle = math.atan(major_minor_ratio)
    col_edges = nmpy.logical_or(
        site_angles < limit_angle, site_angles > math.pi - limit_angle
    )
    row_edges = nmpy.logical_not(col_edges)

    normals = nmpy.empty_like(un_rotated_sites)
    normals[col_edges, 0] = nmpy.sign(un_rotated_sites[col_edges, 0])
    normals[col_edges, 1] = 0.0
    normals[row_edges, 0] = 0.0
    normals[row_edges, 1] = nmpy.sign(un_rotated_sites[row_edges, 1])

    normals = normals @ rotation.transpose()

    return sites, normals
