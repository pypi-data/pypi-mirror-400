"""Normalization utilities for motion data."""

import numpy as np


def z_score_normalize(data):
    """Z-score normalization (zero mean, unit variance).
    
    Parameters
    ----------
    data : np.ndarray
        Input data array
    
    Returns
    -------
    np.ndarray
        Normalized data with zero mean and unit variance
    """
    mean_vals = np.mean(data, axis=0)
    std_vals = np.std(data, axis=0)
    
    # Avoid division by zero
    std_vals = np.where(std_vals == 0, 1.0, std_vals)
    
    normalized_data = (data - mean_vals) / std_vals
    return normalized_data


def min_max_normalize(data):
    """Min-max normalization to [0, 1] range.
    
    Parameters
    ----------
    data : np.ndarray
        Input data array
    
    Returns
    -------
    np.ndarray
        Normalized data in [0, 1] range
    """
    min_vals = np.min(data, axis=0)
    max_vals = np.max(data, axis=0)
    
    # Avoid division by zero
    range_vals = max_vals - min_vals
    range_vals = np.where(range_vals == 0, 1.0, range_vals)
    
    normalized_data = (data - min_vals) / range_vals
    return normalized_data


def min_max_normalize_1D(data):
    """Min-max normalization for 1D array.
    
    Parameters
    ----------
    data : np.ndarray
        1D input data array
    
    Returns
    -------
    np.ndarray
        Normalized data in [0, 1] range
    """
    data = np.asarray(data).flatten()
    min_val = np.min(data)
    max_val = np.max(data)
    
    if max_val == min_val:
        return np.zeros_like(data)
    
    return (data - min_val) / (max_val - min_val)

