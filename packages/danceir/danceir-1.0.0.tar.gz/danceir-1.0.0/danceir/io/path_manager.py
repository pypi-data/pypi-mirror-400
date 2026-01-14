"""Path management and directory structure utilities."""

import os
from pathlib import Path
from typing import Optional

from ..config.defaults import ANCHOR_BASE_DIR, COM_BASE_DIR


class PathManager:
    """Manage paths and directory structures for anchor storage."""
    
    def __init__(self, anchor_base_dir=None, com_base_dir=None):
        """Initialize PathManager with base directories.
        
        Parameters
        ----------
        anchor_base_dir : str or Path, optional
            Base directory for anchor storage (default: from config)
        com_base_dir : str or Path, optional
            Base directory for CoM anchors (default: from config)
        """
        self.anchor_base_dir = Path(anchor_base_dir or ANCHOR_BASE_DIR)
        self.com_base_dir = Path(com_base_dir or COM_BASE_DIR)
    
    def get_anchor_path(self, marker, anchor_type, axis, mode, filename):
        """Get full path for marker anchor file.
        
        Parameters
        ----------
        marker : str
            Marker name (e.g., 'left_wrist')
        anchor_type : str
            Type of anchor ('anchor_zero', 'anchor_peak', 'anchor_energy')
        axis : str
            Axis identifier ('ax0', 'ax1', 'resultant')
        mode : str
            Mode ('uni' or 'bi')
        filename : str
            Base filename
        
        Returns
        -------
        Path
            Full path to anchor file
        """
        return (
            self.anchor_base_dir / marker / anchor_type / axis /
            f"{marker}_{mode}_{filename}"
        )
    
    def get_com_path(self, anchor_type, com_part, axis, mode, filename):
        """Get full path for CoM anchor file.
        
        Parameters
        ----------
        anchor_type : str
            Type of anchor ('anchor_zero', 'anchor_peak', 'anchor_energy')
        com_part : str
            CoM part ('com_hips', 'com_shoulders', 'com_torso')
        axis : str
            Axis identifier ('ax0', 'ax1')
        mode : str
            Mode ('uni' or 'bi')
        filename : str
            Base filename
        
        Returns
        -------
        Path
            Full path to CoM anchor file
        """
        return (
            self.com_base_dir / anchor_type / com_part / axis /
            f"{mode}_{filename}"
        )
    
    def get_all_anchor_paths(self, anchor_type, mode, filename):
        """Get all marker and COM anchor paths for a given anchor type and mode.
        
        Parameters
        ----------
        anchor_type : str
            One of ['anchor_zero', 'anchor_peak', 'anchor_energy']
        mode : str
            Either 'uni' or 'bi'
        filename : str
            The base filename
        
        Returns
        -------
        dict
            Dictionary containing all relevant file paths structured by body part
        """
        markers = ["left_wrist", "right_wrist", "left_ankle", "right_ankle"]
        com_parts = ["com_torso", "com_hips", "com_shoulders"]
        
        data_paths = {
            "markers": {},
            "com": {}
        }
        
        # Body markers (each with ax0 and ax1)
        for m in markers:
            data_paths["markers"][m] = {
                "ax0": self.get_anchor_path(m, anchor_type, "ax0", mode, filename),
                "ax1": self.get_anchor_path(m, anchor_type, "ax1", mode, filename),
                "resultant": self.get_anchor_path(m, anchor_type, "resultant", mode, filename),
            }
        
        # COM parts (each with ax0 and ax1)
        for c in com_parts:
            data_paths["com"][c] = {
                "ax0": self.get_com_path(anchor_type, c, "ax0", mode, filename),
                "ax1": self.get_com_path(anchor_type, c, "ax1", mode, filename),
            }
        
        return data_paths
    
    def create_anchor_directory_structure(self, marker):
        """Create directory structure for a marker's anchors.
        
        Parameters
        ----------
        marker : str
            Marker name (e.g., 'left_wrist')
        """
        marker_dir = self.anchor_base_dir / marker
        
        anchor_types = ["anchor_zero", "anchor_peak", "anchor_energy"]
        for anchor_type in anchor_types:
            base_path = marker_dir / anchor_type
            for axis in ["ax0", "ax1", "resultant"]:
                (base_path / axis).mkdir(parents=True, exist_ok=True)
    
    def create_com_directory_structure(self):
        """Create directory structure for CoM anchors."""
        anchor_types = ["anchor_zero", "anchor_peak", "anchor_energy"]
        com_parts = ["com_hips", "com_shoulders", "com_torso"]
        
        for anchor_type in anchor_types:
            for com_part in com_parts:
                base_path = self.com_base_dir / anchor_type / com_part
                for axis in ["ax0", "ax1"]:
                    (base_path / axis).mkdir(parents=True, exist_ok=True)

