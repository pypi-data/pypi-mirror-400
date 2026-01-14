"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

import numpy as nmpy
from obj_mpp.constant.signal import INFINITY_NUMPY_FLOAT
from obj_mpp.type.quality.base import quality_context_t as _base_t
from p_pattern.type.instance.generic import instance_t
from p_pattern.type.sampler.instance import sampler_t

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class _gradient_t(_base_t):
    q_defaults = {"high_definition": 0.5, "min_fraction_high": 0.0}

    def SetKwargs(
        self, q_kwargs: dict[str, h.Any], s_kwargs: dict[str, h.Any], /
    ) -> None:
        """"""
        self._SetKwargsWithDefaults(q_kwargs, self.q_defaults, s_kwargs, {})

    def SetSignal(self, raw_signal: h.Any, sampler: sampler_t, /) -> bool:
        """"""
        if raw_signal.ndim != sampler.model.dimension:
            return True

        gradient = nmpy.gradient(raw_signal)

        sq_norm = gradient[0] ** 2
        for current in gradient[1:]:
            sq_norm.__iadd__(current**2)

        maximum = nmpy.sqrt(sq_norm.max())
        if maximum > 0.0:
            for current in gradient:
                current.__itruediv__(maximum)

        self.signal = gradient
        return False


def _Gradient_DarkOnBright(
    instance: instance_t,
    gradient: tuple[array_t, ...],
    high_definition: float,
    min_fraction_high: float,
    /,
    *,
    _called_from_bod: bool = False,
) -> float:
    """"""
    sites, normals = instance.Normals()
    if sites is None:
        return -INFINITY_NUMPY_FLOAT

    sites = instance.bbox.GlobalizedSites(sites)

    qualities = nmpy.zeros(sites[0].size, dtype=nmpy.float64)
    for idx in range(gradient.__len__()):
        qualities += normals[:, idx] * gradient[idx][sites]
    if _called_from_bod:
        qualities *= -1.0

    threshold = high_definition * qualities.max()
    if threshold < 0.0:
        return -INFINITY_NUMPY_FLOAT

    n_high = nmpy.count_nonzero(qualities >= threshold)
    if n_high / qualities.size < min_fraction_high:
        return -INFINITY_NUMPY_FLOAT

    return qualities.mean()


def _Gradient_BrightOnDark(
    instance: instance_t,
    gradient: tuple[array_t, ...],
    high_definition: float,
    min_fraction_high: float,
    /,
) -> float:
    """
    See _Gradient_DarkOnBright for conditions.
    """
    return _Gradient_DarkOnBright(
        instance, gradient, high_definition, min_fraction_high, _called_from_bod=True
    )


class gradient_bright_on_dark_t(_gradient_t):
    def Quality(self, instance: instance_t, /) -> float:
        """"""
        return _Gradient_BrightOnDark(
            instance,
            self.signal,
            self.q_kwargs["high_definition"],
            self.q_kwargs["min_fraction_high"],
        )


class gradient_dark_on_bright_t(_gradient_t):
    def Quality(self, instance: instance_t, /) -> float:
        """"""
        return _Gradient_DarkOnBright(
            instance,
            self.signal,
            self.q_kwargs["high_definition"],
            self.q_kwargs["min_fraction_high"],
        )
