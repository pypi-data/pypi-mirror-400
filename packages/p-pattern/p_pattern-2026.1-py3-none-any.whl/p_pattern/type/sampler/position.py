"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

import numpy as nmpy
from p_pattern.extension.type import number_h
from p_pattern.type.instance.parameter.position import position_h
from p_pattern.type.sampler.domain import domain_h, educated_domain_t
from p_pattern.type.sampler.number import new_samples_integer_h, new_samples_real_h

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class position_sampler_t:
    """
    precision: Currently, used only for domain sampling.
    """

    domain: educated_domain_t

    @classmethod
    def New(
        cls,
        domain: domain_h | array_t,
        restriction: domain_h | None,
        precision: int | float | tuple[int | float, ...] | None,
        expected_dimension: int,
        /,
    ) -> h.Self | None:
        """
        classmethod: Only to be able to use typing.Self as a returned type.
        """
        educated_domain = educated_domain_t.New(
            domain,
            restriction=restriction,
            precision=precision,
            expected_dimension=expected_dimension,
        )

        if isinstance(domain, array_t):
            unique_values = nmpy.unique(domain)
            if unique_values.size > 2:
                output = pdf_t.NewLocal(domain, educated_domain)
            else:
                output = stencil_t.NewLocal(domain == unique_values[1], educated_domain)
            return output

        return domain_t.NewLocal(educated_domain)

    def Samples(
        self,
        n_samples: int,
        /,
        *,
        IntegerSamples: new_samples_integer_h | None = None,
        RealSamples: new_samples_real_h | None = None,
    ) -> tuple[array_t, ...]:
        """"""
        raise NotImplementedError

    def NewSimilarSamples(
        self,
        reference: position_h,
        radius: float,
        n_samples: int,
        RealSamples: new_samples_real_h,
        /,
    ) -> tuple[array_t, ...]:
        """
        Note that the (optional) precision is ignored.
        """
        output = []

        for center, (first, last) in zip(reference, self.domain.bounds, strict=True):
            first = max(center - radius, first)
            last = min(center + radius, last)
            last = nmpy.nextafter(last, last + 1.0)
            local_output = RealSamples(low=first, high=last, size=n_samples)
            output.append(local_output)

        indexer = self._ValidityBIndexer(output)

        return tuple(_elm[indexer] for _elm in output)

    def _ValidityBIndexer(self, samples: h.Sequence[array_t], /) -> array_t:
        """
        Used only in NewSimilarSamples.
        """
        raise NotImplementedError


@d.dataclass(slots=True, repr=False, eq=False)
class domain_t(position_sampler_t):
    firsts: tuple[number_h, ...] | None = None
    after_lasts: tuple[float, ...] | None = None
    n_precise_sites_s: tuple[int | None, ...] | None = None

    @classmethod
    def NewLocal(cls, domain: educated_domain_t, /) -> h.Self:
        """"""
        bounds = domain.effective
        if domain.precisions is None:
            precisions = domain.dimension * (None,)
        else:
            precisions = domain.precisions

        firsts = tuple(_[0] for _ in bounds)
        after_lasts = tuple(nmpy.nextafter(__, __ + 1.0) for _, __ in bounds)
        n_precise_sites_s = tuple(
            None if _prc is None else int((_lst - _fst) / _prc) + 1
            for (_fst, _lst), _prc in zip(bounds, precisions, strict=True)
        )

        return cls(
            domain=domain,
            firsts=firsts,
            after_lasts=after_lasts,
            n_precise_sites_s=n_precise_sites_s,
        )

    def Samples(
        self,
        n_samples: int,
        /,
        *,
        IntegerSamples: new_samples_integer_h | None = None,
        RealSamples: new_samples_real_h | None = None,
    ) -> tuple[array_t, ...]:
        """"""
        if self.domain.precisions is None:
            return tuple(
                RealSamples(low=_, high=__, size=n_samples)
                for _, __ in zip(self.firsts, self.after_lasts, strict=True)
            )

        output = []

        for first, after_last, n_sites, precision in zip(
            self.firsts,
            self.after_lasts,
            self.n_precise_sites_s,
            self.domain.precisions,
            strict=True,
        ):
            if precision is None:
                local_output = RealSamples(low=first, high=after_last, size=n_samples)
            else:
                local_output = (
                    precision * IntegerSamples(0, high=n_sites, size=n_samples) + first
                )
            output.append(local_output)

        return tuple(output)

    def _ValidityBIndexer(self, samples: h.Sequence[array_t], /) -> array_t:
        """"""
        interval, *remaining = self.domain.bounds

        output = nmpy.logical_and(samples[0] >= interval[0], samples[0] <= interval[1])
        for d_idx, (first, last) in enumerate(remaining, start=1):
            local_output = nmpy.logical_and(
                samples[d_idx] >= first, samples[d_idx] <= last
            )
            output = nmpy.logical_and(output, local_output)

        return output


