"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import numpy as nmpy
import scipy.ndimage as spim
import skimage.morphology as mrph
from p_pattern.hint.array import array_t

# TODO: Remove global variable... or not.
PER_DIM_AND_RADIUS: dict[int, dict[int, array_t]] = {}


def OfDimensionAndRadius(dimension: int, radius: int, /) -> array_t:
    """"""
    global PER_DIM_AND_RADIUS

    if dimension not in PER_DIM_AND_RADIUS:
        PER_DIM_AND_RADIUS[dimension] = {}

    per_radius = PER_DIM_AND_RADIUS[dimension]

    if radius not in per_radius:
        if dimension == 1:
            ball = nmpy.full(2 * radius + 1, True, dtype=nmpy.bool_)
        elif dimension == 2:
            ball = mrph.disk(radius, dtype=nmpy.bool_)
        elif dimension == 3:
            ball = mrph.ball(radius, dtype=nmpy.bool_)
        else:
            chart = nmpy.ones(dimension * (2 * radius + 1,), dtype=nmpy.float64)
            center = dimension * (radius,)
            chart[(*center,)] = 0.0
            distances = spim.distance_transform_edt(chart)
            ball = distances <= radius
        per_radius[radius] = ball

    return per_radius[radius]
