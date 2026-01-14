"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import multiprocessing as prll
import typing as h
from multiprocessing.managers import ListProxy as list_shared_t

from logger_36 import L
from logger_36.api.logger import logger_t
from logger_36.api.memory import FormattedObjectSizeHierarchy, ObjectSize
from logger_36.api.record import PROCESS_NAME_ATTR
from mpss_tools_36.api.data import AdditionalSharedCopy, DisposeSharedArrayCopy, line_t
from mpss_tools_36.api.data import client_t as data_client_t
from mpss_tools_36.api.data import server_t as data_server_t
from mpss_tools_36.api.feedback import send_feedback_h
from mpss_tools_36.api.wrapper import proxy_t
from mpss_tools_36.constant.process import MAIN_PROCESS_NAME
from obj_mpp.constant.catalog import MPM_CATALOG_SECTION, Q_CATALOG_SECTION
from obj_mpp.task.catalog.importer import ImportedElement
from obj_mpp.type.detection import detection_t
from p_pattern.extension.type import number_h
from p_pattern.type.instance.parameter.position import coordinate_h
from p_pattern.type.model.parameter import parameter_h as mark_h
from p_pattern.type.sampler.domain import chunked_domain_h, domain_h, interval_h
from p_pattern.type.sampler.instance import sampler_t


