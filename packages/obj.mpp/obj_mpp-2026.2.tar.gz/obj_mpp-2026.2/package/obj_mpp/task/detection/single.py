"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from multiprocessing import Manager as NewSharingManager

import numpy as nmpy
import obj_mpp.task.detection.parallel as prll
from conf_ini_g.api.functional import config_typed_h
from logger_36 import L
from logger_36.api.message import LINE_INDENT
from mpss_tools_36.api.data import server_t as data_server_t
from mpss_tools_36.api.feedback import server_fake_t as feedback_server_fake_t
from mpss_tools_36.api.feedback import server_t as feedback_server_t
from mpss_tools_36.api.wrapper import server_t as wrapping_server_t
from obj_mpp.task.detection.sequential import DetectObjectsInOneChunk
from obj_mpp.type.detection import detection_t
from p_pattern.type.instance.generic import instance_t

array_t = nmpy.ndarray


def DetectedObjects(
    config: config_typed_h,
    config_server: data_server_t,
    signal_server: data_server_t,
    /,
    *,
    n_workers: int = 1,
    logger_wrapper: wrapping_server_t | None = None,
    prefix: str = "",
) -> list[instance_t]:
    """"""
    n_new_per_iteration = config["mpp"]["n_new_per_iteration"] // n_workers
    if n_new_per_iteration == 0:
        L.warning(
            "Number of generated marked points in each chunk per iteration is zero."
        )
        return []

    detection_prm = {
        "instance_tt": config["object"]["definition"],
        "max_overlap": config["constraints"]["max_overlap"],
        "min_quality": config["quality"]["min_value"],
        "only_un_cropped": config["object"]["only_un_cropped"],
        "n_iterations": config["mpp"]["n_iterations"],
        "n_new_per_iteration": n_new_per_iteration,
        "refinement_interval": config["refinement"]["interval"],
        "n_new_per_refinement": config["refinement"]["n_attempts"],
        "max_refinement_variation": config["refinement"]["max_variation"],
    }
    detection = detection_t(**detection_prm)

    if config["output"]["feedback"] == "true":
        actual_feedback_server_t = feedback_server_t
    else:
        actual_feedback_server_t = feedback_server_fake_t
    feedback_server = actual_feedback_server_t(
        n_iterations_per_task=detection_prm["n_iterations"],
        feedback_period=2,
        print_report=True,
        prefix=LINE_INDENT,
    )

    L.SetCheckpoint("Ready for detection")

    if n_workers > 1:
        sharing_manager = NewSharingManager()
        output = sharing_manager.list()
        lock = sharing_manager.Lock()

        prll.DetectObjectsInAllChunks(
            detection_prm,
            config_server,
            signal_server,
            n_workers,
            output,
            lock,
            logger_wrapper,
            feedback_server,
            prefix=prefix,
        )

        if output.__len__() == n_workers:
            L.info(
                f"Marked point(s) per task: {tuple(_.__len__() - 1 for _ in output)}"
            )
            domain_lengths = output[0][0]
            grid_sites = tuple(nmpy.indices(domain_lengths))
            for from_chunk_w_lengths in output:
                from_chunk = from_chunk_w_lengths[1:]
                if from_chunk.__len__() == 0:
                    continue
                detection.Update(
                    from_chunk,
                    domain_lengths=domain_lengths,
                    grid_sites=grid_sites,
                    live_mode=False,
                )
        else:
            L.error(
                f"Only {output.__len__()} worker(s) out of {n_workers} run thoroughly"
            )

        sharing_manager.shutdown()
    else:
        L.ToggleLogHolding(True)
        SendFeedback = feedback_server.NewFeedbackSendingFunction()
        feedback_server.Start()

        DetectObjectsInOneChunk(
            detection, config_server, signal_server, L, SendFeedback=SendFeedback
        )

        feedback_server.Stop()
        L.ToggleLogHolding(False)

        signal_server.DisposeSharedResources()

    L.SetCheckpoint("Detection done")

    return detection.AsListWithDecreasingQualities()
