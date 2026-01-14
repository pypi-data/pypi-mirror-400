"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as sstm
from pathlib import Path as path_t

from conf_ini_g.api.console import CommandLineConfig, CommandLineParser
from conf_ini_g.api.functional import config_definition_h as config_raw_h
from conf_ini_g.api.functional import config_t as config_definition_t
from logger_36 import L
from logger_36.api.storage import SaveLOG
from logger_36.catalog.handler.memory import memory_handler_t
from logger_36.catalog.logger.chronos import LogElapsedTime
from logger_36.catalog.logger.memory import LogMemoryUsages
from logger_36.catalog.logger.system import LogSystemDetails
from obj_mpp.config.app import APP_NAME
from obj_mpp.constant.config.definition import DEFINITION
from obj_mpp.task.catalog.specifier import (
    SpecifyCatalogMarkedPoints,
    SpecifyCatalogQualities,
)
from obj_mpp.task.detection.multiple import DetectedObjects


def Main() -> None:
    """"""
    L.MakeRich()
    L.AddHandler(memory_handler_t)
    LogSystemDetails()

    config, _, ini_path = Config(APP_NAME, DEFINITION)
    config = config.active_as_typed_dict

    assert not L.has_staged_issues

    _ = DetectedObjects(config, ini_path)

    LogMemoryUsages()
    LogElapsedTime()
    SaveLOG(L.StoragePath("execution-log", suffix="htm"), layout="html")


def Config(
    title: str, definition_raw: config_raw_h, /
) -> tuple[config_definition_t, bool, path_t | None]:
    """"""
    definition = config_definition_t(definition_raw)
    SpecifyCatalogMarkedPoints(definition)
    SpecifyCatalogQualities(definition)

    parser = CommandLineParser(title, definition)
    config_cmdline, advanced_mode, ini_path = CommandLineConfig(parser)

    if (config_cmdline.__len__() == 0) and (ini_path is None):
        raise RuntimeError(
            "No Configuration passed, either as an INI file or "
            "as command-line arguments."
        )

    issues = definition.UpdateFromINI(ini_path)
    issues.extend(definition.UpdateFromDict(config_cmdline))
    if issues.__len__() > 0:
        # Issues can have has_actual_expected indicators. They are removed here.
        issues = (_ if isinstance(_, str) else _[0] for _ in issues)
        L.critical("!!!!\n" + "\n".join(issues) + "\n!!!!")
        sstm.exit(1)

    return definition, advanced_mode, ini_path


if __name__ == "__main__":
    #
    Main()
