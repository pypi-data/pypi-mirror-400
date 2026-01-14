"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

"""
This module is in a subfolder to hide it from catalog exploration.
"""

import logging as lggg
import typing as h

import numpy as nmpy
from logger_36 import L
from p_pattern.type.instance.generic import instance_t

array_t = nmpy.ndarray


def BackgroundIsValid(image: array_t | h.Any, expected_dim: int, /) -> bool:
    """"""
    if not isinstance(image, array_t):
        return False

    if (image.ndim == expected_dim) or (
        (image.ndim == expected_dim + 1) and (image.shape[-1] == 3)
    ):
        return True

    L.Log(
        "Invalid background dimension; Displaying/Saving cancelled",
        level=lggg.WARNING,
        actual=image.ndim,
        expected=f"{expected_dim}for grayscale or {expected_dim + 1} for color",
    )

    return False


def ColorOutputImage(background: array_t, image_dim: int, /) -> array_t:
    """"""
    if background.ndim == image_dim:
        output = nmpy.empty((*background.shape, 3), dtype=nmpy.float64)
        for channel in range(3):
            output[..., channel] = background
    else:
        # Returns a copy, as desired
        output = background.astype(nmpy.float64)

    # noinspection PyArgumentList
    normalization_factor = background.max()
    if normalization_factor > 0.0:
        output /= normalization_factor

    return output


def DrawMarkedPoints(
    image: array_t,
    labeled_map: array_t | None,
    instances: h.Sequence[instance_t],
    quality_details: dict[str, h.Any],
    in_color: bool,
    on_channel: int,
    off_channel: int,
    plot_thickness: int,
    /,
) -> None:
    """"""
    qualities = quality_details["pushed_against_1"]

    if in_color:
        target_image = image[..., on_channel]
    else:
        target_image = image

    for i_idx, (instance, quality) in enumerate(
        zip(instances, qualities, strict=True), start=1
    ):
        instance.DrawInArray(target_image, thickness=plot_thickness, level=quality)
        if in_color:
            instance.DrawInArray(
                image[..., off_channel], thickness=plot_thickness, level=0.0
            )

        if labeled_map is not None:
            labeled_map[instance.bbox.domain][instance.region] = i_idx
