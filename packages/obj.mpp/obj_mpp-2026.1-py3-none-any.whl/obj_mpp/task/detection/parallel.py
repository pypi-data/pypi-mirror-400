"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import multiprocessing as prll
import typing as h
from multiprocessing import Process as process_t
from multiprocessing.managers import ListProxy as list_shared_t

from logger_36 import L
from mpss_tools_36.api.data import server_t as data_server_t
from mpss_tools_36.api.feedback import server_fake_t as feedback_server_fake_t
from mpss_tools_36.api.feedback import server_t as feedback_server_t
from mpss_tools_36.api.task import StartAndTrackTasks
from mpss_tools_36.api.wrapper import server_t as wrapping_server_t
from obj_mpp.task.detection.sequential import DetectObjectsInOneChunk
from p_pattern.type.instance.parameter.position import coordinate_h
from p_pattern.type.model.parameter import parameter_h as mark_h


def DetectObjectsInAllChunks(
    detection_prm: dict[str, h.Any],
    config_server: data_server_t,
    signal_server: data_server_t,
    n_workers: int,
    output: list_shared_t[tuple[tuple[coordinate_h | mark_h, ...], ...]],
    lock: h.Any,
    logger_wrapper: wrapping_server_t | None,
    feedback_server: feedback_server_t | feedback_server_fake_t,
    /,
    *,
    prefix: str = "",
) -> None:
    """"""
    if logger_wrapper is None:
        NewLoggerLine = lambda: None
    else:
        NewLoggerLine = lambda: logger_wrapper.NewLine()

    # Alternative: ProcessPoolExecutor + executor.submit + as_completed + .result().
    tasks = []
    for task_id in range(1, n_workers + 1):
        task = process_t(
            target=DetectObjectsInOneChunk,
            args=(
                detection_prm,
                config_server.NewLine(),
                signal_server.NewLine(),
                NewLoggerLine(),
            ),
            kwargs={
                "n_workers": n_workers,
                "task_id": task_id,
                "lock": lock,
                "output": output,
                "SendFeedback": feedback_server.NewFeedbackSendingFunction(),
            },
        )
        tasks.append(task)

    if logger_wrapper is not None:
        logger_wrapper.Start()
    config_server.Start()
    signal_server.Start()

    L.ToggleLogHolding(True)
    StartAndTrackTasks(tasks, prefix=prefix, feedback_server=feedback_server)
    L.ToggleLogHolding(False)

    config_server.Stop(should_dispose_shared_resources=False)
    signal_server.Stop()
    if logger_wrapper is not None:
        logger_wrapper.Stop()


def NParallelWorkers(hint: int, /) -> int:
    """"""
    if hint == 1:
        output = 1
    elif hint > 0:
        output = hint
    else:
        output = (3 * prll.cpu_count()) // 2

    return output
