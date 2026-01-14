"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import numpy as nmpy
from p_pattern.type.sampler.domain import domain_indexer_h

array_t = nmpy.ndarray


class bbox_t:
    """
    domain: To be used in numpy array indexing.
    """

    __slots__ = ("min_s", "max_s", "domain", "_lengths")

    min_s: tuple[int, ...]
    max_s: tuple[int, ...]
    domain: domain_indexer_h
    _lengths: tuple[int, ...] | None

    def __init__(self, min_s: h.Sequence[int], max_s: h.Sequence[int], /) -> None:
        """"""
        self.min_s = tuple(min_s)
        self.max_s = tuple(max_s)
        self.domain = tuple(
            slice(_, __ + 1) for _, __ in zip(self.min_s, self.max_s, strict=True)
        )
        self._lengths = None

    @property
    def lengths(self) -> tuple[int, ...]:
        """"""
        if self._lengths is None:
            self._lengths = tuple(_.stop - _.start for _ in self.domain)
        return self._lengths

    def SlicesOfDilated(
        self, dilation: int, domain_lengths: tuple[int, ...], /
    ) -> domain_indexer_h:
        """
        dilation: Can be negative.
        """
        dilated_min_s = (max(0, _min - dilation) for _min in self.min_s)
        dilated_max_s = (
            min(_lgt - 1, _max + dilation)
            for _max, _lgt in zip(self.max_s, domain_lengths, strict=True)
        )

        return tuple(
            slice(_, __ + 1) for _, __ in zip(dilated_min_s, dilated_max_s, strict=True)
        )

    def GlobalizedSites(
        self, sites_local: tuple[array_t, ...], /
    ) -> tuple[array_t, ...]:
        """"""
        return tuple(_ + __ for _, __ in zip(sites_local, self.min_s, strict=True))
