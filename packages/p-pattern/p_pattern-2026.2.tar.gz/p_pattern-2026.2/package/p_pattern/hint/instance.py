"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from p_pattern.hint.array import array_t
from p_pattern.hint.number import number_h

coordinate_h = number_h
position_h = tuple[coordinate_h, ...]
position_1_h = tuple[coordinate_h]
position_2_h = tuple[coordinate_h, coordinate_h]
position_3_h = tuple[coordinate_h, coordinate_h, coordinate_h]

parameter_h = number_h
parameter_interval_h = tuple[parameter_h, parameter_h]
parameter_precision_h = number_h | None

description_h = tuple[position_h, tuple[parameter_h, ...], dict[str, h.Any]]

dilated_region_h = tuple[array_t, tuple]
