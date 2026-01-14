"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import numpy as nmpy
import scipy.ndimage as spim
import skimage.measure as msre
from p_pattern.constant.number import INFINITY_NUMPY_FLOAT
from p_pattern.extension.type import number_h
from p_pattern.task.ball_factory import OfDimensionAndRadius
from p_pattern.task.formatting import FormattedPoint
from p_pattern.type.instance.parameter.bbox import bbox_t
from p_pattern.type.instance.parameter.position import coordinate_h, position_h
from p_pattern.type.model.generic import model_t
from p_pattern.type.model.parameter import parameter_h
from p_pattern.type.sampler.domain import domain_indexer_h
from p_pattern.type.sampler.instance import sampler_t

array_t = nmpy.ndarray
dilated_region_h = tuple[array_t, tuple]
description_h = tuple[position_h, tuple[parameter_h, ...], dict[str, h.Any]]

PARAMETER_NAME_LENGTH = 10


class instance_t:
    """
    cropping_indicator: top, bottom, left, right, [front, back] (i.e., row, col, dep).
    """

    __slots__ = (
        "position",
        "shape",
        "bbox",
        "region",
        "cropping_indicator",
        "crosses_border",
        "properties",
        "_cache",
    )

    position: position_h
    shape: tuple[parameter_h, ...]
    bbox: bbox_t
    region: array_t
    cropping_indicator: tuple[bool, ...]
    crosses_border: bool
    properties: dict[str, h.Any]
    #
    _cache: dict[str, h.Any]

    @property
    def dimension(self) -> int:
        """"""
        return self.position.__len__()

    def __init__(
        self,
        position: h.Sequence[coordinate_h],
        shape: h.Sequence[parameter_h],
        domain_lengths: tuple[int, ...],
        grid_sites: tuple[array_t, ...],
        /,
    ) -> None:
        """"""
        self.position = tuple(position)
        self.shape = tuple(shape)

        half_lengths = self._CoarseBoundingBoxHalfLengths()
        self._ComputeBoundingBox(half_lengths, domain_lengths)
        self.region = self._Region(grid_sites)

        self.properties = {}
        self._cache = {}

    @property
    def educated_name(self) -> str:
        """
        Could be a class method, but property "prefers" methods.
        """
        return type(self).__name__[:-2].capitalize()

    @property
    def as_tuple(self) -> description_h:
        """
        Instance should be re-buildable from the returned tuple.
        """
        return self.position, self.shape, self.properties

    @property
    def as_sortable(self) -> tuple[coordinate_h | parameter_h, ...]:
        """
        Computes a unique instance identifier.

        An easy solution would be to use id(self). However, the only serious use of this
        uid is in sorting mkpts to guarantee reproducibility of the detection (for
        debugging for example). Hence, the uid cannot depend on runtime-dependent
        quantities.
        A float representation can be (costly) computed as:
        hex(nmpy.float64(real).view(nmpy.uint64).item())
        """
        return *self.position, *self.shape

    @property
    def area(self) -> int:
        """"""
        cache_entry = "area"  # self.[...].__name__ cannot be used with properties.

        if cache_entry not in self._cache:
            self._cache[cache_entry] = nmpy.count_nonzero(self.region).item()

        return self._cache[cache_entry]

    # --- INSTANTIATE

    @classmethod
    def NewFromTuple(
        cls,
        as_tuple: description_h,
        domain_lengths: tuple[int, ...],
        grid_sites: tuple[array_t, ...],
        /,
    ) -> h.Self:
        """"""
        output = cls(as_tuple[0], as_tuple[1], domain_lengths, grid_sites)
        output.properties = as_tuple[2]
        return output

    # --- COMPUTE

    def _ComputeBoundingBox(
        self,
        un_cropped_half_lengths: tuple[int, ...],
        domain_lengths: tuple[int, ...],
        /,
    ) -> None:
        """
        Compute the rectangle just big enough to contain the marked point and set the
        appropriate member variables.
        """
        min_s = []
        max_s = []
        cropping_indicator = 2 * domain_lengths.__len__() * [False]

        ci_idx = 0
        for coordinate, un_cropped_half_length, domain_length in zip(
            self.position, un_cropped_half_lengths, domain_lengths, strict=True
        ):
            min_coord = coordinate - un_cropped_half_length
            if min_coord < 0:
                min_coord = 0
                cropping_indicator[ci_idx] = True
            else:
                min_coord = int(nmpy.floor(min_coord))

            max_coord = coordinate + un_cropped_half_length
            if max_coord > domain_length - 1:
                max_coord = domain_length - 1
                cropping_indicator[ci_idx + 1] = True
            else:
                max_coord = int(nmpy.ceil(max_coord))

            min_s.append(min_coord)
            max_s.append(max_coord)
            ci_idx += 2

        self.bbox = bbox_t(min_s, max_s)
        self.cropping_indicator = tuple(cropping_indicator)
        self.crosses_border = any(self.cropping_indicator)

    def Contour(self, /, *, thickness: int = 1) -> array_t:
        """"""
        cache_entry = self.Contour.__name__

        if cache_entry not in self._cache:
            self._cache[cache_entry] = {}

        if thickness not in self._cache[cache_entry]:
            region = self.region
            ball = OfDimensionAndRadius(self.dimension, thickness)
            contour = nmpy.logical_xor(
                region, spim.binary_erosion(region, structure=ball)
            )

            self._cache[cache_entry][thickness] = contour

        return self._cache[cache_entry][thickness]

    def DilatedRegion(
        self, dilation: int, domain_lengths: tuple[int, ...], /
    ) -> array_t | dilated_region_h:
        """
        Returns the boolean map of the dilated marked-point and the slices for each bbox
        dimension. Dilation can be negative (erosion then).
        """
        cache_entry = self.DilatedRegion.__name__

        if cache_entry not in self._cache:
            self._cache[cache_entry] = {}

        if dilation not in self._cache[cache_entry]:
            dimension = self.dimension
            ball = OfDimensionAndRadius(dimension, abs(dilation))
            if dilation > 0:
                padded_region = nmpy.pad(self.region, dilation)
                dilated_region = spim.binary_dilation(padded_region, structure=ball)
                sub_domain = dimension * [slice(0)]
                for axis, length in enumerate(domain_lengths):
                    start = max(dilation - self.bbox.domain[axis].start, 0)
                    stop = dilated_region.shape[axis] - max(
                        self.bbox.domain[axis].stop + dilation - length, 0
                    )
                    sub_domain[axis] = slice(start, stop)
                dilated_region = dilated_region[tuple(sub_domain)]
                dilated_domain = self.bbox.SlicesOfDilated(dilation, domain_lengths)
            else:
                dilated_region = spim.binary_erosion(self.region, structure=ball)
                dilated_domain = self.bbox.domain

            self._cache[cache_entry][dilation] = (dilated_region, dilated_domain)

        return self._cache[cache_entry][dilation]

    def InnerDistanceMap(self) -> array_t:
        """"""
        return spim.distance_transform_edt(self.region)

    def Property(self, name: str, /) -> h.Any:
        """"""
        all_props_entry = f"{msre.__name__}.{msre.regionprops.__name__}"
        # To store the accessor to all the instance properties returned by
        # msre.regionprops.
        cache_entry = f"{all_props_entry}.{name}"
        # To store the requested property, read from the above accessor.

        if cache_entry not in self._cache:
            if all_props_entry not in self._cache:
                self._cache[all_props_entry] = msre.regionprops(
                    self.region.astype(nmpy.uint8)
                )[0]
                # [0]: Because msre.regionprops expects a labeled image, and returns a
                # list of accessors-to-properties for each label/object.

            self._cache[cache_entry] = self._cache[all_props_entry][name]

        return self._cache[cache_entry]

    # --- GENERATE

    @classmethod
    def NewSamples(cls, sampler: sampler_t, n_samples: int, /) -> tuple[h.Self, ...]:
        """"""
        output = []

        domain = sampler.position.domain
        for position, shape in sampler.NewRawSamples(n_samples):
            sample = cls(position, shape, domain.lengths, domain.sites)
            output.append(sample)

        return tuple(output)

    def NewSimilarSamples(
        self, sampler: sampler_t, n_similar: int, /, *, fraction: float = 0.1
    ) -> tuple[h.Self, ...]:
        """"""
        cls = self.__class__
        radius = self._RadiusForSimilarPositions(fraction=fraction)
        domain = sampler.position.domain
        return tuple(
            cls(_, __, domain.lengths, domain.sites)
            for _, __ in sampler.NewRawSimilarSamples(
                self.position, self.shape, radius, n_similar, fraction=fraction
            )
        )

    # --- ANALYZE

    @staticmethod
    def ParametersExtrema(
        instances: h.Sequence,
        /,
        *,
        model: model_t | None = None,
        formatted: bool = False,
    ) -> tuple[tuple[float, ...], tuple[float, ...]] | str | None:
        """"""
        if instances.__len__() == 0:
            return None

        first = instances[0]
        dimension = first.position.__len__()
        n_properties = first.properties.__len__()
        n_parameters = dimension + first.shape.__len__() + n_properties
        min_s = nmpy.full(n_parameters, INFINITY_NUMPY_FLOAT, dtype=nmpy.float64)
        max_s = nmpy.full(n_parameters, -INFINITY_NUMPY_FLOAT, dtype=nmpy.float64)
        for instance in instances:
            properties = (
                *instance.position,
                *instance.shape,
                *instance.properties.values(),
            )
            nmpy.minimum(min_s, properties, out=min_s)
            nmpy.maximum(max_s, properties, out=max_s)

        if formatted:
            output = []
            for minimum, maximum in zip(min_s, max_s, strict=True):
                if minimum.is_integer():
                    minimum = int(minimum)
                    format_min = "d"
                else:
                    format_min = ".3f"
                if maximum.is_integer():
                    maximum = int(maximum)
                    format_max = "d"
                else:
                    format_max = ".3f"
                output.append(f"[{minimum:{format_min}}, {maximum:{format_max}}]")
            position = "x".join(output[:dimension])
            if model is None:
                shape = output[dimension:-n_properties]
            else:
                shape = (
                    f"{_}:{__}" for _, __ in zip(model, output[dimension:-n_properties])
                )
            shape = ", ".join(shape)
            properties = "\n".join(
                f"{_.capitalize() + ':':<{PARAMETER_NAME_LENGTH}}{__}"
                for _, __ in zip(first.properties, output[-n_properties:], strict=True)
            )
            return (
                f"{'Position:':<{PARAMETER_NAME_LENGTH}}{position}\n"
                f"{'Shape:':<{PARAMETER_NAME_LENGTH}}{shape}\n{properties}"
            )

        return tuple(min_s), tuple(max_s)

    def _RegionIntersects(
        self,
        domain_1: domain_indexer_h,
        region_2: array_t,
        domain_2: domain_indexer_h,
        area_2: int,
        max_overlap: float,
        /,
    ) -> bool:
        """"""
        region_1_inter = self.region[domain_1]
        region_2_inter = region_2[domain_2]
        intersection_area = nmpy.count_nonzero(
            nmpy.logical_and(region_1_inter, region_2_inter)
        ).item()

        if intersection_area == 0:
            return False

        min_area = min(self.area, area_2)
        if intersection_area == min_area:
            # Total inclusion
            return True

        # Always true when max_overlap = 0
        return 100.0 * intersection_area / min_area > max_overlap

    # --- REPORT

    def __str__(self) -> str:
        """"""
        return str(self.AsTuple())

    def AsTuple(
        self,
        /,
        *,
        educated_version: bool = False,
        header: tuple[str, ...] | None = None,
    ) -> tuple[str | coordinate_h | parameter_h | number_h, ...]:
        """"""
        output = [self.educated_name]

        output.extend(self.position)

        if educated_version:
            output.extend(self.educated_shape)
        else:
            output.extend(self.shape)

        if header is not None:
            for idx, (name, value) in enumerate(zip(header, output, strict=True)):
                output[idx] = f"{name}={value}"

        return tuple(output)

    def AsFormattedString(self) -> str:
        """"""
        return (
            f"{type(self).__name__[0].upper()}"
            + FormattedPoint(self.position)
            + "_"
            + self.FormattedShape()
        )

    def DrawInArray(
        self,
        array: array_t,
        /,
        *,
        level: number_h = 255,
        thickness: int = 2,
        bbox_level: number_h = -1,
    ) -> None:
        """"""
        bbox = self.bbox

        if bbox_level >= 0:
            slices = list(bbox.domain)
            for d_idx in range(self.dimension):
                domain_for_dim = slices[d_idx]

                slices[d_idx] = bbox.min_s[d_idx]
                array[tuple(slices)] = bbox_level

                slices[d_idx] = bbox.max_s[d_idx]
                array[tuple(slices)] = bbox_level

                slices[d_idx] = domain_for_dim

        if thickness > 0:
            array[bbox.domain][self.Contour(thickness=thickness)] = level
        else:
            array[bbox.domain][self.region] = level

    # --- JSON
    def __DescriptionForJSON__(self) -> description_h:
        """"""
        return self.as_tuple

    @classmethod
    def __NewFromJsonDescription__(
        cls, description: description_h, domain_lengths: tuple[int, ...], /
    ) -> h.Self:
        """"""
        return cls.NewFromTuple(description, domain_lengths)

    # --- MISSING MANDATORY

    def _CoarseBoundingBoxHalfLengths(self) -> tuple[int, ...]:
        """"""
        raise NotImplementedError

    def _Region(self, grid_sites: tuple[array_t, ...], /) -> array_t:
        """
        Must include the marked point frontier.
        """
        raise NotImplementedError

    def Intersects(self, other: h.Self, max_overlap: float, /) -> bool:
        """"""
        raise NotImplementedError

    # --- MISSING OPTIONAL

    @property
    def educated_shape(self) -> tuple[parameter_h, ...]:
        """"""
        raise NotImplementedError

    def Normals(self) -> tuple[tuple[array_t, ...] | None, array_t | None]:
        """"""
        raise NotImplementedError

    def _RadiusForSimilarPositions(self, /, *, fraction: float = 0.1) -> float:
        """
        Necessary for refinement, but optional since refinement is optional.
        """
        raise NotImplementedError

    def FormattedShape(self) -> str:
        """"""
        raise NotImplementedError
