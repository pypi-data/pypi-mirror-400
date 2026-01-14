"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from pathlib import Path as path_t

from logger_36 import L
from p_pattern.type.model.parameter.generic import (
    parameter_precision_h as point_precision_h,
)


def CheckPointConstraint(constraint: h.Any, dimension: int, /) -> None:
    """"""
    if constraint is None:
        return

    if isinstance(constraint, int | float | path_t):
        return

    if isinstance(constraint, h.Sequence):
        if not all(isinstance(_elm, point_precision_h) for _elm in constraint):
            L.StageIssue(
                "Invalid center precisions; All precisions must be integers or floats"
            )
        if constraint.__len__() != dimension:
            L.StageIssue(
                "Invalid number of center precisions",
                actual=constraint.__len__(),
                expected=dimension,
            )
    else:
        L.StageIssue(
            "Invalid center definition type",
            actual=type(constraint).__name__,
            expected="See documentation",
        )
