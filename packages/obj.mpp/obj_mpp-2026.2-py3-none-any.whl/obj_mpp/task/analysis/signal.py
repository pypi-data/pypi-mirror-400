"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import numpy as nmpy
from p_pattern.extension.type import number_h
from p_pattern.type.instance.generic import instance_t

array_t = nmpy.ndarray


def SignalStatisticsInMarkedPoint(
    instance: instance_t, signal: array_t | None, /, *, header_instead: bool = False
) -> tuple[number_h | str, ...]:
    """"""
    if header_instead:
        return "Min Intensity", "Max Intensity", "Mean Intensity", "SDev Intensity"

    if isinstance(signal, array_t) and (signal.ndim == instance.dimension):
        signal_values = signal[instance.bbox.domain][instance.region]

        return (
            signal_values.min().item(),
            signal_values.max().item(),
            signal_values.mean().item(),
            signal_values.std().item(),
        )
    else:
        return 4 * (nmpy.nan,)


def SignalStatisticsInBackground(
    instances: h.Sequence[instance_t] | None, signal: array_t | None
) -> tuple[number_h | str, ...]:
    """"""
    if instances is None:
        return ("Bck Intensity",)

    if (
        isinstance(signal, array_t)
        and (instances.__len__() > 0)
        and (signal.ndim == instances[0].dimension)
    ):
        background = nmpy.ones_like(signal, dtype=nmpy.bool_)
        for instance in instances:
            background[instance.bbox.domain][instance.region] = False

        return (signal[background].mean().item(),)
    else:
        return (nmpy.nan,)
