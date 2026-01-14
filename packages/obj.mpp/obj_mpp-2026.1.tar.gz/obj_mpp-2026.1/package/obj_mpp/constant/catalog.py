"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import inspect as nspt
import sys as s
import typing as h
from pathlib import Path as path_t

from obj_mpp.extension.function import signature_t
from obj_mpp.type.quality.base import quality_context_t
from p_pattern.type.instance.generic import instance_t
from p_pattern.type.model.generic import model_t
from p_pattern.type.sampler.domain import educated_domain_t as domain_t

PATTERN_CATALOG_FOLDER = (
    path_t(s.modules[model_t.__module__].__file__).parent.parent.parent / "catalog"
)
CATALOG_FOLDER = path_t(__file__).parent.parent / "catalog"


class pattern_catalog_section_t(h.NamedTuple):
    folder: str
    pattern: str
    type_for_getmembers: type[nspt.isclass] | type[nspt.isfunction]
    type_for_issubclass: type | None = None
    sub_folder: str | None = None
    ElementName: h.Callable[[str], str] = lambda _arg: _arg
    ElementValue: h.Callable[[h.Any], h.Any] = lambda _arg: _arg

    def BasePath(self) -> path_t:
        """"""
        output = PATTERN_CATALOG_FOLDER / self.folder
        if self.sub_folder is not None:
            output /= self.sub_folder
        return output


class catalog_section_t(h.NamedTuple):
    folder: str
    pattern: str
    type_for_getmembers: type[nspt.isclass] | type[nspt.isfunction]
    type_for_issubclass: type | None = None
    sub_folder: str | None = None
    ElementName: h.Callable[[str], str] = lambda _arg: _arg
    ElementValue: h.Callable[[h.Any], h.Any] = lambda _arg: _arg

    def BasePath(self) -> path_t:
        """"""
        output = CATALOG_FOLDER / self.folder
        if self.sub_folder is not None:
            output /= self.sub_folder
        return output


def _TypeNameWithoutPostfix(name: str, /) -> str:
    """"""
    return name[:-2]


def _ValueForQuality(value: h.Callable, /) -> tuple[h.Callable, signature_t]:
    """"""
    return value, signature_t.Of(value(domain_t.New(((0, 1),))).Quality)


MPM_CATALOG_SECTION = pattern_catalog_section_t(
    folder="model",
    pattern="*/*.py",
    type_for_getmembers=nspt.isclass,
    type_for_issubclass=model_t,
    ElementName=_TypeNameWithoutPostfix,
)
MPI_CATALOG_SECTION = pattern_catalog_section_t(
    folder="instance",
    pattern="*/*.py",
    type_for_getmembers=nspt.isclass,
    type_for_issubclass=instance_t,
    ElementName=_TypeNameWithoutPostfix,
)
Q_CATALOG_SECTION = catalog_section_t(
    folder="quality",
    pattern="*.py",
    type_for_getmembers=nspt.isclass,
    type_for_issubclass=quality_context_t,
    ElementName=_TypeNameWithoutPostfix,
    ElementValue=_ValueForQuality,
)
I_CATALOG_SECTION = catalog_section_t(
    folder="input", pattern="*.py", type_for_getmembers=nspt.isfunction
)
O_CATALOG_SECTION = catalog_section_t(
    folder="output", pattern="*.py", type_for_getmembers=nspt.isfunction
)
