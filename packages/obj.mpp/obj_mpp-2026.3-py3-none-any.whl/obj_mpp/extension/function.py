"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import inspect as nspt
import types as t
import typing as h

from logger_36 import L

parameter_t = nspt.Parameter

UNSUPPORTED_PARAMETER_KINDS = (
    parameter_t.POSITIONAL_OR_KEYWORD,
    parameter_t.VAR_POSITIONAL,
    parameter_t.VAR_KEYWORD,
)


class signature_t(h.NamedTuple):
    """
    kwargs: {name: (type, default_value)}.
    type[Any] is used as a simplified version of type[Any] | complex_type_hint.
    """

    has_unsupported: bool
    kwargs: dict[str, tuple[h.Any, h.Any]]
    return_type: type | t.GenericAlias | None

    @classmethod
    def Of(cls, function: h.Callable, /) -> h.Self:
        """"""
        signature = nspt.signature(function)

        has_unsupported = False
        kwargs = {}
        for name, value in signature.parameters.items():
            if value.kind == parameter_t.KEYWORD_ONLY:
                kwargs[name] = (value.annotation, value.default)
            elif value.kind in UNSUPPORTED_PARAMETER_KINDS:
                has_unsupported = True

        return cls(
            has_unsupported=has_unsupported,
            kwargs=kwargs,
            return_type=signature.return_annotation,
        )


def CheckPassedParameters(
    Function: h.Callable,
    parameters: dict[str, h.Any],
    expected_type: type | t.GenericAlias | None,
    /,
) -> None:
    """"""
    signature = signature_t.Of(Function)
    if signature.has_unsupported:
        L.StageIssue(
            f"{Function.__name__} has parameter(s) with unsupported kind. "
            f"Supported kinds are {parameter_t.POSITIONAL_ONLY} "
            f"and {parameter_t.KEYWORD_ONLY}."
        )

    if signature.return_type != expected_type:
        L.StageIssue(
            f"{Function.__name__}: Invalid return type(s)",
            actual=signature.return_type,
            expected=expected_type,
        )

    valid_names = tuple(signature.kwargs.keys())
    for name, value in parameters.items():
        if name in signature.kwargs:
            stripe = signature.kwargs[name][0]
            if not isinstance(value, stripe):
                L.StageIssue(
                    f"Incorrect parameter type passed for {Function.__name__}:{name}",
                    actual=f"{value} with type {type(value).__name__}",
                    expected=stripe,
                )
        else:
            L.StageIssue(
                f"Invalid parameter passed to {Function.__name__}",
                actual=name,
                expected=valid_names,
                expected_is_choices=True,
            )
