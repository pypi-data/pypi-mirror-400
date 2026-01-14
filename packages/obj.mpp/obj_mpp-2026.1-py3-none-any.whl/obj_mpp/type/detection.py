"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import typing as h
from pathlib import Path as path_t

import networkx as ntwx
import numpy as nmpy
from obj_mpp.constant.signal import INFINITY_NUMPY_FLOAT
from obj_mpp.type.quality.base import quality_context_t
from p_pattern.type.instance.generic import description_h, instance_t
from p_pattern.type.sampler.instance import sampler_t
from obj_mpp.task.catalog.importer import ImportedElement
from obj_mpp.constant.catalog import MPI_CATALOG_SECTION

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class detection_t(list[instance_t]):
    instance_tt: type[instance_t] | str | path_t
    max_overlap: float
    min_quality: float
    only_un_cropped: bool
    #
    n_iterations: int
    n_new_per_iteration: int
    refinement_interval: int | None
    n_new_per_refinement: int
    max_refinement_variation: float
    #
    sampler: sampler_t | None = None
    n_non_blank_its: int = 0
    n_refinement_attempts: int = 0
    n_refinement_successes: int = 0

    def __post_init__(self) -> None:
        """"""
        if isinstance(self.instance_tt, str | path_t):
            self.instance_tt = ImportedElement(self.instance_tt, MPI_CATALOG_SECTION)
        if self.refinement_interval is None:
            self.refinement_interval = self.n_iterations + 1

    @property
    def refinement_efficiency(self) -> int:
        """"""
        return int(
            round(
                100.0 * self.n_refinement_successes / max(1, self.n_refinement_attempts)
            )
        )

    def NewCandidates(self, quality_context: quality_context_t, /) -> list[instance_t]:
        """
        Returns a list of non-intersecting marked point candidates.

        Note that a list, as opposed to a tuple, must be returned (see Update: addition
        with self). This list can be empty due to min_quality filtering.

        One can also visualize the sampling with (sampling_map being initially all 0's):
        sites = tuple(nmpy.rint(_elm).astype(nmpy.int64, copy=False) for _elm in points)
        sampling_map[sites] += 1
        """
        output = []

        for new_sample in self.instance_tt.NewSamples(
            self.sampler, self.n_new_per_iteration
        ):  # self.sampler.Instances(self.n_new_per_iteration):
            # new_sample = self.instance_tt(position, shape, domain_lengths, grid_sites)
            new_sample.properties["age"] = 0
            if new_sample.area == 0:
                continue

            # Assumption: intersection computation costs less than quality computation.
            # Hence the order of the tests below.
            for sample in output:
                if new_sample.Intersects(sample, self.max_overlap):
                    break
            else:
                quality = quality_context.Quality(new_sample)
                if quality >= self.min_quality:
                    new_sample.properties["quality"] = quality
                    output.append(new_sample)

        return output

    def Update(
        self,
        newly_detected: list[instance_t] | tuple[description_h, ...],
        /,
        *,
        domain_lengths: tuple[int, ...] | None = None,
        grid_sites: tuple[array_t, ...] | None = None,
        live_mode: bool = True,
    ) -> None:
        """"""
        if not isinstance(newly_detected[0], self.instance_tt):
            NewFromTuple = lambda _: self.instance_tt.NewFromTuple(
                _, domain_lengths, grid_sites
            )
            newly_detected = list(map(NewFromTuple, newly_detected))

        graph = ntwx.Graph()
        for new_instance in newly_detected:
            # sfr=so far
            sfr_w_intersection = tuple(
                _ for _ in self if new_instance.Intersects(_, self.max_overlap)
            )
            if sfr_w_intersection.__len__() == 0:
                continue

            for sfr_instance in sfr_w_intersection:
                if sfr_instance not in graph:
                    graph.add_edge(
                        "SO_FAR",
                        sfr_instance,
                        capacity=sfr_instance.properties["quality"],
                    )
                    graph.add_edge(
                        "NEW",
                        sfr_instance,
                        capacity=-sfr_instance.properties["quality"],
                    )
                # From the documentation of ntwx.minimum_cut: "Edges of the graph are
                # expected to have an attribute called ‘capacity’. If this attribute is
                # not present, the edge is considered to have infinite capacity." So, in
                # principle, setting capacity to INFINITY_NUMPY_FLOAT is useless. But...
                graph.add_edge(
                    new_instance, sfr_instance, capacity=INFINITY_NUMPY_FLOAT
                )

            graph.add_edge(
                "SO_FAR", new_instance, capacity=-new_instance.properties["quality"]
            )
            graph.add_edge(
                "NEW", new_instance, capacity=new_instance.properties["quality"]
            )

        if graph.number_of_nodes() > 0:
            isolated = set(self + newly_detected).difference(graph.nodes())

            # Note: do not write self = ... since it will leave the original list
            # unchanged, assigning to a new, local list. Hence the deletions below.
            _, (so_far_better, new_better) = ntwx.minimum_cut(graph, "SO_FAR", "NEW")
            for idx in range(self.__len__() - 1, -1, -1):
                if self[idx] not in so_far_better:
                    del self[idx]
            self.extend(_elm for _elm in newly_detected if _elm in new_better)
            self.extend(isolated)

            # The below sorting is useful when seeding pseudo-random number generation.
            # Indeed, in that case, the object detection is requested to be
            # reproducible. However, either "ntwx.minimum_cut" or "set" above (or both)
            # does not return sequences in deterministic order.
            self.sort(key=lambda _arg: _arg.as_sortable)
        else:
            self.extend(newly_detected)

        if live_mode:
            for instance in self:
                instance.properties["age"] += 1

            self.n_non_blank_its += 1

    def Refine(self, quality_context: quality_context_t, /) -> None:
        """"""
        # Since self can change (in some way; see below) inside the loop, it might be
        # preferable not to use enumerate below. However, it does not change length, so
        # that "range on length" should be ok.
        for idx in range(self.__len__()):
            instance = self[idx]
            if instance.properties["age"] >= self.refinement_interval:
                # Reset its age so that the algorithm does not try to improve it at each
                # next iteration (if it is not replaced by the refinement).
                instance.properties["age"] = 0
                self._RefineInstance(instance, idx, quality_context)

    def _RefineInstance(
        self, instance: instance_t, index: int, quality_context: quality_context_t, /
    ) -> None:
        """"""
        self.n_refinement_attempts += 1

        samples = instance.NewSimilarSamples(
            self.sampler,
            self.n_new_per_refinement,
            fraction=self.max_refinement_variation,
        )
        qualities = []
        for sample in samples:
            quality = quality_context.Quality(sample)
            qualities.append(quality)
            sample.properties["quality"] = quality

        reference = instance.properties["quality"]
        from_high_to_low = nmpy.flipud(nmpy.argsort(qualities))
        for qty_idx in from_high_to_low:
            if qualities[qty_idx] <= reference:
                break

            better = samples[qty_idx]
            for so_far in self:
                if so_far is instance:
                    continue
                if better.Intersects(so_far, self.max_overlap):
                    break
            else:
                better.properties["age"] = 0
                self[index] = better
                self.n_refinement_successes += 1

    def FilterOutCropped(self) -> None:
        """
        Cropped instances were initially not considered at all (filtered out in
        NewCandidates and SimilarSamples). However, this can lead to bad (but still
        "good" enough) instances touching or almost touching a border. Instead, the
        cropped instances are now kept to prevent such bad, border-touching instances,
        and removed only at the end here.
        """
        if self.only_un_cropped:
            for idx in range(self.__len__() - 1, -1, -1):
                if self[idx].crosses_border:
                    del self[idx]

    def AsListWithDecreasingQualities(self) -> list[instance_t]:
        """"""
        return sorted(self, key=lambda _arg: _arg.properties["quality"], reverse=True)


