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
from PIL import Image, ImageDraw, ImageFont

array_t = nmpy.ndarray


def Output2DObjects(
    model: model_t,
    instances: h.Sequence[instance_t],
    background: array_t | None,
    domain_lengths: tuple[int, ...],
    /,
    *,
    signal_id: str = "",
    plot_thickness: int = 1,
    with_annotations: bool = False,
    show_figure: bool = True,
    img_basename: str | None = None,
) -> None:
    """
    Must accept instances and image as first 2 arguments, and date_as_str as optional
    argument.
    """
    if not BackgroundIsValid(background, 2):
        return

    normalized_qualities = NormalizedQualities(instances)
    mkpt_lmp = nmpy.zeros(background.shape[:2], dtype=nmpy.uint16)
    output = ColorOutputImage(background, 2)
    DrawMarkedPoints(
        output, mkpt_lmp, instances, normalized_qualities, True, 0, 1, plot_thickness
    )

    # Plot here so that output is not altered with legend (see below)
    if show_figure:
        figure = detection_window_t.NewFor2D(
            domain_lengths, output, model, instances, mkpt_lmp
        )
        figure.Plot2DImage(output)
        figure.AddColorbar(normalized_qualities, 2)
        if with_annotations:
            figure.PlotAnnotations()
        # But do not block with show() here to let saving below occur right away
    else:
        figure = None

    if (img_basename is not None) and (img_basename != ""):
        if with_annotations:
            _DrawAnnotationsInArray(output, instances)

        mgio.imwrite(
            L.StoragePath(
                f"{img_basename}-{signal_id}", purpose="output", suffix="png"
            ),
            nmpy.around(255.0 * output).astype("uint8"),
        )

    if show_figure:
        pplt.show()
        pplt.close(figure.root)


def _DrawAnnotationsInArray(
    image: array_t, instances: h.Sequence[instance_t], /
) -> None:
    """"""
    font_size = 11

    for instance in instances:
        bbox = instance.bbox
        array_w_text = _ArrayWithText(str(id(instance)), size=font_size)
        array_w_text = list(nmpy.nonzero(array_w_text))
        array_w_text[0] += (
            bbox.min_s[0] + bbox.max_s[0] + font_size
        ) // 2 - array_w_text[0].max()
        array_w_text[1] += bbox.min_s[1] + font_size // 2 - array_w_text[1].min()

        out_of_domain = nmpy.logical_or(array_w_text[0] < 0, array_w_text[1] < 0)
        out_of_domain = nmpy.logical_or(
            out_of_domain, array_w_text[0] >= image.shape[0]
        )
        out_of_domain = nmpy.logical_or(
            out_of_domain, array_w_text[1] >= image.shape[1]
        )
        within_domain = nmpy.logical_not(out_of_domain)

        array_w_text = (array_w_text[0][within_domain], array_w_text[1][within_domain])

        image[..., 0][array_w_text] = 1.0


def _ArrayWithText(text: str, /, *, size: int = 10) -> array_t:
    """"""
    font = ImageFont.truetype("arial.ttf", size)

    image = Image.new(mode="1", size=(size * (text.__len__() + 1), 2 * size))
    drawer = ImageDraw.Draw(image)
    drawer.text((size // 2, size // 2), text, font=font, fill=1)

    output = nmpy.asarray(image, dtype=nmpy.bool_)

    n_rows, n_cols = output.shape
    row_projection = output.any(axis=1)
    col_projection = output.any(axis=0)
    row_start = row_projection.argmax()
    row_end_p_1 = n_rows - row_projection[::-1].argmax()
    col_start = col_projection.argmax()
    col_end_p_1 = n_cols - col_projection[::-1].argmax()

    return output[row_start:row_end_p_1, col_start:col_end_p_1]
