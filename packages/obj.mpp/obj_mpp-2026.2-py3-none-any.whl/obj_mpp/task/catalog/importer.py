"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import inspect as nspt
import typing as h
from pathlib import Path as path_t

from logger_36 import L
from obj_mpp.constant.catalog import catalog_section_t, pattern_catalog_section_t
from obj_mpp.constant.config.parameter import MOD_ELM_SEPARATOR
from obj_mpp.extension.importer import IsOriginalAndExported, ModuleFromPath


def ImportedElement(
    query: str | None, catalog_section: catalog_section_t | pattern_catalog_section_t, /
) -> h.Any:
    """"""
    output = {}

    if query is None:
        path = None
    else:
        path, query = _ModuleAndElement(query)
    if path is None:
        path = catalog_section.BasePath()
        # Tuple-d for potential error message below.
        paths = tuple(path.glob(catalog_section.pattern))
    else:
        paths = (path,)

    for path in paths:
        module = ModuleFromPath(path)
        for name, value in nspt.getmembers(module, catalog_section.type_for_getmembers):
            if IsOriginalAndExported(name, value, path) and (
                (catalog_section.type_for_issubclass is None)
                or issubclass(value, catalog_section.type_for_issubclass)
            ):
                name = catalog_section.ElementName(name)
                value = catalog_section.ElementValue(value)
                if query is None:
                    output[name] = value
                elif name == query:
                    return value

    if query is None:
        return output

    paths = "\n".join(map(str, paths))
    L.StageIssue(f'Element "{query}" not found in:\n{paths}')
    return None


def _ModuleAndElement(composite: str, /) -> tuple[path_t | None, str]:
    """"""
    if MOD_ELM_SEPARATOR in composite:
        document, element = composite.rsplit(sep=MOD_ELM_SEPARATOR, maxsplit=1)
        if document.__len__() > 0:
            document = path_t(document)
        else:
            document = None
    else:
        document = None
        element = composite

    return document, element
