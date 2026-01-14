"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import pprint as pprt
from pathlib import Path as path_t

from conf_ini_g.type.dict import config_typed_h
from json_any import JsonStringOf
from logger_36 import L
from logger_36.api.message import LINE_INDENT
from mpss_tools_36.api.data import server_t as data_server_t
from mpss_tools_36.api.task import SetStartMethod
from obj_mpp.constant.catalog import (
    I_CATALOG_SECTION,
    MPM_CATALOG_SECTION,
    O_CATALOG_SECTION,
)
from obj_mpp.constant.interface.storage import MARKED_POINTS_BASE_NAME
from obj_mpp.interface.console.detection import ReportDetectedMarkedPoints
from obj_mpp.interface.storage.save import detection as svdt
from obj_mpp.task.catalog.importer import ImportedElement
from obj_mpp.task.detection import parallel as prll
from obj_mpp.task.detection.single import DetectedObjects as DetectedObjectsSingle
from obj_mpp.task.validation.interface import CheckOutputFunction, CheckRequestedOutputs
from obj_mpp.type.signal.context import signal_context_t
from p_pattern.type.instance.generic import instance_t as base_instance_t

SaveDetection = dict(
    zip(
        ("contour", "region", "region_numpy"),
        (
            svdt.SaveDetectionAsContourImage,
            svdt.SaveDetectionAsRegionImage,
            svdt.SaveDetectionAsRegionNumpyArray,
        ),
        strict=True,
    )
)


def DetectedObjects(
    config: config_typed_h, ini_path: path_t | None, /
) -> dict[path_t, list[base_instance_t]]:
    """"""
    output = {}

    # --- Logging
    if (folder := config["output"]["base_folder"]) is not None:
        L.SetFolder(folder)
        if ini_path is not None:
            L.file(ini_path, purpose="input")
        L.value(
            "config-processed",
            layout="str",
            purpose="input",
            suffix="txt",
            config=pprt.pformat(config, sort_dicts=True),
        )
    if config["output"]["memory_usage"]:
        L.ActivateMemoryUsageMonitoring()

    # --- Model
    model_t = ImportedElement(config["object"]["definition"], MPM_CATALOG_SECTION)
    model = model_t()
    dimension = model.dimension

    # --- Signal
    LoadedSignalMapOrPDF = ImportedElement(
        config["signal"]["loading_function"], I_CATALOG_SECTION
    )
    signal_context = signal_context_t(
        signal_path_or_folder=config["signal"]["path"],
        map_or_pdf_path_or_folder=config["object"]["center"],
    )

    # --- Output
    requested_outputs = config["output"]["what"]
    if requested_outputs is None:
        requested_outputs = ()
    else:
        requested_outputs = tuple(map(str.strip, requested_outputs.split(",")))
        CheckRequestedOutputs(requested_outputs)
    if config["output"]["output_function"] in (None, "", "none", "None"):
        ReportDetectionResult = None
    else:
        ReportDetectionResult = ImportedElement(
            config["output"]["output_function"], O_CATALOG_SECTION
        )
        CheckOutputFunction(ReportDetectionResult, config["output_prm"])

    # --- Computing: sequential or parallel
    n_workers = prll.NParallelWorkers(config["mpp"]["n_parallel_workers"])
    start_method = config["mpp"]["parallel_method"]
    if n_workers > 1:
        if SetStartMethod(start_method):
            L.ToggleShareability(True)
        else:
            n_workers = 1
            L.warning(
                f"Parallel computing cannot be used "
                f'due to unsupported process start method "{start_method}"'
            )

    # --- Servers: config, signal, logging
    config_server = data_server_t(name="config", data=config)
    signal_server = data_server_t(name="signal", is_read_only=False)
    if n_workers > 1:
        logger_wrapper = None  # Trust logger_36.L shareability.
        # Alternative (do not rely on logger_36.L shareability):
        # from mpss_tools_36.api.wrapper import server_t as wrapping_server_t
        # logger_wrapper = wrapping_server_t(name="logger", object=L)
    else:
        logger_wrapper = None

    signal_server.Store(map_or_pdf=None)  # No map or PDF by default.

    # --- Loop over signals
    for signal_idx, (
        signal_path,
        signal_is_valid,
        _,  # signal_is_new
        signal_id,
        map_or_pdf_path,
        map_or_pdf_is_valid,
        map_or_pdf_is_new,
        __,  # map_or_pdf_id
    ) in enumerate(signal_context.SignalDetails(), start=1):
        L.DisplayRule()
        L.info(
            f"Signal#{signal_idx}: {signal_path} / "
            f"MAP-or-PDF {map_or_pdf_path} (New: {map_or_pdf_is_new})"
        )

        L.SetCheckpoint(f"Ready for signal {signal_idx}")

        if (not signal_is_valid) or (
            (map_or_pdf_path is not None) and not map_or_pdf_is_valid
        ):
            L.error(
                f"Invalid signal(s):\n"
                f"    {signal_path}:{signal_is_valid}\n"
                f"    {map_or_pdf_path}:{map_or_pdf_is_valid}"
            )
            continue

        if not _LoadSignalAndSendToServer(
            signal_path,
            signal_context,
            dimension,
            LoadedSignalMapOrPDF,
            signal_server,
            **config["signal_loading_prm"],
        ):
            continue
        if (map_or_pdf_path is not None) and (
            map_or_pdf_is_new or (signal_context.map_or_pdf is None)
        ):
            # map_or_pdf_is_new is False and signal_context.map_or_pdf is None if using
            # the same map or pdf for all signals, but the previous signals were all
            # unloadable (which means that execution did not reach this point when
            # map_or_pdf_is_new was True for this first signal).
            if not _LoadMapOrPDFAndSendToServer(
                map_or_pdf_path,
                signal_context,
                LoadedSignalMapOrPDF,
                signal_server,
                **config["signal_loading_prm"],
            ):
                continue

        L.info(f"Signal server size: {signal_server.size:_}")
        L.SetCheckpoint(f"Signal {signal_idx} loaded")
        L.RecordMemoryUsage()

        local_output = DetectedObjectsSingle(
            config,
            config_server,
            signal_server,
            n_workers=n_workers,
            logger_wrapper=logger_wrapper,
            prefix=LINE_INDENT,
        )
        output[signal_path] = local_output

        L.RecordMemoryUsage()

        if L.has_staged_issues:
            L.CommitIssues()
            continue

        if local_output.__len__() == 0:
            continue

        if config["output"]["console"]:
            ReportDetectedMarkedPoints(local_output, model)

        if L.folder is not None:
            L.info(f"Saving detection result to {L.folder}...")
            if "csv" in requested_outputs:
                svdt.SaveDetectionInCSVFormat(
                    local_output,
                    model,
                    signal_id,
                    signal_context.signal_original,
                    sep=config["output"]["marks_separator"],
                )
            if "json" in requested_outputs:
                L.value(
                    f"{MARKED_POINTS_BASE_NAME}-{signal_id}",
                    purpose="output",
                    suffix="json",
                    StorableValue=lambda _: str(JsonStringOf(_)[0]),
                    detection=local_output,
                )
            for what in requested_outputs:
                if what not in ("csv", "json"):
                    SaveDetection[what](
                        dimension, signal_context.lengths, local_output, signal_id
                    )

        # Leave here so that in case it contains blocking instructions (like matplotlib
        # show()), it does not delay saving to files above.
        if ReportDetectionResult is not None:
            L.info(
                f"Reporting detection result with {ReportDetectionResult.__name__}..."
            )
            L.SetCheckpoint(f"Reporting for signal {signal_idx}")
            ReportDetectionResult(
                model,
                local_output,
                signal_context.signal_original,
                signal_context.lengths,
                **config["output_prm"],
            )

    if n_workers > 1:
        L.ToggleShareability(False)
    L.RecordMemoryUsage()

    return output


