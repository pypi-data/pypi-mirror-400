"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import numpy as nmpy

array_t = nmpy.ndarray

number_sampler_t = nmpy.random.Generator

new_samples_integer_h = h.Callable[..., int | array_t]
new_samples_real_h = h.Callable[..., float | array_t]
