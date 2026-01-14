"""Tests for pipeline functions."""

import pytest
import numpy as np

from danceir.pipelines import estimate_tempo_from_keypoints


class TestEstimateTempoFromKeypoints:
    """Test estimate_tempo_from_keypoints pipeline."""
    
    def test_estimate_tempo_from_keypoints_basic(self):
        """Test basic tempo estimation with valid keypoints."""
        # Create synthetic keypoint data: 200 frames, 17 joints, 2D
        np.random.seed(42)
        keypoints_2d = np.random.rand(200, 17, 2) * 100
        
        result = estimate_tempo_from_keypoints(
            keypoints_2d,
            marker_groups=[(9, 10)],  # both hands
            axis='y',
            use_com=False,
            fps=30.0
        )
        
        assert isinstance(result, dict)
        assert 'combined_anchors' in result
        assert 'gtempo' in result['combined_anchors']
        assert isinstance(result['combined_anchors']['gtempo'], (int, float))
        assert result['combined_anchors']['gtempo'] > 0
    
    def test_estimate_tempo_from_keypoints_with_com(self):
        """Test tempo estimation with center of mass."""
        np.random.seed(42)
        keypoints_2d = np.random.rand(150, 17, 2) * 100
        
        result = estimate_tempo_from_keypoints(
            keypoints_2d,
            marker_groups=[(9, 10), (15, 16)],
            axis='y',
            use_com=True,
            com_type='torso',
            fps=30.0
        )
        
        assert isinstance(result, dict)
        assert 'combined_anchors' in result
        assert result['combined_anchors']['gtempo'] > 0
    
    def test_estimate_tempo_from_keypoints_invalid_shape(self):
        """Test with invalid keypoint shape raises error."""
        keypoints_2d = np.random.rand(100, 17)  # Missing last dimension
        
        with pytest.raises(ValueError, match="must be of shape"):
            estimate_tempo_from_keypoints(keypoints_2d, fps=30.0)
    
    def test_estimate_tempo_from_keypoints_invalid_axis(self):
        """Test with invalid axis raises error."""
        keypoints_2d = np.random.rand(100, 17, 2)
        
        with pytest.raises(ValueError, match="axis must be"):
            estimate_tempo_from_keypoints(keypoints_2d, axis='z', fps=30.0)
    
    def test_estimate_tempo_from_keypoints_invalid_com_type(self):
        """Test with invalid com_type raises error."""
        keypoints_2d = np.random.rand(100, 17, 2)
        
        with pytest.raises(ValueError, match="com_type must be"):
            estimate_tempo_from_keypoints(
                keypoints_2d,
                use_com=True,
                com_type='invalid',
                fps=30.0
            )
    
    def test_estimate_tempo_from_keypoints_default_marker_groups(self):
        """Test with default marker groups (None)."""
        np.random.seed(42)
        keypoints_2d = np.random.rand(200, 17, 2) * 100
        
        result = estimate_tempo_from_keypoints(
            keypoints_2d,
            marker_groups=None,  # Should default to [(9, 10), (15, 16)]
            fps=30.0
        )
        
        assert isinstance(result, dict)
        assert result['combined_anchors']['gtempo'] > 0
    
    def test_estimate_tempo_from_keypoints_different_anchor_methods(self):
        """Test different anchor extraction methods."""
        np.random.seed(42)
        keypoints_2d = np.random.rand(200, 17, 2) * 100
        
        methods = ['zero_velocity', 'peak_velocity', 'energy']
        for method in methods:
            result = estimate_tempo_from_keypoints(
                keypoints_2d,
                marker_groups=[(9, 10)],
                anchor_method=method,
                fps=30.0
            )
            assert result['combined_anchors']['gtempo'] > 0
    
    def test_estimate_tempo_from_keypoints_invalid_anchor_method(self):
        """Test with invalid anchor_method raises error."""
        keypoints_2d = np.random.rand(100, 17, 2)
        
        with pytest.raises(ValueError, match="anchor_method must be"):
            estimate_tempo_from_keypoints(
                keypoints_2d,
                anchor_method='invalid_method',
                fps=30.0
            )

