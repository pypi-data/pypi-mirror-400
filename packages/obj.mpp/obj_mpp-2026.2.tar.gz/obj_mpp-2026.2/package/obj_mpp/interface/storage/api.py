"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from pathlib import Path as path_t

signal_details_h = tuple[h.Any | None, Exception | None]


@h.runtime_checkable
class signal_loading_fct_p(h.Protocol):
    def __call__(self, path: path_t | None, /, **kwargs) -> signal_details_h: ...


instance_t = h.TypeVar("instance_t")


@h.runtime_checkable
class signal_output_fct_p(h.Protocol):
    def __call__(
        self,
        instances: h.Sequence[instance_t],
        signal: h.Any | None,
        path: path_t,
        /,
        *,
        signal_id: str = "",
        **kwargs,
    ) -> None: ...
