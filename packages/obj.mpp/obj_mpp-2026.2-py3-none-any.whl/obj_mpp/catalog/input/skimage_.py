"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from pathlib import Path as path_t

import numpy as nmpy
import skimage.io as skio
from obj_mpp.interface.storage.api import signal_details_h
from skimage.color import rgb2hsv as HSVVersionFromRGB

array_t = nmpy.ndarray


def ImageBySkimage(image_path: path_t | None, /) -> signal_details_h:
    """"""
    if image_path is None:
        return None, None

    return _ImageBySkimage(image_path)


def ImageChannelBySkimage(
    image_path: path_t | None, /, *, channel: str = "gray"
) -> signal_details_h:
    """
    channel (case-insensitive): gray, 0, 1, 2, R, G, B, H, S, V
    """
    if image_path is None:
        return None, None

    image, image_error = ImageBySkimage(image_path)
    if image is None:
        return None, image_error

    if image.ndim == 3:
        if nmpy.all(nmpy.diff(image[..., :3], axis=2) == 0):
            image = image[..., 0]
            return image, image_error

        channel_couple_lst = ((0, 1), (0, 2), (1, 2))
        for channel_couple in channel_couple_lst:
            simultaneously_zero = (
                nmpy.all(image[..., channel_couple[0]] == 0)
                and (image[..., channel_couple[1]] == 0).all()
            )
            if simultaneously_zero:
                image = image[..., {0, 1, 2}.difference(channel_couple)]
                return image, image_error

        # Normally, channel is already a string, but 0, 1, 2 also works.
        channel = channel.__str__().lower()

        if channel == "gray":  # ITU-R 601-2 luma transform.
            rounded = nmpy.empty(image.shape[:-1], dtype=image.dtype)
            nmpy.rint(
                0.299 * image[..., 0] + 0.587 * image[..., 1] + 0.114 * image[..., 2],
                casting="unsafe",
                out=rounded,
            )
            image = rounded
        elif channel in "012":
            image = image[..., int(channel)]
        elif channel in "rgb":
            image = image[..., int("rgb".find(channel))]
        elif channel in "hsv":
            normalized_image = image.astype(nmpy.float64)
            # noinspection PyArgumentList
            image_max = normalized_image.max()
            if image_max > 1.0:
                normalized_image /= image_max  # Normally never zero
            else:
                normalized_image = image
            hsv_image = HSVVersionFromRGB(normalized_image)
            image = hsv_image[..., int("hsv".find(channel))]
        else:
            return None, ValueError(f"{channel}: Invalid channel specification")

    return image, image_error


def _ImageBySkimage(path: path_t, /) -> signal_details_h:
    """"""
    try:
        image = skio.imread(str(path))
        error = None
    except Exception as exception:
        image = None
        error = exception

    return image, error
