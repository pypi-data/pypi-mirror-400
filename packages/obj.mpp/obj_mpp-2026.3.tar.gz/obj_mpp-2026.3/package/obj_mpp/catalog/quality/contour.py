"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h
from enum import Enum as enum_t

import numpy as nmpy
from obj_mpp.type.quality.base import quality_context_t as _base_t
from p_pattern.type.instance.generic import instance_t


class measure_e(enum_t):
    MEAN = 1
    STDDEV = 2
    VARIANCE = 3
    MEDIAN = 4
    MIN = 5
    MAX = 6


@d.dataclass(slots=True, repr=False, eq=False)
class contour_t(_base_t):
    q_defaults = {"measure": measure_e.MEAN}

    def SetKwargs(self, q_kwargs: dict[str, h.Any], _: dict[str, h.Any], /) -> None:
        """"""
        if (measure := q_kwargs.get("measure")) is None:
            q_kwargs["measure"] = self.q_defaults["measure"]
        elif isinstance(measure, str):
            # For example, "mean".
            q_kwargs["measure"] = measure_e(measure.upper())

        self.q_kwargs = q_kwargs

    def Quality(self, instance: instance_t, /) -> float:
        """"""
        domain = instance.bbox.domain
        contour = instance.Contour()

        # Cannot be empty (see Contour).
        signal = self.signal[domain][contour]
        measure = self.q_kwargs["measure"]

        if measure == measure_e.MEAN:
            return signal.mean().item()
        elif measure == measure_e.STDDEV:
            return signal.std().item()
        elif measure == measure_e.VARIANCE:
            return signal.var().item()
        elif measure == measure_e.MEDIAN:
            return signal.median().item()
        elif measure == measure_e.MIN:
            return nmpy.min(signal).item()
        else:  # measure == measure_e.MAX:
            return nmpy.max(signal).item()