def DetectObjectsInOneChunk(
    detection_or_prm: detection_t | dict[str, h.Any],
    config_server_or_line: data_server_t | line_t,
    signal_server_or_line: data_server_t | line_t,
    logger_or_logger_line: logger_t | line_t | None,
    /,
    *,
    n_workers: int = 1,
    task_id: int = 0,
    lock: h.Any | None = None,
    output: list_shared_t[tuple[tuple[coordinate_h | mark_h, ...], ...]] | None = None,
    SendFeedback: send_feedback_h | None = None,
) -> None:
    """
    When called in sequential mode:
        - detection_or_prm is a detection,
        - domain is the full signal domain,
        - output is None since the detection serves as output,
        - previous_detection is None since the detection has been initialized with the
        history.
    When called in parallel mode:
        - detection_or_prm is a parameter dictionary,
        - domain is a domain chunk,
        - output is a multiprocessing.Manager (shared) list,
        - previous_detection is a list of instance descriptions in the domain chunk, or
        None.
    """
    if logger_or_logger_line is None:
        logger = L
    elif isinstance(logger_or_logger_line, logger_t):
        logger = logger_or_logger_line
    else:
        logger = proxy_t.New(server_line=logger_or_logger_line)
    if SendFeedback is None:
        SendFeedback = lambda _, __: None

    if (process_name := prll.current_process().name) != MAIN_PROCESS_NAME:
        extra = {"extra": {PROCESS_NAME_ATTR: process_name}}
    else:
        extra = {}

    if isinstance(config_server_or_line, data_server_t):
        server, server_line = config_server_or_line, None
    else:
        server, server_line = None, config_server_or_line
    config_client = data_client_t.New(server=server, server_line=server_line)
    if isinstance(signal_server_or_line, data_server_t):
        server, server_line = signal_server_or_line, None
    else:
        server, server_line = None, signal_server_or_line
    signal_client = data_client_t.New(server=server, server_line=server_line)

    model_t = ImportedElement(
        config_client.RequestedData("object")["definition"], MPM_CATALOG_SECTION
    )
    model = model_t()
    mark_ranges = config_client.RequestedData("mark_ranges")
    if not model.ShapeIntervalsAreValid(mark_ranges):
        logger.CommitIssues()
        SendFeedback(-1, 0)
        return

    model.SetShapeIntervals(mark_ranges)

    quality_context_t = ImportedElement(
        config_client.RequestedData("quality")["definition"], Q_CATALOG_SECTION
    )
    if quality_context_t is not None:
        quality_context_t = quality_context_t[0]

    if logger.has_staged_issues:
        logger.CommitIssues()
        SendFeedback(-1, 0)
        return

    signal_lengths = signal_client.RequestedData("signal_lengths")
    signal_domain = tuple((0, _ - 1) for _ in signal_lengths)
    map_or_pdf = signal_client.RequestedData("map_or_pdf")
    if map_or_pdf is None:
        domain, map_or_pdf_shared_memory = signal_domain, None
        precision = config_client.RequestedData("object")["center"]
        if isinstance(precision, number_h):
            precision = domain.__len__() * (float(precision),)
        # else: Must be a sequence of integers or floats.
        elif precision.__len__() != domain.__len__():
            logger.error(
                f"Mismatch between domain dimension ({domain.__len__()}) and "
                f"number of precisions ({precision.__len__()}).",
                **extra,
            )
            SendFeedback(-1, 0)
            return
    else:
        domain, map_or_pdf_shared_memory = AdditionalSharedCopy(map_or_pdf)
        precision = None
    if n_workers > 1:
        chunked_bounds = ChunkedBounds(signal_lengths, signal_domain, n_workers)
        before, chunks, after = chunked_bounds
        restriction = before + (chunks[task_id - 1],) + after
    else:
        restriction = None

    logger.SetCheckpoint("First initializations done", process_name=process_name)
    logger.RecordMemoryUsage(process_name=process_name)

    sampler = sampler_t(
        model=model,
        domain=domain,
        restriction=restriction,
        precision=precision,
        seed=config_client.RequestedData("mpp")["seed"],
    )
    if map_or_pdf_shared_memory is not None:
        DisposeSharedArrayCopy(map_or_pdf_shared_memory)
    if (sampler is None) or (sampler.position is None):
        logger.error("Position sampling cannot be done.", **extra)
        SendFeedback(-1, 0)
        return
    hierarchy = {}
    size = ObjectSize(sampler, hierarchy=hierarchy, lock=lock)
    hierarchy = FormattedObjectSizeHierarchy(hierarchy)
    logger.info(f"Sampler size: {size:_}\n{hierarchy}", **extra)

    logger.SetCheckpoint("Sampler instantiated", process_name=process_name)
    logger.RecordMemoryUsage(process_name=process_name)

    q_kwargs = (config_client.RequestedData("quality_prm"),)
    s_kwargs = (config_client.RequestedData("signal_processing_prm"),)
    if q_kwargs is None:
        q_kwargs = {}
    else:
        q_kwargs = dict(zip(q_kwargs[:-1:2], q_kwargs[1::2]))
    if s_kwargs is None:
        s_kwargs = {}
    else:
        s_kwargs = dict(zip(s_kwargs[:-1:2], s_kwargs[1::2]))
    quality_context = quality_context_t(domain=sampler.position.domain)
    quality_context.SetKwargs(q_kwargs, s_kwargs)

    signal_for_qty_name = signal_client.RequestedData("signal_for_qty")
    signal_for_qty, signal_for_qty_raw = AdditionalSharedCopy(signal_for_qty_name)
    if quality_context.SetSignal(signal_for_qty, sampler):
        logger.error("Signal skipped by quality context.", **extra)
        SendFeedback(-1, 0)
        return

    logger.SetCheckpoint("Quality context instantiated", process_name=process_name)
    logger.RecordMemoryUsage(process_name=process_name)

    if isinstance(detection_or_prm, detection_t):
        detection = detection_or_prm
        detection.sampler = sampler
    else:
        detection = detection_t(sampler=sampler, **detection_or_prm)

    for i_idx in range(1, detection.n_iterations + 1):
        candidates = detection.NewCandidates(quality_context)
        if candidates.__len__() > 0:
            detection.Update(candidates)
            detection.Refine(quality_context)

        SendFeedback(i_idx, detection.__len__())

    logger.SetCheckpoint("Detection iterations done", process_name=process_name)
    logger.RecordMemoryUsage(process_name=process_name)
    DisposeSharedArrayCopy(signal_for_qty_raw)

    detection.FilterOutCropped()

    if output is not None:
        with lock:
            output.append(
                (sampler.position.domain.lengths,)
                + tuple(_.as_tuple for _ in detection)
            )


def ChunkedBounds(
    lengths: tuple[int, ...], domain: domain_h, n_workers: int, /
) -> chunked_domain_h:
    """"""
    max_length = max(lengths)
    where = lengths.index(max_length)
    chunks = _ChunksForLength(n_workers, max_length)

    return domain[:where], chunks, domain[(where + 1) :]


def _ChunksForLength(n_workers: int, length: int, /) -> tuple[interval_h, ...]:
    """"""
    if n_workers < length:
        chunk_size = length // n_workers
        remainder = length % n_workers
        chunk_sizes = n_workers * [chunk_size]
        for chunk_idx in range(remainder):
            chunk_sizes[chunk_idx] += 1
    else:
        chunk_sizes = length * [1]

    output = [(0, chunk_sizes[0] - 1)]
    for chunk_idx, chunk_size in enumerate(chunk_sizes[1:]):
        last = output[chunk_idx][1]
        output.append((last + 1, last + chunk_size))

    return tuple(output)
