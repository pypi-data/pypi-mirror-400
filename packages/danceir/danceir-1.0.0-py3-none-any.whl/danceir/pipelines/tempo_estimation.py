"""High-level tempo estimation pipeline from keypoint data.

This module provides convenient functions for common workflows, orchestrating
the full pipeline from keypoint loading to tempo estimation.
"""

import numpy as np
from typing import List, Union, Optional, Tuple

from ..features import compute_com_variants, detect_segment_anchor
from ..preprocessing import detrend_signal_array, z_score_normalize, filter_dir_anchors_by_threshold
from ..analysis import estimate_dance_tempo
from ..config import (
    MARKER_DICT,
    DEFAULT_FPS,
    DEFAULT_DETREND_CUTOFF_MARKER,
    DEFAULT_DETREND_CUTOFF_COM,
)


def _resolve_marker_ids(marker_input):
    """Resolve marker input to marker IDs.
    
    Parameters
    ----------
    marker_input : int or tuple
        Marker identifier(s). Can be:
        - int: Single marker ID (0-16)
        - tuple: Multiple marker IDs (e.g., (9, 10))
    
    Returns
    -------
    tuple
        Tuple of marker IDs
    """
    if isinstance(marker_input, int):
        return (marker_input,)
    elif isinstance(marker_input, tuple):
        return marker_input
    else:
        raise ValueError(
            f"marker_input must be int or tuple, got {type(marker_input)}"
        )


def _extract_and_combine_markers(keypoints_2d, marker_ids, axis, fps):
    """Extract and combine marker positions.
    
    Parameters
    ----------
    keypoints_2d : np.ndarray
        Keypoint array of shape (num_frames, num_joints, 2) where last dim is [x, y]
    marker_ids : tuple or int
        Tuple of marker IDs to combine
    axis : str
        'x' or 'y'
    fps : float
        Sampling rate
    
    Returns
    -------
    np.ndarray
        Combined, detrended, and normalized signal
    """
    # Extract markers
    
    if type(marker_ids) == int:
        marker_ids = (marker_ids,)
        
    axis_idx = 0 if axis == 'x' else 1    
    
    signals = []
    for marker_id in marker_ids:
        
        signal = keypoints_2d[:, marker_id, axis_idx]
        signals.append(signal)
    
    # Combine signals
    # combined = signals[0].copy()
    # for signal in signals[1:]:
    #     combined = combined + signal
    
    # Stack signals
    combined = np.column_stack(signals)
    
    # Preprocess
    detrended = detrend_signal_array(
        combined.reshape(-1, 1),
        cutoff=DEFAULT_DETREND_CUTOFF_MARKER,
        fs=fps
    )
    normalized = z_score_normalize(detrended)
    
    return normalized     # normalized.flatten()


