"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import numpy as nmpy
from logger_36 import L
from obj_mpp.constant.signal import MAX_UINT16
from p_pattern.type.instance.generic import instance_t

array_t = nmpy.ndarray


def ContourMapOfDetection(
    instances: h.Sequence[instance_t], domain_lengths, /
) -> array_t:
    """"""
    output = nmpy.zeros(domain_lengths, dtype=nmpy.uint16, order="C")

    if (n_instances := instances.__len__()) > MAX_UINT16:
        _PlotExclamationPoints(output)
        L.Log(
            "Number of marked points too high for storage as UInt16",
            actual=n_instances,
            expected=f"<={MAX_UINT16}",
        )
        return output

    for label, instance in enumerate(instances):
        output[instance.bbox.domain][instance.Contour()] = MAX_UINT16 - label

    return output


def RegionMapOfDetection(
    instances: h.Sequence[instance_t], domain_lengths, /
) -> array_t:
    """"""
    output = nmpy.zeros(domain_lengths, dtype=nmpy.uint16, order="C")

    if (n_instances := instances.__len__()) > MAX_UINT16:
        _PlotExclamationPoints(output)
        L.Log(
            "Number of marked points too high for storage as UInt16",
            actual=n_instances,
            expected=f"<={MAX_UINT16}",
        )
        return output

    distance_map = nmpy.zeros_like(output, dtype=nmpy.float64, order="C")
    for label, instance in enumerate(instances, start=1):
        local_dmp = distance_map[instance.bbox.domain]  # dmp=distance map
        instance_dmp = instance.InnerDistanceMap()
        without_intersection = instance_dmp > local_dmp

        local_dmp[without_intersection] = instance_dmp[without_intersection]
        output[instance.bbox.domain][without_intersection] = label

    return output


def _PlotExclamationPoints(array: array_t, /) -> None:
    """"""
    value = nmpy.iinfo(array.dtype).max

    half_width = array.shape[1] // 2
    half_half_width = half_width // 2
    half_bar_width = max(array.shape[1] // 20, 1)
    separation = max((2 * half_bar_width) // 4, 1)

    for col in (half_half_width, half_width, half_width + half_half_width):
        col_slice = slice(col - half_bar_width, col + half_bar_width)
        array[1 : (-2 * half_bar_width - separation - 1), col_slice] = value
        array[(-2 * half_bar_width - 1) : -1, col_slice] = value
