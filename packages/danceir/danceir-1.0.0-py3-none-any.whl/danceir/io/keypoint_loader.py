"""Keypoint data loading from various formats.

This module provides generic keypoint loading functions that work with
COCO-format 2D keypoint data stored in pickle files.
"""

import pickle
import numpy as np
from pathlib import Path

from ..utils.exceptions import InvalidKeypointDataError


class KeypointLoader:
    """Load keypoint data from various file formats.
    
    Supports COCO-format 2D keypoints stored in pickle files.
    Expected format: keypoints2d array of shape (num_persons, num_frames, num_joints, 3)
    where the last dimension is [x, y, confidence].
    """
    
    @staticmethod
    def load_keypoints_pickle(filepath):
        """Load COCO-format keypoint data from pickle file.
        
        Parameters
        ----------
        filepath : str or Path
            Path to pickle file containing keypoint data
        
        Returns
        -------
        dict
            Dictionary containing keypoint data with 'keypoints2d' key.
            Expected format: keypoints2d array of shape (num_persons, num_frames, num_joints, 3)
            where the last dimension is [x, y, confidence] following COCO format.
        
        Raises
        ------
        InvalidKeypointDataError
            If file cannot be loaded or data is invalid
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise InvalidKeypointDataError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                motion_data = pickle.load(f)
            return motion_data
        except Exception as e:
            raise InvalidKeypointDataError(f"Failed to load keypoint data: {e}")
    
    @staticmethod
    def extract_marker_position(keypoints_data, marker_id, person_idx=0):
        """Extract x and y positions for a specific marker/joint.
        
        Parameters
        ----------
        keypoints_data : dict
            Keypoint data dictionary (from load_keypoints_pickle)
        marker_id : int
            Joint/marker ID (COCO format: 0=nose, 1=left_eye, ..., 15=left_ankle, 16=right_ankle)
        person_idx : int, optional
            Person index (default: 0)
        
        Returns
        -------
        tuple of np.ndarray
            (x_positions, y_positions) arrays of shape (num_frames,)
        
        Raises
        ------
        InvalidKeypointDataError
            If marker data is invalid or missing
        """
        if 'keypoints2d' not in keypoints_data:
            raise InvalidKeypointDataError("Missing 'keypoints2d' in data")
        
        keypoints2d = keypoints_data['keypoints2d']
        
        try:
            marker_x = keypoints2d[person_idx, :, marker_id, 0]
            marker_y = keypoints2d[person_idx, :, marker_id, 1]
        except (IndexError, KeyError) as e:
            raise InvalidKeypointDataError(f"Invalid marker_id or person_idx: {e}")
        
        # Validate data
        if np.all((marker_x == 0) & (marker_y == 0)):
            raise InvalidKeypointDataError(f"Marker {marker_id} has all zero values")
        
        if np.any(np.isnan(marker_x) | np.isnan(marker_y)):
            raise InvalidKeypointDataError(f"Marker {marker_id} contains NaN values")
        
        return marker_x, marker_y
    
    @staticmethod
    def extract_all_keypoints_2d(keypoints_data, person_idx=0):
        """Extract all 2D keypoints for a person in COCO format.
        
        Parameters
        ----------
        keypoints_data : dict
            Keypoint data dictionary (from load_keypoints_pickle)
        person_idx : int, optional
            Person index (default: 0)
        
        Returns
        -------
        np.ndarray
            Array of shape (num_frames, num_joints, 2) containing [x, y] coordinates
            following COCO keypoint format.
        """
        if 'keypoints2d' not in keypoints_data:
            raise InvalidKeypointDataError("Missing 'keypoints2d' in data")
        
        keypoints2d = keypoints_data['keypoints2d']
        return keypoints2d[person_idx, :, :, :2]

