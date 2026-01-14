"""Center of Mass computation from keypoint data."""

import numpy as np

from ..config.body_model import COM_PART_INDICES


def compute_com_hips(joints_2d):
    """Compute center of mass for hips.
    
    Parameters
    ----------
    joints_2d : np.ndarray
        Array of shape (num_frames, num_joints, 2)
    
    Returns
    -------
    np.ndarray
        Array of shape (num_frames, 2)
    """
    LHip, RHip = COM_PART_INDICES["hips"]
    return (joints_2d[:, LHip, :] + joints_2d[:, RHip, :]) / 2.0


def compute_com_shoulders(joints_2d):
    """Compute center of mass for shoulders.
    
    Parameters
    ----------
    joints_2d : np.ndarray
        Array of shape (num_frames, num_joints, 2)
    
    Returns
    -------
    np.ndarray
        Array of shape (num_frames, 2)
    """
    LShoulder, RShoulder = COM_PART_INDICES["shoulders"]
    return (joints_2d[:, LShoulder, :] + joints_2d[:, RShoulder, :]) / 2.0


def compute_com_torso(joints_2d):
    """Compute center of mass for torso (mean of hips and shoulders).
    
    Parameters
    ----------
    joints_2d : np.ndarray
        Array of shape (num_frames, num_joints, 2)
    
    Returns
    -------
    np.ndarray
        Array of shape (num_frames, 2)
    """
    com_hips = compute_com_hips(joints_2d)
    com_shoulders = compute_com_shoulders(joints_2d)
    return (com_hips + com_shoulders) / 2.0


def compute_com_variants(joints_2d):
    """Compute all CoM variants from COCO-format 2D keypoints.
    
    Parameters
    ----------
    joints_2d : np.ndarray
        Array of shape (num_frames, num_joints, 2) containing COCO-format keypoints.
        Expected joint indices: 11=left_hip, 12=right_hip, 5=left_shoulder, 6=right_shoulder.
    
    Returns
    -------
    tuple of np.ndarray
        (com_hips, com_shoulders, com_torso) each of shape (num_frames, 2)
    """
    com_hips = compute_com_hips(joints_2d)
    com_shoulders = compute_com_shoulders(joints_2d)
    com_torso = compute_com_torso(joints_2d)
    return com_hips, com_shoulders, com_torso

