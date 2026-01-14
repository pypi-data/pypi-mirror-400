"""Anchor detection from motion signals."""

import numpy as np

from ..preprocessing import (
    smooth_velocity,
    detect_velocity_peaks,
    filter_dir_anchors_by_threshold,
    binary_to_peak,
)
from ..preprocessing.normalization import min_max_normalize_1D as norm_1d
from ..preprocessing.signal_processing import moving_average
from ..config.defaults import (
    DEFAULT_T_FILTER,
    DEFAULT_SMOOTH_WINDOW_LENGTH,
    DEFAULT_HEIGHT_THRESHOLD,
    DEFAULT_PEAK_DURATION,
)


def detect_segment_anchor(
    sensor_data,
    t_filter=None,
    smooth_wlen=None,
    height_thres=None,
    fps=60,
    vel_mode="off",
    mode="uni",
):
    """Detect anchors from sensor/segment data.
    
    Parameters
    ----------
    sensor_data : np.ndarray
        Sensor data array of shape (n_frames, 1)
    t_filter : float, optional
        Temporal filter threshold in seconds (default: 0.25)
    smooth_wlen : int, optional
        Smoothing window length (default: 10)
    height_thres : float, optional
        Peak height threshold (default: 0.2)
    fps : float, optional
        Sampling rate in Hz (default: 60)
    vel_mode : str, optional
        Velocity mode: "on" to use velocity, "off" for position (default: "off")
    mode : str, optional
        Direction mode: "uni" for uni-directional, "bi" for bi-directional (default: "uni")
    
    Returns
    -------
    dict
        Dictionary containing anchor detection results with keys:
        - 'raw_signal': Original input signal
        - 'sensor_abs': Absolute smoothed signal
        - 'sensor_abs_pos_norm': Normalized absolute signal
        - 'sensor_dir_change_anchors': Direction change detection (binary array)
        - 'sensor_anchors': Filtered anchors (binary array)
        - 'sensor_anchors_50ms': Anchors with 50ms peak windows (continuous array)
    """
    if t_filter is None:
        t_filter = DEFAULT_T_FILTER
    if smooth_wlen is None:
        smooth_wlen = DEFAULT_SMOOTH_WINDOW_LENGTH
    if height_thres is None:
        height_thres = DEFAULT_HEIGHT_THRESHOLD
    
    sensor_dir_change = None
    sensor_anchors = None
    
    if mode == 'uni':  # Extract uni-directional change anchors
        sensor_abs_pos = smooth_velocity(
            sensor_data, abs="no", window_length=smooth_wlen, polyorder=0
        )
        if vel_mode == "on":
            sensor_abs_pos = np.diff(sensor_abs_pos, axis=0)
        
        sensor_abs_pos[sensor_abs_pos < 0] = 0
        
        sensor_abs_pos_norm = norm_1d(sensor_abs_pos.flatten())
        sensor_dir_change = detect_velocity_peaks(
            sensor_abs_pos_norm.reshape(-1, 1),
            height=height_thres,
            distance=15
        )
        
        sensor_anchors = filter_dir_anchors_by_threshold(
            sensor_dir_change, threshold_s=t_filter, fps=fps
        )
        sensor_anchors_50ms = binary_to_peak(
            sensor_anchors, peak_duration=DEFAULT_PEAK_DURATION, sampling_rate=fps
        )
    
    elif mode == 'bi':  # Extract bi-directional change anchors
        sensor_abs_pos = smooth_velocity(
            sensor_data, abs="yes", window_length=smooth_wlen, polyorder=0
        )
        if vel_mode == "on":
            sensor_abs_pos = np.diff(sensor_abs_pos, axis=0)
        
        sensor_abs_pos_norm = norm_1d(sensor_abs_pos.flatten())
        sensor_dir_change = detect_velocity_peaks(
            sensor_abs_pos_norm.reshape(-1, 1),
            height=height_thres,
            distance=15
        )
        
        sensor_anchors = filter_dir_anchors_by_threshold(
            sensor_dir_change, threshold_s=t_filter, fps=fps
        )
        sensor_anchors_50ms = binary_to_peak(
            sensor_anchors, peak_duration=DEFAULT_PEAK_DURATION, sampling_rate=fps
        )
    
    return {
        "raw_signal": sensor_data,
        "sensor_abs": sensor_abs_pos,
        "sensor_abs_pos_norm": sensor_abs_pos_norm,
        "sensor_dir_change_anchors": sensor_dir_change,
        "sensor_anchors": sensor_anchors,
        "sensor_anchors_50ms": sensor_anchors_50ms,
    }


