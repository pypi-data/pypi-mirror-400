"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from logger_36 import L
from p_pattern.type.instance.generic import instance_t
from p_pattern.type.model.generic import model_t

_MAX_N_INSTANCES_FOR_DISPLAY = 50


def ReportDetectedMarkedPoints(
    instances: h.Sequence[instance_t], model: model_t, /
) -> None:
    """"""
    if (n_instances := instances.__len__()) == 0:
        return

    ParametersExtrema = instances[0].__class__.ParametersExtrema
    as_strings = [
        _.AsFormattedString() for _ in instances[:_MAX_N_INSTANCES_FOR_DISPLAY]
    ]
    if n_instances > _MAX_N_INSTANCES_FOR_DISPLAY:
        as_strings.append(
            f"... and {n_instances - _MAX_N_INSTANCES_FOR_DISPLAY} more ..."
        )
    L.info(
        f"Detected marked point(s): {n_instances}\n"
        f"{ParametersExtrema(instances, model=model, formatted=True)}\n"
        f"{'\n'.join(as_strings)}"
    )


def ReportDetectedMarkedPointsInCSVFormat(
    instances: h.Sequence[instance_t], model: model_t, /
) -> None:
    """"""
    header_as_list = model.DescriptionHeader()
    L.info(", ".join(header_as_list))

    for instance in instances:
        L.info(", ".join(map(str, instance.AsTuple())))
