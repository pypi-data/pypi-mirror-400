"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from pathlib import Path as path_t

import numpy as nmpy
from obj_mpp.interface.storage.api import signal_details_h

array_t = nmpy.ndarray


def SignalByNumpy(
    signal_path: path_t | None, /, *, can_be_anything: bool = True
) -> signal_details_h:
    """"""
    if signal_path is None:
        return None, None

    return _SignalByNumpy(signal_path, can_be_anything=can_be_anything)


def _SignalByNumpy(
    path: path_t, /, *, can_be_anything: bool = True
) -> signal_details_h:
    """"""
    try:
        signal = nmpy.load(str(path))
        error = None
    except Exception as exception:
        signal = None
        error = exception

    if can_be_anything:
        return signal, error

    if isinstance(signal, h.Mapping):
        keys = tuple(signal.keys())
        signal = signal[keys[0]]
    if isinstance(signal, array_t):
        return signal, None

    return None, ValueError(
        f'Invalid signal loaded for "{path}": '
        f"Actual={signal}; "
        f'Expected=a Numpy array of type "Numpy.ndarray".'
    )
