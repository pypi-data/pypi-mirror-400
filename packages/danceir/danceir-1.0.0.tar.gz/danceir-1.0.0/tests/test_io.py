"""Tests for I/O module."""

import pytest
import numpy as np
import pickle
from pathlib import Path
import tempfile

from danceir.io import KeypointLoader
from danceir.utils.exceptions import InvalidKeypointDataError


class TestKeypointLoader:
    """Test KeypointLoader class."""
    
    def test_load_keypoints_pickle_valid(self):
        """Test loading valid keypoint pickle file."""
        # Create a temporary pickle file with valid data
        keypoints_data = {
            'keypoints2d': np.random.rand(1, 100, 17, 3)  # 1 person, 100 frames, 17 joints, [x,y,conf]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            pickle.dump(keypoints_data, f)
            temp_path = Path(f.name)
        
        try:
            loader = KeypointLoader()
            result = loader.load_keypoints_pickle(temp_path)
            assert 'keypoints2d' in result
            assert result['keypoints2d'].shape == (1, 100, 17, 3)
        finally:
            temp_path.unlink()
    
    def test_load_keypoints_pickle_file_not_found(self):
        """Test loading non-existent file raises error."""
        loader = KeypointLoader()
        with pytest.raises(InvalidKeypointDataError, match="File not found"):
            loader.load_keypoints_pickle("nonexistent_file.pkl")
    
    def test_extract_all_keypoints_2d(self):
        """Test extracting all 2D keypoints."""
        keypoints_data = {
            'keypoints2d': np.random.rand(1, 50, 17, 3)
        }
        
        loader = KeypointLoader()
        result = loader.extract_all_keypoints_2d(keypoints_data)
        
        assert result.shape == (50, 17, 2)  # frames, joints, [x,y]
        assert result.dtype == np.float64 or result.dtype == np.float32
    
    def test_extract_all_keypoints_2d_missing_key(self):
        """Test extracting keypoints with missing key raises error."""
        keypoints_data = {'wrong_key': np.array([1, 2, 3])}
        
        loader = KeypointLoader()
        with pytest.raises(InvalidKeypointDataError, match="Missing 'keypoints2d'"):
            loader.extract_all_keypoints_2d(keypoints_data)
    
    def test_extract_marker_position(self):
        """Test extracting specific marker position."""
        keypoints_data = {
            'keypoints2d': np.random.rand(1, 30, 17, 3)
        }
        
        loader = KeypointLoader()
        x, y = loader.extract_marker_position(keypoints_data, marker_id=9, person_idx=0)
        
        assert len(x) == 30
        assert len(y) == 30
        assert x.shape == y.shape
    
    def test_extract_marker_position_invalid_id(self):
        """Test extracting invalid marker ID raises error."""
        keypoints_data = {
            'keypoints2d': np.random.rand(1, 30, 17, 3)
        }
        
        loader = KeypointLoader()
        with pytest.raises(InvalidKeypointDataError):
            loader.extract_marker_position(keypoints_data, marker_id=999, person_idx=0)

