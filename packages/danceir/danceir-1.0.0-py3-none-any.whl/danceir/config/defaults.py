"""Default configurations for DanceIR toolbox.

This module contains default parameter values and path configurations.
All paths are relative and should be configured per project.
"""

from pathlib import Path

# Path defaults (can be overridden via configuration)
ANCHOR_BASE_DIR = "./extracted_anchors"
COM_BASE_DIR = "./extracted_anchors/com"
COM_COMPUTED_DIR = "./computed_com"

# Processing defaults
DEFAULT_FPS = 60
DEFAULT_HEIGHT_THRESHOLD = 0.2
DEFAULT_SMOOTH_WINDOW_LENGTH = 10
DEFAULT_T_FILTER = 0.25
DEFAULT_PEAK_DURATION = 0.1  # seconds

# Signal processing defaults
DEFAULT_DETREND_CUTOFF = 0.8  # Hz for high-pass filter
DEFAULT_DETREND_CUTOFF_MARKER = 1.0  # Hz for marker detrending
DEFAULT_DETREND_CUTOFF_COM = 0.5  # Hz for CoM detrending

# Anchor detection defaults
DEFAULT_PEAK_HEIGHT = 0.2
DEFAULT_PEAK_DISTANCE = 15  # frames
DEFAULT_MOVING_AVG_WINDOW = 10

# Marker IDs (for backward compatibility)
from .body_model import MARKER_GROUPS

MARKER_IDS = MARKER_GROUPS.copy()

