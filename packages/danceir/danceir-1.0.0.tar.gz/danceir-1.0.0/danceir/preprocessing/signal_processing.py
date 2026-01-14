"""Core signal processing functions for motion data."""

import numpy as np
from scipy.signal import butter, filtfilt, savgol_filter

from ..config.defaults import DEFAULT_DETREND_CUTOFF


def smooth_velocity(velocity_data, abs='yes', window_length=60, polyorder=0):
    """Smooth velocity data using Savitzky-Golay filter.
    
    Parameters
    ----------
    velocity_data : np.ndarray
        Velocity data of shape (n_frames, n_axes)
    abs : str, optional
        If 'yes', take absolute value after smoothing (default: 'yes')
    window_length : int, optional
        Window length for Savitzky-Golay filter (default: 60)
    polyorder : int, optional
        Polynomial order for filter (default: 0)
    
    Returns
    -------
    np.ndarray
        Smoothed velocity array of shape (n_frames, n_axes)
    """
    smoothed_list = []
    for i in range(velocity_data.shape[1]):
        smoothed = savgol_filter(velocity_data[:, i], window_length, polyorder)
        if abs == 'yes':
            smoothed = np.abs(smoothed)
        smoothed_list.append(smoothed)
    
    return np.column_stack(smoothed_list)


def detrend_signal(signal, cutoff=None, fs=60):
    """Remove low-frequency trend from signal using high-pass filter.
    
    Parameters
    ----------
    signal : np.ndarray
        1D signal array
    cutoff : float, optional
        High-pass filter cutoff frequency in Hz (default: 0.5)
    fs : float, optional
        Sampling rate in Hz (default: 60)
    
    Returns
    -------
    np.ndarray
        Detrended signal
    """
    if cutoff is None:
        cutoff = DEFAULT_DETREND_CUTOFF
    
    b, a = butter(2, cutoff / (fs / 2), btype='highpass')
    detrended_signal = filtfilt(b, a, signal)
    return detrended_signal


def detrend_signal_array(signal, cutoff=0.5, fs=60):
    """Remove low-frequency trend from multi-dimensional signal.
    
    Parameters
    ----------
    signal : np.ndarray
        Signal array of shape (n_frames, n_axes)
    cutoff : float, optional
        High-pass filter cutoff frequency in Hz (default: 0.5)
    fs : float, optional
        Sampling rate in Hz (default: 60)
    
    Returns
    -------
    np.ndarray
        Detrended signal array of shape (n_frames, n_axes)
    """
    if cutoff is None:
        cutoff = DEFAULT_DETREND_CUTOFF
    
    b, a = butter(2, cutoff / (fs / 2), btype='highpass')
    
    detrended_list = []
    for i in range(signal.shape[1]):
        detrended = filtfilt(b, a, signal[:, i])
        detrended_list.append(detrended)
    
    return np.column_stack(detrended_list)


def moving_average(signal, window_size):
    """Compute moving average of signal.
    
    Parameters
    ----------
    signal : np.ndarray
        1D signal array
    window_size : int
        Size of moving average window
    
    Returns
    -------
    np.ndarray
        Moving averaged signal (valid convolution, shorter than input)
    """
    return np.convolve(signal, np.ones(window_size) / window_size, mode='valid')

