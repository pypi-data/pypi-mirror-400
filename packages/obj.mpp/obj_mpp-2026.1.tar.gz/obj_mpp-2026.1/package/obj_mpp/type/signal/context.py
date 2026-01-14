"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import collections.abc as a
import dataclasses as d
import typing as h
from pathlib import Path as path_t

import numpy as nmpy
from p_pattern.extension.type import number_h

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class signal_context_t:
    """
    Domain-related details correspond to the domain the marked points will be
    superimposed on. In particular, the dimension is the dimension of marked points.

    map_or_pdf_path_or_folder: May be of type number_h or h.Sequence[number_h] at
    instantiation time, in which case it will be set to None in post-initialization.
    """

    signal_path_or_folder: path_t
    map_or_pdf_path_or_folder: path_t | str | None | number_h | h.Sequence[number_h]

    signal_path: path_t = d.field(init=False, default=None)
    map_or_pdf_path: path_t = d.field(init=False, default=None)

    lengths: tuple[int, ...] = d.field(init=False)

    signal_original: h.Any = d.field(init=False)
    signal_for_qty: h.Any = d.field(init=False)
    map_or_pdf: array_t | None = d.field(init=False, default=None)

    def __post_init__(self) -> None:
        """"""
        self.signal_path_or_folder = path_t(self.signal_path_or_folder)
        if isinstance(self.map_or_pdf_path_or_folder, str):
            self.map_or_pdf_path_or_folder = path_t(self.map_or_pdf_path_or_folder)
        elif isinstance(self.map_or_pdf_path_or_folder, path_t):
            pass
        else:  # Domain precision(s) for position sampling.
            self.map_or_pdf_path_or_folder = None

    def SignalDetails(
        self,
    ) -> a.Iterator[tuple[path_t, bool, bool, str, path_t | None, bool, bool, str]]:
        """"""
        if self.map_or_pdf_path_or_folder is None:
            MapOrPDFPathFromSignal = lambda _: None
        elif self.map_or_pdf_path_or_folder.is_file():
            MapOrPDFPathFromSignal = lambda _: self.map_or_pdf_path_or_folder
        elif self.signal_path_or_folder.is_file():
            MapOrPDFPathFromSignal = lambda _: self.map_or_pdf_path_or_folder / _.name
        else:
            MapOrPDFPathFromSignal = (
                lambda _: self.map_or_pdf_path_or_folder
                / _.relative_to(self.signal_path_or_folder)
            )

        if self.signal_path_or_folder.is_dir():
            signal_paths = self.signal_path_or_folder.rglob("*.*")
        else:
            signal_paths = (self.signal_path_or_folder,)
        for path in signal_paths:
            output = []
            for current, attribute in (
                (path, "signal_path"),
                (MapOrPDFPathFromSignal(path), "map_or_pdf_path"),
            ):
                previous = getattr(self, attribute)
                setattr(self, attribute, current)
                output.extend(
                    (
                        current,
                        (current is not None) and current.is_file(),
                        current != previous,
                        f"{path.stem}_{path.suffix[1:]}",
                    )
                )

            yield tuple(output)

    def SetSignals(self, signal: h.Any, dimension: int, /) -> None:
        """"""
        assert nmpy.all(signal >= 0)

        self.lengths = signal.shape[:dimension]

        self.signal_original = signal
        self.signal_for_qty = nmpy.empty_like(signal, dtype=nmpy.uint16)
        signal_max = signal.max()
        if signal_max == 0:
            signal_max = 1.0
        nmpy.rint(
            (2**16 - 1) * (signal / signal_max),
            casting="unsafe",
            out=self.signal_for_qty,
        )

    def SetMapOrPDF(self, map_or_pdf: array_t, /) -> None:
        """"""
        assert nmpy.all(map_or_pdf >= 0)

        array_sum = map_or_pdf.sum()
        if array_sum == 0:
            array_sum = 1.0
        self.map_or_pdf = (map_or_pdf / array_sum).astype(dtype=nmpy.float16)
