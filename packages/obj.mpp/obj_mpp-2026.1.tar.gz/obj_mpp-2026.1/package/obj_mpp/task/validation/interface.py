"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from logger_36 import L
from obj_mpp.constant.config.parameter import VALID_REQUESTED_OUTPUTS
from obj_mpp.extension.function import CheckPassedParameters
from obj_mpp.interface.storage.api import (
    signal_details_h,
    signal_loading_fct_p,
    signal_output_fct_p,
)


def CheckLoadingFunction(
    SignalLoading_fct: signal_loading_fct_p | None, loading_prm: dict[str, h.Any], /
) -> None:
    """"""
    if SignalLoading_fct is None:
        return

    CheckPassedParameters(SignalLoading_fct, loading_prm, signal_details_h)


def CheckOutputFunction(
    SignalOutput_fct: signal_output_fct_p | None, output_prm: dict[str, h.Any], /
) -> None:
    """"""
    if SignalOutput_fct is None:
        return

    CheckPassedParameters(SignalOutput_fct, output_prm, None)


def CheckRequestedOutputs(requested_outputs: tuple[str, ...], /) -> None:
    """"""
    if any(_elm not in VALID_REQUESTED_OUTPUTS for _elm in requested_outputs):
        actual = ", ".join(requested_outputs)
        L.StageIssue(
            f"At least one invalid requested output",
            actual=actual,
            expected=VALID_REQUESTED_OUTPUTS,
        )
