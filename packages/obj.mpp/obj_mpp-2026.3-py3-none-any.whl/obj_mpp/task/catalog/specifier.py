"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from conf_ini_g.api.functional import config_t
from obj_mpp.constant.catalog import MPM_CATALOG_SECTION, Q_CATALOG_SECTION
from obj_mpp.constant.config.label import label_e
from obj_mpp.task.catalog.importer import ImportedElement
from p_pattern.type.model.parameter import parameter_h
from value_factory.api.catalog import collection_t


def SpecifyCatalogMarkedPoints(config: config_t, /) -> None:
    """"""
    s_name = label_e.sct_mark_ranges.value
    basic = config[s_name].ppt.basic
    mark_hint = h.Annotated[
        tuple, collection_t(items_types=parameter_h, lengths=(2, 3))
    ]

    for mkpt_name, mkpt_type in ImportedElement(None, MPM_CATALOG_SECTION).items():
        for mark, definition in mkpt_type().items():
            config.AddPluginParameter(
                s_name,
                mark,
                hint=mark_hint,
                default=definition.default_interval,
                controlling_value=mkpt_name,
                basic=basic,
            )


def SpecifyCatalogQualities(config: config_t, /) -> None:
    """"""
    s_name = label_e.sct_quality_prm.value
    basic = config[s_name].ppt.basic

    for q_name, (q_context, _) in ImportedElement(None, Q_CATALOG_SECTION).items():
        for p_name, value in q_context.q_defaults.items():
            config.AddPluginParameter(
                s_name,
                p_name,
                hint=type(value),
                default=value,
                controlling_value=q_name,
                basic=basic,
            )
