"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from enum import Enum as enum_t
from enum import unique as ensure_unique_values


@ensure_unique_values
class label_e(enum_t):
    """
    Word case is used to guarantee value uniqueness.
    """

    cat_input = "INPUT"
    cat_object = "OBJECT"
    cat_optimization = "OPTIMIZATION"
    cat_output = "OUTPUT"
    #
    sct_mpp = "mpp"
    sct_refinement = "refinement"
    sct_feedback = "feedback"
    sct_object = "object"
    sct_mark_ranges = "mark_ranges"
    sct_quality = "quality"
    sct_quality_prm = "quality_prm"
    sct_constraints = "constraints"
    sct_signal = "signal"
    sct_signal_loading_prm = "signal_loading_prm"
    sct_signal_processing_prm = "signal_processing_prm"
    sct_output = "output"
    sct_output_prm = "output_prm"
