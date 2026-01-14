"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from p_pattern.constant.number import MAX_FLOAT
from p_pattern.type.model.parameter import parameter_t

DEFAULT_RADIUS_DEFINITION = parameter_t(
    type=float,
    min=0.0,
    max=MAX_FLOAT,
    min_inclusive=False,
    max_inclusive=True,
    # If None, the mark is not recognized as a potential tuple.
    default_interval=(1.0, 10.0),
    default_precision=1.0,
)

DEFAULT_RADII_RATIO_ANY_DEFINITION = parameter_t(
    type=float,
    min=0.0,
    max=MAX_FLOAT,
    min_inclusive=False,
    max_inclusive=True,
    default_interval=(0.0, 2.0),
    default_precision=None,
)

DEFAULT_RADII_RATIO_LARGER_DEFINITION = parameter_t(
    type=float,
    min=1.0,
    max=MAX_FLOAT,
    min_inclusive=True,
    max_inclusive=True,
    default_interval=(1.0, 2.0),
    default_precision=None,
)

DEFAULT_POSITIVE_EXPONENT_DEFINITION = parameter_t(
    type=float,
    min=0.0,
    max=MAX_FLOAT,
    min_inclusive=False,
    max_inclusive=True,
    # If None, the mark is not recognized as a potential tuple.
    default_interval=(0.0, 2.0),
    default_precision=None,
)
