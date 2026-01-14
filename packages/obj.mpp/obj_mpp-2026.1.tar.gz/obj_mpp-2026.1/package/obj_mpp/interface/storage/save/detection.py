"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import sys as sstm
import typing as h
from csv import writer as csv_saver_t

import imageio as mgio
import numpy as nmpy
from logger_36 import L
from obj_mpp.constant.interface.storage import MARKED_POINTS_BASE_NAME
from obj_mpp.task.analysis.illustration import (
    ContourMapOfDetection,
    RegionMapOfDetection,
)
from obj_mpp.task.analysis.signal import (
    SignalStatisticsInBackground,
    SignalStatisticsInMarkedPoint,
)
from p_pattern.type.instance.generic import instance_t
from p_pattern.type.model.generic import model_t


def SaveDetectionInCSVFormat(
    instances: h.Sequence[instance_t],
    model: model_t,
    signal_id: str | None,
    signal: h.Any | None,
    /,
    *,
    sep: str = ",",
) -> None:
    """
    Originally, the code used __class__ and isinstance. But this does not always work as
    expected!
    See https://stackoverflow.com/questions/10582774/python-why-can-isinstance-return-false-when-it-should-return-true
    for example.
    """
    if instances.__len__() == 0:
        return

    class_name = type(instances[0]).__name__
    if any(_elm.__class__.__name__ != class_name for _elm in instances[1:]):
        types = set(_elm.__class__.__name__ for _elm in instances)
        L.warning(f"Types: Mixed types in mkpt list in CSV output: {types}")

    path = L.StoragePath(
        f"{MARKED_POINTS_BASE_NAME}-{signal_id}", purpose="output", suffix="csv"
    )
    with open(path, "w", encoding=sstm.getfilesystemencoding()) as csv_accessor:
        csv_writer = csv_saver_t(csv_accessor, delimiter=sep)

        csv_writer.writerow(
            model.DescriptionHeader(educated_version=True)
            + SignalStatisticsInMarkedPoint(instances[0], signal, header_instead=True)
            + SignalStatisticsInBackground(None, signal)
        )

        bck_stat = SignalStatisticsInBackground(instances, signal)
        for instance in instances:
            csv_writer.writerow(
                instance.AsTuple(educated_version=True)
                + SignalStatisticsInMarkedPoint(instance, signal)
                + bck_stat
            )


def SaveDetectionAsContourImage(
    dimension: int,
    domain_lengths: tuple[int, ...],
    instances: h.Sequence[instance_t],
    signal_id: str | None,
    /,
) -> None:
    """"""
    if instances.__len__() == 0:
        return

    contour_map = ContourMapOfDetection(instances, domain_lengths)
    if dimension == 2:
        path = L.StoragePath(f"contour-{signal_id}", purpose="output", suffix="png")
        mgio.imwrite(path, contour_map)
    elif dimension == 3:
        path = L.StoragePath(f"contour-{signal_id}", purpose="output", suffix="tif")
        mgio.volwrite(path, contour_map)
    else:
        L.warning(f"Contour output in {dimension}-D not implemented")


def SaveDetectionAsRegionImage(
    dimension: int,
    domain_lengths: tuple[int, ...],
    instances: h.Sequence[instance_t],
    signal_id: str | None,
    /,
) -> None:
    """"""
    if instances.__len__() == 0:
        return

    region_map = RegionMapOfDetection(instances, domain_lengths)
    if dimension == 2:
        path = L.StoragePath(f"region-{signal_id}", purpose="output", suffix="png")
        mgio.imwrite(path, region_map)
    elif dimension == 3:
        path = L.StoragePath(f"region-{signal_id}", purpose="output", suffix="tif")
        mgio.volwrite(path, region_map)
    else:
        L.warning(f"Region output in {dimension}-D not implemented")


def SaveDetectionAsRegionNumpyArray(
    _: int,
    domain_lengths: tuple[int, ...],
    instances: h.Sequence[instance_t],
    signal_id: str | None,
    /,
) -> None:
    """"""
    if instances.__len__() == 0:
        return

    region_map = RegionMapOfDetection(instances, domain_lengths)
    path = L.StoragePath(f"region-{signal_id}", purpose="output", suffix="npz")
    nmpy.savez_compressed(path, detection=region_map)
