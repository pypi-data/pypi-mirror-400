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
from p_pattern.type.model.generic import model_t
from p_pattern.type.model.parameter import parameter_h
from p_pattern.type.sampler.domain import domain_h
from p_pattern.type.sampler.number import (
    new_samples_integer_h,
    new_samples_real_h,
    number_sampler_t,
)
from p_pattern.type.sampler.position import position_sampler_t
from p_pattern.type.sampler.shape import shape_sampler_t

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class sampler_t:
    model: model_t
    seed: int | None = None

    domain: d.InitVar[domain_h | array_t] = ()
    restriction: d.InitVar[domain_h | None] = None
    precision: d.InitVar[int | float | tuple[int | float, ...] | None] = None

    number: number_sampler_t = d.field(init=False)
    IntegerSamples: new_samples_integer_h = d.field(init=False)
    RealSamples: new_samples_real_h = d.field(init=False)
    position: position_sampler_t = d.field(init=False)
    shape: dict[str, shape_sampler_t] = d.field(init=False, default_factory=dict)

    def __post_init__(
        self,
        domain: domain_h | array_t,
        restriction: domain_h | None,
        precision: int | float | tuple[int | float, ...] | None,
    ) -> None:
        """"""
        self.number = nmpy.random.default_rng(seed=self.seed)
        self.IntegerSamples = self.number.integers
        self.RealSamples = self.number.uniform

        self.position = position_sampler_t.New(
            domain, restriction, precision, self.model.dimension
        )
        if self.position is None:
            return

        for name, parameter in self.model.items():
            self.shape[name] = shape_sampler_t.New(
                parameter.interval[0],
                parameter.interval[1],
                parameter.type,
                self.number,
            )

    def NewRawSamples(
        self, n_samples: int, /
    ) -> h.Iterator[tuple[position_h, tuple[number_h, ...]]]:
        """"""
        if self.position is None:
            return

        positions = self.position.Samples(
            n_samples, IntegerSamples=self.IntegerSamples, RealSamples=self.RealSamples
        )
        shapes = (_.Samples(n_samples) for _ in self.shape.values())

        dimension = positions.__len__()
        for sample in zip(*positions, *shapes, strict=True):
            yield sample[:dimension], sample[dimension:]

    def NewRawSimilarSamples(
        self,
        position: position_h,
        shape: tuple[parameter_h, ...],
        radius: float,
        n_similar: int,
        /,
        *,
        fraction: float = 0.1,
    ) -> h.Iterator[tuple[position_h, tuple[number_h, ...]]]:
        """"""
        positions = self.position.NewSimilarSamples(
            position, radius, n_similar, self.RealSamples
        )
        shapes = (
            __.NewSimilarSamples(_, fraction, n_similar)
            for _, __ in zip(shape, self.shape.values(), strict=True)
        )

        dimension = positions.__len__()
        # Do not make zipping strict since validation of position sampling can result in
        # positions[...] being shorter than shapes[...].
        for sample in zip(*positions, *shapes):
            yield sample[:dimension], sample[dimension:]
