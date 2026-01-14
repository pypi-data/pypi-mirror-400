"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import numpy as nmpy
from p_pattern.extension.type import number_h

interval_h = tuple[number_h, number_h]  # Closed interval.
precision_h = number_h | None  # None=infinite.

interval_with_precision_h = tuple[number_h, number_h, precision_h]
domain_precisions_h = precision_h | tuple[precision_h, ...]

domain_h = tuple[interval_h, ...]
domain_indexer_h = tuple[slice, ...]
chunked_domain_h = tuple[domain_h, tuple[interval_h, ...], domain_h]

array_t = nmpy.ndarray


class educated_domain_t(h.NamedTuple):
    """
    The domain is defined by its "bounds" inside the infinite, "dimension"-dimensional
    space. Along each axis, the lower bound is always zero.
    Restriction is a potential restriction of the full domain. Its lower bounds can be
    different from zero.
    Effective is the restriction if there is one, else the whole domain.
    """

    dimension: int
    bounds: domain_h
    lengths: tuple[int, ...]
    precisions: domain_precisions_h | None
    sites: tuple[array_t, ...]
    sites_flat: tuple[array_t, ...]

    restriction: domain_h | None
    effective: domain_h

    @classmethod
    def New(
        cls,
        definition: domain_h | array_t,
        /,
        *,
        restriction: domain_h | None = None,
        precision: int | float | tuple[int | float, ...] | None = None,
        expected_dimension: int | None = None,
    ) -> h.Self:
        """"""
        if isinstance(definition, array_t):
            lengths = definition.shape
            if expected_dimension is not None:
                # Why limiting to the first dimension components? To fit 2-D patterns on
                # 2-D, color images for example.
                lengths = lengths[:expected_dimension]
            definition = tuple((0, _ - 1) for _ in lengths)
            precision = None
        else:
            assert all(_[0] == 0 for _ in definition), definition
            assert (expected_dimension is None) or (
                definition.__len__() == expected_dimension
            ), (definition.__len__(), expected_dimension)

            lengths = tuple(_[1] + 1 for _ in definition)
            if precision is None:
                pass
            elif isinstance(precision, number_h):
                precision = expected_dimension * (float(precision),)
            else:
                precision = tuple(None if _ is None else float(_) for _ in precision)

        sites = tuple(nmpy.indices(lengths))
        sites_flat = tuple(_.flatten() for _ in sites)

        if restriction is None:
            effective = definition
        else:
            effective = restriction

        return cls(
            dimension=definition.__len__(),
            bounds=definition,
            lengths=lengths,
            precisions=precision,
            sites=sites,
            sites_flat=sites_flat,
            restriction=restriction,
            effective=effective,
        )