def estimate_tempo_from_keypoints(
    keypoints_2d: np.ndarray,
    marker_groups: Optional[List[Union[int, Tuple[int, ...]]]] = None,
    axis: str = 'y',
    use_com: bool = True,
    com_type: str = 'torso',
    com_axis: Optional[str] = None,
    fps: float = 60.0,
    anchor_method: str = 'zero_velocity',
    height_thres: float = 0.1,
    **tempo_kwargs
):
    """Estimate tempo from keypoint data using multi-anchor approach.
    
    This is a high-level pipeline function that orchestrates the complete
    workflow: marker extraction → preprocessing → anchor detection → tempo estimation.
    
    Parameters
    ----------
    keypoints_2d : np.ndarray
        Keypoint array of shape (num_frames, num_joints, 2) where last dim is [x, y]
        Expected to follow COCO format with joint indices:
        0=nose, 1=left_eye, ..., 9=left_wrist, 10=right_wrist, 
        ..., 15=left_ankle, 16=right_ankle
    
    marker_groups : list, optional
        List of marker groups. Each element can be:
        - int: Single marker ID (e.g., 9 for left_wrist)
        - tuple: Multiple marker IDs to combine (e.g., (9, 10) for both hands)
        
        If None, defaults to: [(9, 10), (15, 16)] (both hands, both feet)
    
    axis : {'x', 'y'}, default='y'
        Which axis to use for marker analysis
    
    use_com : bool, default=True
        Whether to include center of mass analysis
    
    com_type : {'hips', 'torso', 'shoulders'}, default='torso'
        Type of center of mass to compute
    
    com_axis : {'x', 'y'} or None, default=None
        Axis for COM analysis. If None, uses same as `axis`
    
    fps : float, default=60.0
        Sampling rate in Hz
    
    anchor_method : {'zero_velocity', 'peak_velocity', 'energy'}, default='zero_velocity'
        Method for anchor extraction
    
    height_thres : float, default=0.1
        Height threshold for anchor detection
    
    **tempo_kwargs
        Additional parameters passed to estimate_dance_tempo():
        - window_length : int (default: 300)
        - hop_size : int (default: 150)
        - tempi_range : np.ndarray (default: np.arange(45, 140, 1))
        - peak_duration : float (default: 0.1)
    
    Returns
    -------
    dict
        Tempo estimation results with same structure as estimate_dance_tempo()
    """
    # Validate inputs
    if axis not in ['x', 'y']:
        raise ValueError(f"axis must be 'x' or 'y', got '{axis}'")
    
    if com_axis is None:
        com_axis = axis
    elif com_axis not in ['x', 'y']:
        raise ValueError(f"com_axis must be 'x' or 'y', got '{com_axis}'")
    
    if com_type not in ['hips', 'torso', 'shoulders']:
        raise ValueError(f"com_type must be 'hips', 'torso', or 'shoulders', got '{com_type}'")
    
    if anchor_method not in ['zero_velocity', 'peak_velocity', 'energy']:
        raise ValueError(
            f"anchor_method must be 'zero_velocity', 'peak_velocity', or 'energy', "
            f"got '{anchor_method}'"
        )
    
    # Validate input shape
    if keypoints_2d.ndim != 3 or keypoints_2d.shape[2] != 2:
        raise ValueError(
            f"keypoints_2d must be of shape (num_frames, num_joints, 2), "
            f"got shape {keypoints_2d.shape}"
        )
    
    # Default marker groups: both hands + both feet
    if marker_groups is None:
        marker_groups = [(9, 10), (15, 16)]  # both_hands, both_feet
    
    # Process marker groups
    processed_signals = {}
    marker_names = []
    
    for i, marker_group in enumerate(marker_groups):
        # Resolve marker IDs (handles int, tuple, etc.)
        marker_ids = _resolve_marker_ids(marker_group)
        
        # Extract and combine
        signal = _extract_and_combine_markers(
            keypoints_2d, marker_ids, axis, fps
        )
        
        # Generate name for this group
        if len(marker_ids) == 1:
            marker_name = MARKER_DICT[marker_ids[0]]
        else:
            marker_names_list = [MARKER_DICT[mid] for mid in marker_ids]
            marker_name = '_'.join(marker_names_list)
        
        processed_signals[f'group_{i}'] = signal
        marker_names.append(marker_name)
    
    # Process Center of Mass if requested
    if use_com:
        com_hips, com_shoulders, com_torso = compute_com_variants(keypoints_2d)
        
        # Select COM type and axis
        com_data = {
            'hips': com_hips,
            'shoulders': com_shoulders,
            'torso': com_torso
        }[com_type]
        
        com_signal = com_data[:, 0] if com_axis == 'x' else com_data[:, 1]
        
        # Preprocess COM
        detrended_com = detrend_signal_array(
            com_signal.reshape(-1, 1),
            cutoff=DEFAULT_DETREND_CUTOFF_COM,
            fs=fps
        )
        normalized_com = z_score_normalize(detrended_com)
        
        processed_signals['com'] = normalized_com    # normalized_com.flatten() 
        marker_names.append(f'com_{com_type}')
    
    # Extract anchors from all processed signals
    anchor_segments = {}
    segment_names = []
    
    vel_mode = "on" if anchor_method == "peak_velocity" else "off"
    use_energy = (anchor_method == "energy")
    
    for key, signal in processed_signals.items():
        # signal_2d = signal.reshape(-1, 1)
        anchors_per_marker = []
        
        for col in range(signal.shape[1]):
            signal_col = signal[:, col:col+1]
        
            if use_energy:
                from ..features import detect_energy_anchor
                anchors = detect_energy_anchor(
                    signal_col,
                    mode="uni",
                    fps=fps,
                    height_thres=height_thres
                )
            else:
                anchors = detect_segment_anchor(
                    signal_col,
                    mode="uni",
                    vel_mode=vel_mode,
                    fps=fps,
                    height_thres=height_thres
                )
            
            anchor_binary = anchors['sensor_anchors'][:, 0]
            anchors_per_marker.append(anchor_binary)
        
        # Merge anchors within the group (OR across markers)
        merged_anchor = np.logical_or.reduce(anchors_per_marker).astype(float)
        merged_anchor_filtered = filter_dir_anchors_by_threshold(merged_anchor.reshape(-1, 1))
            
        anchor_segments[key] = merged_anchor_filtered
        segment_names.append(marker_names[list(processed_signals.keys()).index(key)])
    
    # Prepare multi-segment structure
    segments_list = list(anchor_segments.values())
    multi_segments = {
        'combined_anchors': {
            'segments': segments_list,
            'names': segment_names
        }
    }
    
    # Default tempo estimation parameters
    default_tempo_kwargs = {
        'window_length': int(fps * 5),  # 5 seconds
        'hop_size': int(fps * 2.5),    # 2.5 seconds
        'tempi_range': np.arange(45, 140, 1),
        'signal_length': len(segments_list[0]) if segments_list else None,
        'peak_duration': 0.1
    }
    
    # Merge user-provided kwargs with defaults
    tempo_params = {**default_tempo_kwargs, **tempo_kwargs}
    
    # Run tempo estimation
    result = estimate_dance_tempo(
        multi_segments,
        fps=fps,
        **tempo_params
    )
    
    return result

