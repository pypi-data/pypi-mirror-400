"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h

from logger_36 import L
from p_pattern.type.instance.generic import instance_t
from p_pattern.type.sampler.domain import educated_domain_t as domain_t
from p_pattern.type.sampler.instance import sampler_t


@d.dataclass(slots=True, repr=False, eq=False)
class quality_context_t:
    """
    s_kwargs: for use in raw signal conversion into a signal used for quality
        computation.
    q_kwargs: marked-point-related; for use in quality computation.
    """

    domain: domain_t

    s_defaults: h.ClassVar[dict[str, h.Any]] = {}
    q_defaults: h.ClassVar[dict[str, h.Any]] = {}

    signal: h.Any = None
    s_kwargs: dict[str, h.Any] | None = None
    q_kwargs: dict[str, h.Any] | None = None

    def SetKwargs(
        self, q_kwargs: dict[str, h.Any], s_kwargs: dict[str, h.Any], /
    ) -> None:
        """"""
        self._SetKwargsWithDefaults(
            q_kwargs, self.q_defaults, s_kwargs, self.s_defaults
        )

    def _SetKwargsWithDefaults(
        self,
        q_kwargs: dict[str, h.Any],
        q_defaults: dict[str, h.Any],
        s_kwargs: dict[str, h.Any],
        s_defaults: dict[str, h.Any],
        /,
    ) -> None:
        """"""
        for kwargs, defaults in ((q_kwargs, q_defaults), (s_kwargs, s_defaults)):
            invalid_s = set(kwargs.keys()).difference(defaults.keys())
            if invalid_s.__len__() > 0:
                invalid_s = ", ".join(invalid_s)
                L.StageIssue(
                    f"Invalid quality signal or quality parameter(s): {invalid_s}"
                )

            for name, value in defaults.items():
                if name not in kwargs:
                    kwargs[name] = value

        self.q_kwargs = q_kwargs
        self.s_kwargs = s_kwargs

    def SetSignal(self, raw_signal: h.Any, sampler: sampler_t, /) -> bool:
        """
        The returned value has a "signal is invalid" meaning. Consequently, any current
        procedure should abort.

        Default implementation: identity. The raw signal is also required to have the
        same dimension as the marked point model since this is probably a common
        requisite for quality computation. In case it is not, then SetSignalUnsafe can
        be "renamed" to SetSignal in derived quality context classes.
        """
        if raw_signal.ndim != sampler.model.dimension:
            return True

        self.signal = raw_signal
        return False

    def SetSignalUnsafe(self, raw_signal: h.Any, /) -> bool:
        """
        See SetSignal.
        """
        self.signal = raw_signal
        return False

    def Quality(self, instance: instance_t, /) -> float:
        """"""
        raise NotImplementedError
