"""Tests for features module."""

import pytest
import numpy as np

from danceir.features import (
    compute_com_variants,
    compute_com_hips,
    compute_com_shoulders,
    compute_com_torso,
    detect_segment_anchor,
    AnchorExtractor,
)


class TestCenterOfMass:
    """Test center of mass computation."""
    
    def test_compute_com_variants(self):
        """Test computing all COM variants."""
        keypoints_2d = np.random.rand(100, 17, 2) * 100
        
        com_hips, com_shoulders, com_torso = compute_com_variants(keypoints_2d)
        
        assert com_hips.shape == (100, 2)
        assert com_shoulders.shape == (100, 2)
        assert com_torso.shape == (100, 2)
    
    def test_compute_com_hips(self):
        """Test computing hips COM."""
        keypoints_2d = np.random.rand(50, 17, 2) * 100
        
        com = compute_com_hips(keypoints_2d)
        
        assert com.shape == (50, 2)
        assert not np.any(np.isnan(com))
    
    def test_compute_com_shoulders(self):
        """Test computing shoulders COM."""
        keypoints_2d = np.random.rand(50, 17, 2) * 100
        
        com = compute_com_shoulders(keypoints_2d)
        
        assert com.shape == (50, 2)
        assert not np.any(np.isnan(com))
    
    def test_compute_com_torso(self):
        """Test computing torso COM."""
        keypoints_2d = np.random.rand(50, 17, 2) * 100
        
        com = compute_com_torso(keypoints_2d)
        
        assert com.shape == (50, 2)
        assert not np.any(np.isnan(com))


class TestAnchorDetection:
    """Test anchor detection functions."""
    
    def test_detect_segment_anchor_basic(self):
        """Test basic segment anchor detection."""
        # Create synthetic signal
        signal = np.random.rand(200, 1)
        
        result = detect_segment_anchor(
            signal,
            fps=30.0,
            height_thres=0.1
        )
        
        assert isinstance(result, dict)
        assert 'sensor_anchors' in result
        assert result['sensor_anchors'].shape[0] == 200
    
    def test_anchor_extractor_class(self):
        """Test AnchorExtractor class."""
        signal = np.random.rand(100, 1)
        
        extractor = AnchorExtractor(fps=30.0)
        result = extractor.extract_segment_anchor(signal)
        
        assert isinstance(result, dict)
        assert 'sensor_anchors' in result

