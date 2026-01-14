"""Energy-based anchor detection using RMS energy features."""

import numpy as np
import librosa

from ..preprocessing import (
    smooth_velocity,
    detect_velocity_peaks,
    filter_dir_anchors_by_threshold,
    binary_to_peak,
)
from ..preprocessing.normalization import min_max_normalize_1D
from ..preprocessing.signal_processing import moving_average
from ..config.defaults import (
    DEFAULT_T_FILTER,
    DEFAULT_SMOOTH_WINDOW_LENGTH,
    DEFAULT_HEIGHT_THRESHOLD,
    DEFAULT_PEAK_DURATION,
)


def compute_energy(signal):
    """Compute instantaneous energy: v[n]^2."""
    return signal ** 2


def detect_energy_anchor(
    sensor_data,
    t_filter=None,
    smooth_wlen=None,
    height_thres=0.2,
    fps=60,
    mode="uni",
):
    """Detect anchors using energy-based method (RMS energy).
    
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
    mode : str, optional
        Direction mode: "uni" or "bi" (default: "uni")
    
    Returns
    -------
    dict
        Dictionary containing anchor detection results with keys:
        - 'raw_signal': Original input signal
        - 'sensor_abs': Absolute smoothed signal
        - 'sensor_abs_pos_norm': Normalized energy change signal
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
    
    hop_length = int(fps * 0.1)
    frame_length = int(fps * 0.5)
    
    if mode == 'uni':
        sensor_abs_pos = smooth_velocity(
            sensor_data, abs="no", window_length=smooth_wlen, polyorder=0
        )
        sensor_abs_pos[sensor_abs_pos < 0] = 0
        
        # Compute RMS energy
        rmse = compute_energy(sensor_abs_pos.flatten())
        
        # Compute energy change (first difference with smoothing)
        rmse_smooth = np.convolve(rmse, np.ones(3) / 3, mode='same')
        rmse_diff = np.diff(rmse_smooth, prepend=rmse_smooth[0])
        energy_change = np.maximum(0, rmse_diff)
        
        sensor_abs_pos_norm = min_max_normalize_1D(energy_change.flatten())
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
    
    elif mode == 'bi':
        sensor_abs_pos = smooth_velocity(
            sensor_data, abs="yes", window_length=smooth_wlen, polyorder=0
        )
        
        # Compute RMS energy
        rmse = compute_energy(sensor_abs_pos.flatten())
        
        # Compute energy change
        rmse_smooth = np.convolve(rmse, np.ones(3) / 3, mode='same')
        rmse_diff = np.diff(rmse_smooth, prepend=rmse_smooth[0])
        energy_change = np.maximum(0, rmse_diff)
        
        sensor_abs_pos_norm = min_max_normalize_1D(energy_change.flatten())
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


def detect_energy_resultant_anchor(
    resultant_data,
    t_filter=0.20,
    smooth_wlen=None,
    height_thres=None,
    mov_avg_winsz=10,
    fps=60,
):
    """Detect anchors from resultant signal using energy-based method.
    
    Parameters
    ----------
    resultant_data : np.ndarray
        Resultant signal array of shape (n_frames, 1)
    t_filter : float, optional
        Temporal filter threshold in seconds (default: 0.20)
    smooth_wlen : int, optional
        Smoothing window length (default: 10)
    height_thres : float, optional
        Peak height threshold (default: 0.2)
    mov_avg_winsz : int, optional
        Moving average window size (default: 10)
    fps : float, optional
        Sampling rate in Hz (default: 60)
    
    Returns
    -------
    dict
        Dictionary containing anchor detection results
    """
    if smooth_wlen is None:
        smooth_wlen = DEFAULT_SMOOTH_WINDOW_LENGTH
    if height_thres is None:
        height_thres = DEFAULT_HEIGHT_THRESHOLD
    
    hop_length = int(fps * 0.1)
    frame_length = int(fps * 0.5) 
    
    resultant_smooth = smooth_velocity(
        resultant_data, abs="no", window_length=smooth_wlen, polyorder=0
    )
    
    # Compute RMS energy
    rmse = compute_energy(resultant_smooth.flatten())
    
    # Compute energy change
    rmse_smooth = np.convolve(rmse, np.ones(3) / 3, mode='same')
    rmse_diff = np.diff(rmse_smooth, prepend=rmse_smooth[0])
    energy_change = np.maximum(0, rmse_diff)
    
    resultant_filtered = moving_average(energy_change.flatten(), mov_avg_winsz)
    
    # Pad to original length
    pad_length = len(energy_change) - len(resultant_filtered)
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


class EnergyExtractor:
    """High-level energy-based anchor extraction interface."""
    
    def __init__(self, fps=60, config=None):
        """Initialize EnergyExtractor.
        
        Parameters
        ----------
        fps : float, optional
            Sampling rate in Hz (default: 60)
        config : dict, optional
            Configuration dictionary with parameter overrides
        """
        self.fps = fps
        self.config = config or {}
    
    def extract_energy_anchor(self, signal, mode="uni", **kwargs):
        """Extract energy-based anchors.
        
        Parameters
        ----------
        signal : np.ndarray
            Input signal array
        mode : str
            'uni' or 'bi'
        **kwargs
            Additional parameters passed to detect_energy_anchor
        
        Returns
        -------
        dict
            Anchor detection results
        """
        return detect_energy_anchor(signal, fps=self.fps, mode=mode, **kwargs)