@d.dataclass(slots=True, repr=False, eq=False)
class stencil_t(position_sampler_t):
    stencil_lengths: tuple[int, ...] = ()
    valid_indices: array_t | None = None
    n_valid_indices: int = 0

    @classmethod
    def NewLocal(cls, stencil: array_t, domain: educated_domain_t, /) -> h.Self | None:
        """"""
        if (restriction := domain.restriction) is None:
            valid_indices = nmpy.flatnonzero(stencil)
            if valid_indices.size == 0:
                return None
        else:
            origin = (_ for _, __ in restriction)
            slices = tuple(slice(_fst, _lst + 1) for _fst, _lst in restriction)
            valid_indices = nmpy.nonzero(stencil[slices])
            if valid_indices[0].size > 0:
                valid_indices = tuple(
                    _ + __ for _, __ in zip(valid_indices, origin, strict=True)
                )
                valid_indices = nmpy.ravel_multi_index(valid_indices, stencil.shape)
            else:
                return None

        return cls(
            domain=domain,
            stencil_lengths=stencil.shape,
            valid_indices=valid_indices,
            n_valid_indices=valid_indices.size,
        )

    def Samples(
        self,
        n_samples: int,
        /,
        *,
        IntegerSamples: new_samples_integer_h | None = None,
        RealSamples: new_samples_real_h | None = None,
    ) -> tuple[array_t, ...]:
        """"""
        return nmpy.unravel_index(
            self.valid_indices[
                IntegerSamples(0, high=self.n_valid_indices, size=n_samples)
            ],
            self.stencil_lengths,
        )

    def _ValidityBIndexer(self, samples: h.Sequence[array_t], /) -> array_t:
        """"""
        if nmpy.issubdtype(samples[0].dtype, nmpy.floating):
            samples = tuple(nmpy.rint(_).astype(nmpy.uint64) for _ in samples)

        return nmpy.fromiter(
            map(
                lambda _: _ in self.valid_indices,
                nmpy.ravel_multi_index(samples, self.stencil_lengths),
            ),
            dtype=nmpy.bool_,
            count=samples[0].__len__(),
        )


@d.dataclass(slots=True, repr=False, eq=False)
class pdf_t(position_sampler_t):
    origin: tuple[int, ...] = ()
    restriction_lengths: tuple[int, ...] = ()
    cdf: array_t | None = None

    @classmethod
    def NewLocal(cls, pdf: array_t, domain: educated_domain_t, /) -> h.Self:
        """
        pdf.sum(): Must be equal (very close to) 1.0.
        """
        assert nmpy.issubdtype(pdf.dtype, nmpy.floating)

        if (restriction := domain.restriction) is None:
            origin = pdf.ndim * (0,)
            restriction_lengths = pdf.shape
            restricted = pdf
        else:
            origin = tuple(_ for _, __ in restriction)
            restriction_lengths = tuple(_lst - _fst + 1 for _fst, _lst in restriction)
            slices = tuple(slice(_fst, _lst + 1) for _fst, _lst in restriction)
            restricted = pdf[slices]
        cdf = restricted.cumsum()
        if cdf[-1] > 0.0:
            nmpy.divide(cdf, cdf[-1], out=cdf)

        return cls(
            domain=domain,
            origin=origin,
            restriction_lengths=restriction_lengths,
            cdf=cdf,
        )

    def Samples(
        self,
        n_samples: int,
        /,
        *,
        IntegerSamples: new_samples_integer_h | None = None,
        RealSamples: new_samples_real_h | None = None,
    ) -> tuple[array_t, ...]:
        """"""
        uniform_samples = RealSamples(size=n_samples)
        indices = nmpy.unravel_index(
            nmpy.searchsorted(self.cdf, uniform_samples), self.restriction_lengths
        )
        return tuple(_ + __ for _, __ in zip(indices, self.origin, strict=True))

    def _ValidityBIndexer(self, samples: h.Sequence[array_t], /) -> array_t:
        """"""
        # Code duplication: See domain_t.
        interval, *remaining = self.domain.bounds

        output = nmpy.logical_and(samples[0] >= interval[0], samples[0] <= interval[1])
        for d_idx, (first, last) in enumerate(remaining, start=1):
            local_output = nmpy.logical_and(
                samples[d_idx] >= first, samples[d_idx] <= last
            )
            output = nmpy.logical_and(output, local_output)

        return output
