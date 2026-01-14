"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import re as regx
import sys as sstm

from conf_ini_g.api.functional import config_t, section_controlled_t, section_free_t
from conf_ini_g.api.functional import prm_t as parameter_t
from obj_mpp.constant.config.definition import DEFINITION
from rich import print as rprint
from value_factory.api.constant import UNSET


def QueryResult(query: str, /) -> None:
    """"""
    query = query.lower()

    for s_name, section in config_t(definition=DEFINITION).items():
        if query in s_name.lower():
            rprint(f"[blue]\\[{s_name}][/]", end="")
            _PrintSectionDetails(section, query)
            if section.__len__() > 0:
                for p_name, prm in section.prm_iterator:
                    _PrintParameterDetails(p_name, prm, query)
                rprint("")
        else:
            for p_name, prm in section.prm_iterator:
                if any(
                    query in _elm
                    for _elm in (p_name, prm.ppt.short, prm.ppt.long)
                    if isinstance(_elm, str)
                ):
                    rprint(f"[blue]\\[{s_name}]", end="")
                    _PrintSectionDetails(section, query)
                    _PrintParameterDetails(p_name, prm, query)
                    rprint("")


def _PrintSectionDetails(
    section: section_controlled_t | section_free_t, query: str, /
) -> None:
    """"""
    rprint(
        f" {_WithEmphasizedWord(section.ppt.short, query)} / "
        f"cat={section.ppt.category} / "
        f"adv.opt={not section.ppt.basic}.{section.ppt.optional}"
    )


def _PrintParameterDetails(name: str, parameter: parameter_t, query: str, /) -> None:
    """"""
    if parameter.default is UNSET:
        prm_default = "No defaults"
    else:
        prm_default = parameter.default
    rprint(
        f"\n    [magenta]{name}[/]: "
        f"{_WithEmphasizedWord(parameter.ppt.short, query)}\n"
        f"        def={prm_default}\n"
        f"        type={parameter.hint}\n"
        f"        adv.opt={not parameter.ppt.basic}.{parameter.ppt.optional}"
    )


def _WithEmphasizedWord(sentence: str, word: str, /) -> str:
    """"""
    return regx.sub(
        word, lambda wrd: f"[green]{wrd[0]}", sentence, flags=regx.IGNORECASE
    )


def Main() -> None:
    """"""
    if sstm.argv.__len__() > 1:
        QueryResult(sstm.argv[1])


if __name__ == "__main__":
    #
    Main()