def NormalizedQualities(
    instances: h.Sequence[instance_t] | detection_t, /
) -> dict[str, array_t]:
    """"""
    output = {}

    qualities = nmpy.array(tuple(_.properties["quality"] for _ in instances))
    output["original"] = qualities.copy()

    where_infinite = nmpy.isinf(qualities)
    if where_infinite.all():
        qualities[qualities == -INFINITY_NUMPY_FLOAT] = 0.0
        qualities[qualities == INFINITY_NUMPY_FLOAT] = 1.0

        min_quality = min(qualities)
        max_quality = max(qualities)
        q_extent = max_quality - min_quality
    elif where_infinite.any():
        non_inf_qualities = qualities[nmpy.logical_not(where_infinite)]
        min_quality = min(non_inf_qualities)
        max_quality = max(non_inf_qualities)
        if max_quality == min_quality:
            quality_margin = 1.0
            q_extent = 2.0 * quality_margin
        else:
            q_extent = max_quality - min_quality
            # If qualities.size == 1.0, then max_quality == min_quality,
            # so the previous code path is taken instead.
            quality_margin = q_extent / (qualities.size - 1.0)
            q_extent += 2.0 * quality_margin

        qualities[qualities == -INFINITY_NUMPY_FLOAT] = min_quality - quality_margin
        qualities[qualities == INFINITY_NUMPY_FLOAT] = max_quality + quality_margin

        min_quality -= quality_margin
        max_quality += quality_margin
    else:
        min_quality, max_quality = min(qualities), max(qualities)
        q_extent = max_quality - min_quality

    if q_extent == 0.0:
        q_extent = 1.0
        # Hence, (qualities[idx] - min_quality) / q_extent == 1
        min_quality -= 1.0

    output["un_infinite_ized"] = qualities
    output["normalized"] = (qualities - min_quality) / q_extent
    output["pushed_against_1"] = 0.7 * output["normalized"] + 0.3

    return output
