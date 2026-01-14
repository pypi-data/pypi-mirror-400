"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from pathlib import Path as pl_path_t

from conf_ini_g.api.functional import ctl_t, ppt_t, prm_t
from obj_mpp.constant.config.label import label_e
from value_factory.api.catalog import (
    choices_t,
    collection_t,
    number_t,
    path_kind_e,
    path_purpose_e,
    path_t,
)

DEFINITION = {
    "mpp": {  # label_e.sct_mpp.value
        "": ppt_t(
            category=label_e.cat_optimization.value,
            short="Main Obj.MPP parameters",
            long="Algorithmic parameters of Obj.MPP.",
            basic=True,
            optional=False,
        ),
        "n_iterations": prm_t(
            hint=h.Annotated[int, number_t(min=1)],
            ppt=ppt_t(
                short="Number of iterations",
                long="Number of rounds (or iterations) of random candidate object generation. There is no default value.",
                basic=True,
            ),
        ),
        "n_new_per_iteration": prm_t(
            hint=h.Annotated[int, number_t(min=1)],
            default=100,
            ppt=ppt_t(
                short='Number of object "births" at each iteration',
                long="Number of new, random candidate objects generated at each iteration. "
                "This could be set equal to the expected number of objects in the signal "
                "although there is no guarantee that this order of magnitude is optimal "
                "in terms of detection_performance-vs-computation_time trade-off. "
                "The total number of candidate objects generated will be "
                '"n_iterations x n_new_per_iteration". '
                "The default value is 20.",
                basic=False,
            ),
        ),
        "seed": prm_t(
            hint=h.Annotated[int, number_t(min=0, max=2**32 - 1)] | None,
            default=None,
            ppt=ppt_t(
                short="Seed for pseudo-random number generation",
                long="The seed used to initialize the pseudo-random number generator "
                "used to build random candidate objects. This parameter should usually be ignored. "
                'It is mainly used to make the randomness in Obj.MPP "predictable" '
                "when testing or debugging. "
                "If None, there is no specific seeding."
                "The default value is None.",
                basic=False,
            ),
        ),
        "n_parallel_workers": prm_t(
            hint=int,
            default=0,
            ppt=ppt_t(
                short="Number of parallel detection subtasks",
                long="Number of subtasks the detection task will be split into to be run in parallel. "
                "If equal to 1, the detection task will be run sequentially. "
                "If > 1, that number of subtasks will be used. "
                "If <= 0, Obj.MPP will choose the number of subtasks based on the number of CPU cores. "
                "Note that this parameter is ignored on Windows, falling back to sequential processing "
                '(see the documentation of the "fork" start method in the "multiprocessing" Python module). '
                "The default value is 0.",
                basic=False,
            ),
        ),
        "parallel_method": prm_t(
            hint=h.Annotated[str, choices_t(("fork", "forkserver", "spawn"))],
            default="forkserver",
            ppt=ppt_t(
                short="Which process start method to use", basic=False
            ),
        ),
    },
    "refinement": {  # label_e.sct_refinement.value
        "": ppt_t(
            category=label_e.cat_optimization.value,
            short="Refinement parameters",
            basic=False,
            optional=True,
        ),
        "interval": prm_t(
            hint=h.Annotated[int, number_t(min=0)] | None,
            default=None,
            ppt=ppt_t(basic=False),
        ),
        "n_attempts": prm_t(
            hint=h.Annotated[int, number_t(min=1)], default=10, ppt=ppt_t(basic=False)
        ),
        "max_variation": prm_t(
            hint=h.Annotated[float, number_t(min=0.0, min_inclusive=False)],
            default=0.1,
            ppt=ppt_t(basic=False),
        ),
    },
    "feedback": {  # label_e.sct_feedback.value
        "": ppt_t(category=label_e.cat_optimization.value, basic=False, optional=True),
        "status_period": prm_t(
            hint=h.Annotated[float, number_t(min=0.0)],
            default=2.0,
            ppt=ppt_t(
                short="Time in seconds between two status feedback (0 -> no feedback)",
                basic=False,
            ),
        ),
    },
    "object": {  # label_e.sct_object.value
        "": ppt_t(
            category=label_e.cat_object.value,
            short="Object type and common properties",
            basic=True,
            optional=False,
        ),
        "definition": ctl_t(
            # TODO: Change the hint check in ctl_t __post_init__ from h.Any to also add
            #     some sort of choice protocol.
            # hint=h.Annotated[h.callable, callable_t("class", allow_external=True)],
            controlled_section="mark_ranges",
            ppt=ppt_t(
                short="[Object module:]Object type",
                long="Before the colon: Object module path (absolute or relative to ini file) "
                "or object module name in brick/marked_point/(oneD|twoD|threeD), "
                'with "py" extension chopped off. '
                "E.g. circle for circle.py. "
                "This part, including the colon, is optional. "
                "Since when this part is omitted, a module is searched for in several folders, "
                "these modules should have different names to avoid masking modules in subsequently visited folders. "
                'After the colon: An object type defined in the object module with "_t" suffix chopped off. '
                "E.g. circle for class circle_t",
                basic=True,
            ),
        ),
        "center": prm_t(
            hint=int
            | float
            | h.Annotated[tuple, collection_t(items_types=int | float)]
            | h.Annotated[
                pl_path_t, path_t(kind=path_kind_e.any, purpose=path_purpose_e.input)
            ]
            | None,
            default=None,
            ppt=ppt_t(
                short="- None = No constraint on position: it can be anywhere inside image domain"
                "- Precision(s): a precision common to all dimensions, or a list/tuple of per-axis precisions"
                "- Path to an image representing a map (image containing 2 distinct values, "
                "the locii of the max being valid points) or "
                "a PDF (image of positive values summing to 1 used to draw points).",
                basic=False,
            ),
        ),
        "only_un_cropped": prm_t(
            hint=bool,
            default=True,
            ppt=ppt_t(
                short="Only retain objects that do not cross domain border", basic=False
            ),
        ),
    },
    "mark_ranges": {  # label_e.sct_mark_ranges.value
        "": ppt_t(
            category=label_e.cat_object.value,
            short="Specific to the selected object type",
            basic=True,
            optional=False,
        )
    },
    "quality": {  # label_e.sct_quality.value
        "": ppt_t(
            category=label_e.cat_object.value,
            short="Common to any object quality",
            basic=True,
            optional=False,
        ),
        "definition": ctl_t(
            controlled_section="quality_prm",
            ppt=ppt_t(
                short="[Quality module:]Quality class",
                long="Before the colon: Quality module path (absolute or relative to ini file) "
                "or object module name in brick/quality/(oneD|twoD|threeD), "
                'with "py" extension chopped off. '
                "E.g. contrast for contrast.py. "
                "This part, including the colon, is optional. "
                "Since when this part is omitted, a module is searched for in several folders, "
                "these modules should have different names to avoid masking modules in subsequently visited folders. "
                'After the colon: A quality class defined in the quality module with "_t" suffix chopped off. '
                "E.g. bright_on_dark_contrast for class contrast_bright_on_dark_t",
                basic=True,
            ),
        ),
        "min_value": prm_t(hint=int | float, ppt=ppt_t(basic=True)),
    },
    "quality_prm": {  # label_e.sct_quality_prm.value
        "": ppt_t(
            category=label_e.cat_object.value,
            short="Specific to the selected object quality",
            basic=False,
            optional=True,
        )
    },
    # section_t(
    #     name=label_e.sct_incentives.value,
    #     category=label_e.cat_object.value,
    #     short="Incentives on Generated Objects",
    #     basic=False,
    #     optional=True,
    # ),
    "constraints": {  # label_e.sct_constraints.value
        "": ppt_t(
            category=label_e.cat_object.value,
            short="Constraints on Generated Objects",
            basic=False,
            optional=True,
        ),
        "max_overlap": prm_t(
            hint=h.Annotated[float, number_t(min=0.0, max=100.0)],
            default=20.0,
            ppt=ppt_t(short="As a percentage (0.0 => no overlap allowed)", basic=False),
        ),
    },
    "signal": {  # label_e.sct_signal.value
        "": ppt_t(
            category=label_e.cat_input.value,
            short="Common to any signal loading function",
            basic=True,
            optional=False,
        ),
        "path": prm_t(
            hint=h.Annotated[
                pl_path_t, path_t(kind=path_kind_e.any, purpose=path_purpose_e.input)
            ],
            ppt=ppt_t(
                short="Image path or image folder path",
                long="Path to raw signal (either a single file or a folder (absolute or relative to ini file) "
                "that will be scanned w/o recursion)",
                basic=True,
            ),
        ),
        "loading_function": prm_t(
            hint=str,
            default="ImageChannelBySkimage",
            ppt=ppt_t(
                long="Raw signal loading module in given folder (absolute or relative to ini file) or "
                "in helper with py extension chopped off. E.g. signal_loading for signal_loading.py. "
                "Optional = signal_loading module in helper. "
                "It must accept a parameter named signal_path",
                basic=False,
            ),
        ),
    },
    "signal_loading_prm": {  # label_e.sct_signal_loading_prm.value
        "": ppt_t(
            category=label_e.cat_input.value,
            short="Specific to the selected signal loading function",
            basic=False,
            optional=True,
        )
    },
    "signal_processing_prm": {  # label_e.sct_signal_processing_prm.value
        "": ppt_t(
            category=label_e.cat_input.value,
            short="Specific to the selected object quality: parameters for the function converting "
            "loaded raw signal into signal used by object quality",
            basic=False,
            optional=True,
        )
    },
    "output": {  # label_e.sct_output.value
        "": ppt_t(category=label_e.cat_output.value, basic=True, optional=True),
        "console": prm_t(
            hint=bool,
            default=True,
            ppt=ppt_t(short="Whether to print the result in the console", basic=True),
        ),
        "feedback": prm_t(
            hint=h.Annotated[str, choices_t(("true", "fake"))],
            default="true",
            ppt=ppt_t(
                short="Whether to use the true or fake feedback server", basic=True
            ),
        ),
        "memory_usage": prm_t(
            hint=bool,
            default=False,
            ppt=ppt_t(short="Whether to monitor memory usage", basic=False),
        ),
        "base_folder": prm_t(
            hint=h.Annotated[
                pl_path_t,
                path_t(kind=path_kind_e.folder, purpose=path_purpose_e.output),
            ]
            | None,
            default=None,
            ppt=ppt_t(short="Base output folder", basic=True),
        ),
        "what": prm_t(
            hint=str | None,
            default=None,
            ppt=ppt_t(
                short="Which results should be output. Comma-separated list of keywords among: "
                "csv (detected marked points in a CSV file),"
                "json (detected marked points in a file with a format that can be used to recreate them),"
                "contour (contours of the detected marked points in an image file),"
                "region (regions of the detected marked points in an image file),"
                "region_numpy (regions of the detected marked points in a Numpy file (.npz)).",
                basic=True,
            ),
        ),
        "output_function": prm_t(
            hint=str | None,
            default=None,
            ppt=ppt_t(
                long="Result output module in given folder (absolute or relative to ini file) or "
                'in helper with "py" extension chopped off. '
                "E.g. result_output for result_output.py. Optional  =  result_output module in helper. "
                "Result output function: Output2DObjects if processing a single "
                "datum, or None if processing a signal folder",
                basic=False,
            ),
        ),
        "marks_separator": prm_t(
            hint=str,
            default=",",
            ppt=ppt_t(short="Marks separator for the CSV format", basic=True),
        ),
    },
    "output_prm": {  # label_e.sct_output_prm.value
        "": ppt_t(
            category=label_e.cat_output.value,
            short="Specific to the select result output function",
            basic=False,
            optional=True,
        )
    },
}
