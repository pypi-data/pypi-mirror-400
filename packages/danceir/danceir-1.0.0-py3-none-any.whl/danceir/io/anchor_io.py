"""Anchor data I/O operations."""

import pickle
from pathlib import Path
from typing import Any, Dict

from ..utils.exceptions import IOError


class AnchorIO:
    """Handle loading and saving of anchor data."""
    
    @staticmethod
    def save_anchor(filepath, data):
        """Save anchor data to pickle file.
        
        Parameters
        ----------
        filepath : str or Path
            Full path to output file
        data : dict
            Anchor data dictionary to save
        
        Raises
        ------
        IOError
            If file cannot be written
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            raise IOError(f"Failed to save anchor data to {filepath}: {e}")
    
    @staticmethod
    def load_anchor(filepath):
        """Load anchor data from pickle file.
        
        Parameters
        ----------
        filepath : str or Path
            Path to pickle file
        
        Returns
        -------
        dict
            Anchor data dictionary
        
        Raises
        ------
        IOError
            If file cannot be loaded
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise IOError(f"Anchor file not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            raise IOError(f"Failed to load anchor data from {filepath}: {e}")
    
    @staticmethod
    def save_anchor_with_path(base_path, relative_path, data):
        """Save anchor data using base path and relative path.
        
        Parameters
        ----------
        base_path : str or Path
            Base directory path
        relative_path : str
            Relative path within base directory
        data : dict
            Anchor data dictionary to save
        """
        full_path = Path(base_path) / relative_path
        AnchorIO.save_anchor(full_path, data)

