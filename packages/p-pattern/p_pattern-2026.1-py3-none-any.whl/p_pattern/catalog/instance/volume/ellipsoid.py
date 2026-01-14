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
from p_pattern.type.instance.volume import instance_t as _base_t
from p_pattern.type.model.parameter import parameter_h

array_t = nmpy.ndarray

_Region_C = RegionImplementationInC(
    __file__,
    (
        c_void_p,
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
        c_double,
        c_void_p,
    ),
)

_SEMI_MINOR_AXIS, _MAJOR_MINOR_RATIO, _THIRD_MINOR_RATIO, _RC_ANGLE, _RD_ANGLE = range(
    5
)


class ellipsoid_t(_base_t):
    # TODO: The sampling is probably not uniform due to absence of constraint on
    #     third_minor_ratio.

    @property
    def educated_shape(self) -> tuple[parameter_h, ...]:
        """"""
        return (
            self.shape[_SEMI_MINOR_AXIS],
            self.shape[_SEMI_MINOR_AXIS] * self.shape[_MAJOR_MINOR_RATIO],
            self.shape[_SEMI_MINOR_AXIS] * self.shape[_THIRD_MINOR_RATIO],
            self.shape[_RC_ANGLE],
            self.shape[_RC_ANGLE] * 180.0 / math.pi,
            self.shape[_RD_ANGLE],
            self.shape[_RD_ANGLE] * 180.0 / math.pi,
        )

    def _CoarseBoundingBoxHalfLengths(self) -> tuple[int, ...]:
        """"""
        semi_major_axis = math.ceil(
            self.shape[_SEMI_MINOR_AXIS] * self.shape[_MAJOR_MINOR_RATIO]
        ).__int__()
        semi_third_axis = math.ceil(
            self.shape[_SEMI_MINOR_AXIS] * self.shape[_THIRD_MINOR_RATIO]
        ).__int__()
        radius = max(semi_major_axis, semi_third_axis)

        return radius, radius, radius

    def _Region(self, grid_sites: tuple[array_t, ...], /) -> array_t:
        """"""
        if _Region_C is None:
            centered_rows = grid_sites[0][self.bbox.domain] - self.position[0]
            centered_cols = grid_sites[1][self.bbox.domain] - self.position[1]
            centered_deps = grid_sites[2][self.bbox.domain] - self.position[2]

            cos_rc = math.cos(self.shape[_RC_ANGLE])
            sin_rc = math.sin(self.shape[_RC_ANGLE])
            rotated_rows = sin_rc * centered_cols + cos_rc * centered_rows

            cos_rd = math.cos(self.shape[_RD_ANGLE])
            sin_rd = math.sin(self.shape[_RD_ANGLE])
            re_rotated_rows = sin_rd * centered_deps + cos_rd * rotated_rows
            re_rotated_cols = cos_rc * centered_cols - sin_rc * centered_rows
            re_rotated_deps = cos_rd * centered_deps - sin_rd * rotated_rows

            semi_minor_axis = self.shape[_SEMI_MINOR_AXIS]
            semi_major_axis = semi_minor_axis * self.shape[_MAJOR_MINOR_RATIO]
            semi_third_axis = semi_minor_axis * self.shape[_THIRD_MINOR_RATIO]
            sq_1_level_map = (
                re_rotated_rows**2 * (1.0 / semi_minor_axis**2)
                + re_rotated_cols**2 * (1.0 / semi_major_axis**2)
                + re_rotated_deps**2 * (1.0 / semi_third_axis**2)
            )
            region = sq_1_level_map <= 1.0
        else:
            bbox_grid_rows = nmpy.array(
                grid_sites[0][self.bbox.domain], dtype=nmpy.float64, order="C"
            )
            bbox_grid_cols = nmpy.array(
                grid_sites[1][self.bbox.domain], dtype=nmpy.float64, order="C"
            )
            bbox_grid_deps = nmpy.array(
                grid_sites[2][self.bbox.domain], dtype=nmpy.float64, order="C"
            )
            region = nmpy.empty_like(bbox_grid_rows, dtype=nmpy.bool_)
            _Region_C(
                bbox_grid_rows.ctypes.data,
                bbox_grid_cols.ctypes.data,
                bbox_grid_deps.ctypes.data,
                bbox_grid_rows.size,
                *self.position,
                self.shape[_SEMI_MINOR_AXIS],
                self.shape[_MAJOR_MINOR_RATIO],
                self.shape[_THIRD_MINOR_RATIO],
                self.shape[_RC_ANGLE],
                self.shape[_RD_ANGLE],
                region.ctypes.data,
            )

        return region

    def Normals(self) -> tuple[tuple[array_t, ...] | None, array_t | None]:
        """"""
        cache_entry = self.Normals.__name__

        if cache_entry not in self._cache:
            contour = self.Contour()
            sites = contour.nonzero()

            if sites[0].size > 0:
                rd_rotation = nmpy.zeros((3, 3), dtype=nmpy.float64, order="C")
                rd_rotation[0, 0] = nmpy.cos(self.shape[_RD_ANGLE])
                rd_rotation[2, 0] = nmpy.sin(self.shape[_RD_ANGLE])
                rd_rotation[0, 2] = -rd_rotation[2, 0]
                rd_rotation[2, 2] = rd_rotation[0, 0]
                rd_rotation[1, 1] = 1.0

                rc_rotation = nmpy.zeros((3, 3), dtype=nmpy.float64, order="C")
                rc_rotation[0, 0] = nmpy.cos(self.shape[_RC_ANGLE])
                rc_rotation[1, 0] = nmpy.sin(self.shape[_RC_ANGLE])
                rc_rotation[0, 1] = -rc_rotation[1, 0]
                rc_rotation[1, 1] = rc_rotation[0, 0]
                rc_rotation[2, 2] = 1.0

                rotation = rd_rotation @ rc_rotation

                un_rotated_sites = (
                    nmpy.transpose(sites).astype(nmpy.float64)
                    + [
                        [
                            self.bbox.min_s[0] - self.position[0],
                            self.bbox.min_s[1] - self.position[1],
                            self.bbox.min_s[2] - self.position[2],
                        ]
                    ]
                ) @ rotation

                normals = un_rotated_sites
                normals[:, 0] /= self.shape[_SEMI_MINOR_AXIS] ** 2
                normals[:, 1] /= (
                    self.shape[_SEMI_MINOR_AXIS] * self.shape[_MAJOR_MINOR_RATIO]
                ) ** 2
                normals[:, 2] /= (
                    self.shape[_SEMI_MINOR_AXIS] * self.shape[_THIRD_MINOR_RATIO]
                ) ** 2

                normals = normals @ rotation.transpose()
                normal_norms = nmpy.sqrt((normals**2).sum(axis=1, keepdims=True))
                # When the analytical normal expression is evaluated at (0,0), it results in a null normal. This
                # occurs whenever the contour "passes through the center" (very thick contour and/or very thin object).
                normal_norms[normal_norms == 0.0] = 1.0
                normals /= normal_norms
            else:
                sites = normals = None

            self._cache[cache_entry] = (sites, normals)

        return self._cache[cache_entry]

    def _RadiusForSimilarPositions(self, /, *, fraction: float = 0.1) -> float:
        """"""
        return (
            0.34
            * fraction
            * self.shape[_SEMI_MINOR_AXIS]
            * (1.0 + self.shape[_MAJOR_MINOR_RATIO] + self.shape[_THIRD_MINOR_RATIO])
        )

    def FormattedShape(self) -> str:
        """"""
        semi_minor_axis = self.shape[_SEMI_MINOR_AXIS]
        semi_major_axis = semi_minor_axis * self.shape[_MAJOR_MINOR_RATIO]
        semi_third_axis = semi_minor_axis * self.shape[_THIRD_MINOR_RATIO]
        return (
            f"{semi_minor_axis:.2f}x{semi_major_axis:.2f}x{semi_third_axis:.2f}"
            + FormattedAngle(self.shape[_RC_ANGLE])
            + FormattedAngle(self.shape[_RD_ANGLE])
        )
