"""Preprocessing module for signal processing, normalization, and filtering."""

from .signal_processing import (
    smooth_velocity,
    detrend_signal,
    detrend_signal_array,
    moving_average,
)
from .normalization import (
    z_score_normalize,
    min_max_normalize,
    min_max_normalize_1D,
)
from .filtering import (
    detect_velocity_peaks,
    filter_dir_anchors_by_threshold,
    binary_to_peak,
)

__all__ = [
    "smooth_velocity",
    "detrend_signal",
    "detrend_signal_array",
    "moving_average",
    "z_score_normalize",
    "min_max_normalize",
    "min_max_normalize_1D",
    "detect_velocity_peaks",
    "filter_dir_anchors_by_threshold",
    "binary_to_peak",
]

