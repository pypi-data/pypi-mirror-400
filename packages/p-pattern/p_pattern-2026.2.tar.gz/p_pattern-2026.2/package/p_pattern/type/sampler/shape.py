"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import math
import typing as h

from p_pattern.hint.array import array_t
from p_pattern.hint.instance import (
    parameter_h,
    parameter_interval_h,
    parameter_precision_h,
)
from p_pattern.hint.sampler import number_sampler_t


@d.dataclass(slots=True, repr=False, eq=False)
class shape_sampler_t:
    NewSamples: h.Callable[[int], array_t]
    NewSimilarSamples: h.Callable[[parameter_h, float, int], array_t]

    @classmethod
    def New(
        cls,
        interval: parameter_interval_h,
        precision: parameter_precision_h,
        stripe: type[parameter_h],
        sampler: number_sampler_t,
        /,
    ) -> h.Self:
        """"""
        first, last = interval
        IntegerSamples = sampler.integers
        RealSamples = sampler.uniform

        if precision is None:
            if stripe is int:
                NewSamples = lambda _arg: IntegerSamples(
                    first, high=last + 1, size=_arg
                )
            else:
                NewSamples = lambda _arg: RealSamples(low=first, high=last, size=_arg)
        else:
            if stripe is int:
                maximum = (last - first) // precision
            else:
                maximum = int((last - first) / precision)
            NewSamples = (
                lambda _arg: precision * IntegerSamples(0, high=maximum + 1, size=_arg)
                + first
            )

        NewSimilarSamples = lambda _ref, _frt, _nbr: _SimilarSamples(
            _ref, stripe, interval, _frt, _nbr, IntegerSamples, RealSamples
        )

        return cls(NewSamples=NewSamples, NewSimilarSamples=NewSimilarSamples)


def _SimilarSamples(
    reference: parameter_h,
    stripe: type[parameter_h],
    interval: parameter_interval_h,
    fraction: float,
    n_samples: int,
    IntegerSamples,
    RealSamples,
    /,
) -> array_t:
    """"""
    first = max(reference * (1.0 - fraction), interval[0])
    last = min(reference * (1.0 + fraction), interval[1])

    if stripe is int:
        return IntegerSamples(
            math.floor(first), high=math.ceil(last) + 1, size=n_samples
        )
    else:
        if last < interval[1]:
            last = math.nextafter(last, last + 1.0)
        return RealSamples(low=first, high=last, size=n_samples)
