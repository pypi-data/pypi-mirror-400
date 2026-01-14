"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

import numpy as nmpy
from logger_36 import L
from obj_mpp.constant.signal import INFINITY_NUMPY_FLOAT, INFINITY_NUMPY_INT
from obj_mpp.type.quality.base import quality_context_t as _base_t
from p_pattern.type.instance.generic import instance_t

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class _contrast_t(_base_t):
    q_defaults = {
        "ring_thickness_ext": 1,
        "ring_thickness_int": INFINITY_NUMPY_INT,
        "normalized": False,
    }

    def SetKwargs(self, q_kwargs: dict[str, h.Any], _: dict[str, h.Any], /) -> None:
        """"""
        self._SetKwargsWithDefaults(q_kwargs, self.q_defaults, {}, {})


def _Contrast_BrightOnDark(
    instance: instance_t,
    signal: array_t,
    ring_thickness_ext: int,
    ring_thickness_int: int,
    normalized: bool,
    domain_lengths: tuple[int, ...],
    /,
) -> float:
    """
    The DilatedRegion method must accept positive and negative (if not
    nmpy.isinf(ring_thickness_int)) dilation parameters.
    """
    region = instance.region
    dilated, dilated_bbox_domain = instance.DilatedRegion(
        ring_thickness_ext, domain_lengths
    )

    sum_region, area_region, sum2_region = _SumsAndArea(
        signal[instance.bbox.domain], region, normalized
    )
    sum_dilated, area_dilated, sum2_dilated = _SumsAndArea(
        signal[dilated_bbox_domain], dilated, normalized
    )
    if area_dilated <= area_region:
        L.error("Dilated area not strictly larger than original area.")
        return -INFINITY_NUMPY_FLOAT

    if ring_thickness_int == INFINITY_NUMPY_INT:
        sum_eroded = area_eroded = sum2_eroded = 0
    else:
        eroded, eroded_bbox_domain = instance.DilatedRegion(-ring_thickness_int)
        sum_eroded, area_eroded, sum2_eroded = _SumsAndArea(
            signal[eroded_bbox_domain], eroded, normalized
        )
        if area_eroded >= area_region:
            L.error("Eroded area not strictly smaller than original area.")
            return -INFINITY_NUMPY_FLOAT

    area_ext = area_dilated - area_region
    area_int = area_region - area_eroded

    average_ext = (sum_dilated - sum_region) / area_ext
    average_int = (sum_region - sum_eroded) / area_int

    if normalized:
        var_ext = ((sum2_dilated - sum2_region) / area_ext) - average_ext**2
        var_int = ((sum2_region - sum2_eroded) / area_int) - average_int**2

        return (average_int - average_ext) / (var_int * var_ext) ** 0.25
    else:
        return average_int - average_ext


def _Contrast_DarkOnBright(
    instance: instance_t,
    signal: array_t,
    ring_thickness_ext: int,
    ring_thickness_int: int,
    normalized: bool,
    domain_lengths: tuple[int, ...],
    /,
) -> float:
    """
    See _Contrast_BrightOnDark for conditions.
    """
    contrast = _Contrast_BrightOnDark(
        instance,
        signal,
        ring_thickness_ext,
        ring_thickness_int,
        normalized,
        domain_lengths,
    )
    if contrast == -INFINITY_NUMPY_FLOAT:
        # To avoid returning +INFINITY_NUMPY_FLOAT by negation below.
        return -INFINITY_NUMPY_FLOAT

    return -contrast


def _SumsAndArea(
    local_signal: array_t, region: array_t, with_sum_of_sq: bool, /
) -> tuple[float, float, float | None]:
    """"""
    values = local_signal[region]

    area_msk = nmpy.count_nonzero(region)
    sum_region = values.sum().item()
    if with_sum_of_sq:
        sum_of_sq = (values**2).sum().item()
    else:
        sum_of_sq = None

    return sum_region, area_msk, sum_of_sq


class contrast_bright_on_dark_t(_contrast_t):
    def Quality(self, instance: instance_t, /) -> float:
        """"""
        return _Contrast_BrightOnDark(
            instance,
            self.signal,
            self.q_kwargs["ring_thickness_ext"],
            self.q_kwargs["ring_thickness_int"],
            self.q_kwargs["normalized"],
            self.domain.lengths,
        )


class contrast_dark_on_bright_t(_contrast_t):
    def Quality(self, instance: instance_t, /) -> float:
        """"""
        return _Contrast_DarkOnBright(
            instance,
            self.signal,
            self.q_kwargs["ring_thickness_ext"],
            self.q_kwargs["ring_thickness_int"],
            self.q_kwargs["normalized"],
            self.domain.lengths,
        )
