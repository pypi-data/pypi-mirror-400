"""Filtering and anchor detection utilities."""

import numpy as np
from scipy.signal import find_peaks

from ..config.defaults import (
    DEFAULT_PEAK_HEIGHT,
    DEFAULT_PEAK_DISTANCE,
    DEFAULT_PEAK_DURATION,
)


def detect_velocity_peaks(velocity_array, height=None, distance=None):
    """Detect peaks in velocity array (formerly velocity_based_novelty).
    
    Parameters
    ----------
    velocity_array : np.ndarray
        Velocity array of shape (n_frames, n_axes)
    height : float, optional
        Minimum height of peaks (default: 0.2)
    distance : int, optional
        Minimum distance between peaks in frames (default: 15)
    
    Returns
    -------
    np.ndarray
        Binary array of shape (n_frames, n_axes) where 1 indicates peak locations
    """
    if height is None:
        height = DEFAULT_PEAK_HEIGHT
    if distance is None:
        distance = DEFAULT_PEAK_DISTANCE
    
    peak_arrays = []
    for i in range(velocity_array.shape[1]):
        peaks, _ = find_peaks(velocity_array[:, i], height=height, distance=distance)
        binary_data = np.zeros(len(velocity_array[:, i]))
        binary_data[peaks] = 1
        peak_arrays.append(binary_data)
    
    return np.column_stack(peak_arrays)


def filter_dir_anchors_by_threshold(dir_change_array, threshold_s=0.4, fps=60):
    """Filter direction change anchors by temporal threshold.
    
    Removes anchors that fall within threshold window after current anchor.
    This function was previously named filter_dir_onsets_by_threshold.
    
    Parameters
    ----------
    dir_change_array : np.ndarray
        Binary array of shape (n_frames, n_axes) where >0 indicates anchor locations
    threshold_s : float, optional
        Time threshold in seconds (default: 0.4)   # Dance beat ioi range 1sec - 0.43 sec (60-140 bpm)
    fps : float, optional
        Sampling rate in Hz (default: 60)
    
    Returns
    -------
    np.ndarray
        Filtered binary array of same shape as input
    """
    window_frames = int(threshold_s * fps)
    filtered_cols = []
    
    for col in range(dir_change_array.shape[1]):
        dir_change_anchors = dir_change_array[:, col]
        anchor_frames = np.where(dir_change_anchors > 0)[0]
        
        filtered_anchors = np.zeros(len(dir_change_anchors))
        filtered_frame_indices = []
        
        i = 0
        while i < len(anchor_frames):
            current_frame = anchor_frames[i]
            end_frame = current_frame + window_frames
            
            # Add current anchor
            filtered_frame_indices.append(current_frame)
            
            # Skip all subsequent anchors within the window
            j = i + 1
            while j < len(anchor_frames) and anchor_frames[j] <= end_frame:
                j += 1
            
            i = j
        
        filtered_anchors[filtered_frame_indices] = 1
        filtered_cols.append(filtered_anchors)
    
    return np.column_stack(filtered_cols)


def binary_to_peak(binary_array, sampling_rate=60, peak_duration=None):
    """Convert binary array to continuous signal with Gaussian peaks.
    
    Represent binary anchors with peaks of specified duration.
    
    Parameters
    ----------
    binary_array : np.ndarray
        Binary input array (1s and 0s)
    sampling_rate : int, optional
        Sampling rate in Hz (default: 60)
    peak_duration : float, optional
        Duration of each peak in seconds (default: 0.05)
    
    Returns
    -------
    np.ndarray
        Continuous signal with peaks for each 1 in the binary array
    """
    if peak_duration is None:
        peak_duration = DEFAULT_PEAK_DURATION
    
    n = len(binary_array)
    peak_samples = int(peak_duration * sampling_rate)
    half_peak = peak_samples // 2
    
    # Create Gaussian peak
    t = np.linspace(-half_peak, half_peak, peak_samples)
    peak_shape = np.exp(-0.5 * (t / (half_peak / 2)) ** 2)
    
    # Create continuous signal
    continuous_signal = np.zeros(n + peak_samples)
    for i, value in enumerate(binary_array):
        if value == 1:
            start = i
            end = i + peak_samples
            continuous_signal[start:end] += peak_shape
    
    # Trim to original length
    return continuous_signal[:n].reshape(-1, 1)

