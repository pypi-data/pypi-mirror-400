"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import importlib.util as mprt
import inspect as nspt
import types as t
import typing as h
from pathlib import Path as path_t


def ModuleFromPath(path: path_t, /) -> t.ModuleType:
    """"""
    parts = list(path.parts[:-1])
    if parts.__len__() > 0:
        if parts[0] in ("/", r"\\"):
            parts[0] = "ROOT"
        elif ":" in parts[0]:
            parts[0] = parts[0][:1]
    py_path = ".".join(parts)
    name = f"{py_path}.{path.stem}"

    spec = mprt.spec_from_file_location(name, path)

    return spec.loader.load_module(spec.name)


def IsOriginalAndExported(name: str, value: h.Any, path: path_t, /) -> bool:
    """"""
    if name.startswith("_"):
        return False

    try:
        where = nspt.getfile(value)
    except TypeError:  # Builtin object.
        where = ""

    return where == str(path)