def _LoadSignalAndSendToServer(
    path: path_t,
    context: signal_context_t,
    dimension: int,
    LoadedSignal,
    server: data_server_t,
    **signal_loading_prm,
) -> bool:
    """"""
    loaded, error = LoadedSignal(path, **signal_loading_prm)
    if error is None:
        context.SetSignals(loaded, dimension)

        L.info(
            f"{path}:\n"
            f"    shape={context.signal_original.shape}\n"
            f"    size={context.signal_original.nbytes / 10**6:_.3f}MB"
        )
        L.info(
            f"Signal for Quality:\n"
            f"    shape={context.signal_for_qty.shape}\n"
            f"    size={context.signal_for_qty.nbytes / 10**6:_.3f}MB"
        )
        L.RecordMemoryUsage()

        server.Store(
            signal_lengths=context.lengths, signal_for_qty=context.signal_for_qty
        )
        L.RecordMemoryUsage()
        context.signal_for_qty = None
        return True

    L.error(f"Unable to load {path}:\n{error}")
    return False


def _LoadMapOrPDFAndSendToServer(
    path: path_t,
    context: signal_context_t,
    LoadedMapOrPDF,
    server: data_server_t,
    **signal_loading_prm,
) -> bool:
    """"""
    loaded, error = LoadedMapOrPDF(path, **signal_loading_prm)
    if error is None:
        context.SetMapOrPDF(loaded)

        L.info(
            f"{path}:\n"
            f"    shape={context.map_or_pdf.shape}\n"
            f"    size={context.map_or_pdf.nbytes / 10**6:_.3f}MB"
        )
        L.RecordMemoryUsage()

        server.Store(map_or_pdf=context.map_or_pdf)
        L.RecordMemoryUsage()
        context.map_or_pdf = None
        return True

    L.error(f"Unable to load {path}:\n{error}")
    return False