def detect_resultant_anchor(
    resultant_data,
    t_filter=None,
    smooth_wlen=None,
    height_thres=None,
    mov_avg_winsz=10,
    fps=60,
    vel_mode="off",
):
    """Detect anchors from resultant signal (magnitude of x and y).
    
    Parameters
    ----------
    resultant_data : np.ndarray
        Resultant signal array of shape (n_frames, 1)
    t_filter : float, optional
        Temporal filter threshold in seconds (default: 0.20 from config)
    smooth_wlen : int, optional
        Smoothing window length (default: 10)
    height_thres : float, optional
        Peak height threshold (default: 0.2)
    mov_avg_winsz : int, optional
        Moving average window size (default: 10)
    fps : float, optional
        Sampling rate in Hz (default: 60)
    vel_mode : str, optional
        Velocity mode: "on" to use velocity, "off" for position (default: "off")
    
    Returns
    -------
    dict
        Dictionary containing anchor detection results with keys:
        - 'resultant_signal': Original input signal
        - 'resultant_smooth': Smoothed signal
        - 'resultant_filtered': Moving-averaged signal
        - 'resultant_dir_change': Direction change detection (binary array)
        - 'resultant_anchors': Filtered anchors (binary array)
        - 'resultant_anchors_50ms': Anchors with 50ms peak windows (continuous array)
    """
    if t_filter is None:
        t_filter = 0.20  # Slightly different default for resultant
    if smooth_wlen is None:
        smooth_wlen = DEFAULT_SMOOTH_WINDOW_LENGTH
    if height_thres is None:
        height_thres = DEFAULT_HEIGHT_THRESHOLD
    
    # For resultant of x and y
    resultant_smooth = smooth_velocity(
        resultant_data, abs="no", window_length=smooth_wlen, polyorder=0
    )
    if vel_mode == "on":
        resultant_smooth = np.diff(resultant_smooth, axis=0)
    
    resultant_filtered = moving_average(resultant_smooth.flatten(), mov_avg_winsz)
    
    # Pad to original length (moving_average uses 'valid' mode)
    pad_length = len(resultant_smooth) - len(resultant_filtered)
    if pad_length > 0:
        resultant_filtered = np.pad(
            resultant_filtered,
            (0, pad_length),
            mode='constant',
            constant_values=0
        )
    
    resultant_dir_change = detect_velocity_peaks(
        resultant_filtered.reshape(-1, 1),
        height=height_thres,
        distance=15
    )
    resultant_anchors = filter_dir_anchors_by_threshold(
        resultant_dir_change, threshold_s=t_filter, fps=fps
    )
    resultant_anchors_50ms = binary_to_peak(
        resultant_anchors, peak_duration=DEFAULT_PEAK_DURATION, sampling_rate=fps
    )
    
    return {
        "resultant_signal": resultant_data,
        "resultant_smooth": resultant_smooth,
        "resultant_filtered": resultant_filtered,
        "resultant_dir_change": resultant_dir_change,
        "resultant_anchors": resultant_anchors,
        "resultant_anchors_50ms": resultant_anchors_50ms,
    }


class AnchorExtractor:
    """High-level anchor extraction interface."""
    
    def __init__(self, fps=60, config=None):
        """Initialize AnchorExtractor.
        
        Parameters
        ----------
        fps : float, optional
            Sampling rate in Hz (default: 60)
        config : dict, optional
            Configuration dictionary with parameter overrides
        """
        self.fps = fps
        self.config = config or {}
    
    def extract_segment_anchor(
        self, sensor_data, mode="uni", metric="anchor_zero", **kwargs
    ):
        """Extract segment anchors.
        
        Parameters
        ----------
        sensor_data : np.ndarray
            Input signal array
        mode : str
            'uni' or 'bi'
        metric : str
            'anchor_zero' or 'anchor_peak'
        **kwargs
            Additional parameters passed to detect_segment_anchor
        
        Returns
        -------
        dict
            Anchor detection results
        """
        vel_mode = "on" if metric == "anchor_peak" else "off"
        return detect_segment_anchor(
            sensor_data,
            fps=self.fps,
            mode=mode,
            vel_mode=vel_mode,
            **kwargs
        )

