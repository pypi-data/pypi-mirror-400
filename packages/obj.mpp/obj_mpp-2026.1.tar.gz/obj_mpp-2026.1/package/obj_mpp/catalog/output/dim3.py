"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import imageio as mgio
import numpy as nmpy
from logger_36 import L
from matplotlib import pyplot as pplt
from obj_mpp.catalog.output.dimX import (
    BackgroundIsValid,
    ColorOutputImage,
    DrawMarkedPoints,
)
from obj_mpp.interface.window.detection import detection_window_t
from obj_mpp.type.detection import NormalizedQualities
from p_pattern.type.instance.generic import instance_t
from p_pattern.type.model.generic import model_t

array_t = nmpy.ndarray


def Output3DObjects(
    model: model_t,
    instances: h.Sequence[instance_t],
    background: array_t,
    domain_lengths: tuple[int, ...],
    /,
    *,
    signal_id: str = "",
    plot_thickness: int = 2,
    with_annotations: bool = False,
    show_figure: bool = True,
    img_basename: str | None = None,
) -> None:
    """
    Must accept instances and image as first 2 arguments, and date_as_str as optional argument.
    """
    if not BackgroundIsValid(background, 3):
        return

    normalized_qualities = NormalizedQualities(instances)

    if (img_basename is not None) and (img_basename != ""):
        background_color = ColorOutputImage(background, 3)
        DrawMarkedPoints(
            background_color,
            None,
            instances,
            normalized_qualities,
            True,
            0,
            1,
            plot_thickness,
        )

        mgio.volwrite(
            L.StoragePath(
                f"{img_basename}-{signal_id}", purpose="output", suffix="tif"
            ),
            nmpy.around(255.0 * background_color).astype("uint8"),
        )

    if show_figure:
        background_grayscale = nmpy.zeros(background.shape[:3], dtype=nmpy.float64)
        DrawMarkedPoints(
            background_grayscale, None, instances, normalized_qualities, False, 0, 0, 0
        )

        figure = detection_window_t.NewFor3D(
            domain_lengths, background_grayscale, model, instances
        )
        figure.PlotIsoSurface(background_grayscale)
        figure.AddColorbar(normalized_qualities, 3)

        pplt.show()
        pplt.close(figure.root)
