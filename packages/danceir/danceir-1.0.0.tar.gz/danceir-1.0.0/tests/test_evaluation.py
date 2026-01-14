"""Tests for evaluation module."""

import pytest
import numpy as np

from danceir.evaluation import dance_tempo_evaluation, DanceTempoEvaluationResult


class TestDanceTempoEvaluation:
    """Test dance tempo evaluation functions."""
    
    def test_dance_tempo_evaluation_scalar_perfect_match(self):
        """Test evaluation with scalar inputs - perfect match."""
        result = dance_tempo_evaluation(120.0, 120.0)
        
        assert isinstance(result, DanceTempoEvaluationResult)
        assert result.accuracy == 100.0
        assert result.mean_dts == 1.0
        assert np.all(result.hits == True)
    
    def test_dance_tempo_evaluation_scalar_close_match(self):
        """Test evaluation with scalar inputs - close match."""
        result = dance_tempo_evaluation(120.0, 121.0)
        
        assert isinstance(result, DanceTempoEvaluationResult)
        assert result.accuracy > 0
        assert result.mean_dts > 0
    
    def test_dance_tempo_evaluation_array(self):
        """Test evaluation with array inputs."""
        ref = np.array([120, 125, 130])
        est = np.array([121, 124, 131])
        
        result = dance_tempo_evaluation(ref, est)
        
        assert isinstance(result, DanceTempoEvaluationResult)
        assert len(result.dts_scores) == 3
        assert len(result.hits) == 3
        assert len(result.dts_scores) == len(ref)  # Check length matches input
    
    def test_dance_tempo_evaluation_return_scores_only(self):
        """Test evaluation returning only scores array."""
        ref = np.array([120, 125, 130])
        est = np.array([121, 124, 131])
        
        scores = dance_tempo_evaluation(ref, est, return_all=False)
        
        assert isinstance(scores, np.ndarray)
        assert len(scores) == 3
        assert np.all((scores >= 0) & (scores <= 1))
    
    def test_dance_tempo_evaluation_shape_mismatch(self):
        """Test evaluation with mismatched shapes raises error."""
        ref = np.array([120, 125])
        est = np.array([121, 124, 131])
        
        with pytest.raises(ValueError, match="Shape mismatch"):
            dance_tempo_evaluation(ref, est)
    
    def test_dance_tempo_evaluation_negative_bpm(self):
        """Test evaluation with negative BPM raises error."""
        with pytest.raises(ValueError, match="BPM values must be positive"):
            dance_tempo_evaluation(-120.0, 120.0)
    
    def test_dance_tempo_evaluation_octave_equivalence(self):
        """Test that octave equivalents are recognized."""
        # 60 BPM should match 120 BPM (2x) and 30 BPM (0.5x)
        result_2x = dance_tempo_evaluation(60.0, 120.0, tau=0.2)
        result_half = dance_tempo_evaluation(60.0, 30.0, tau=0.2)
        
        # Should have high scores due to octave equivalence
        assert result_2x.mean_dts > 0.5
        assert result_half.mean_dts > 0.5
    
    def test_dance_tempo_evaluation_result_to_dict(self):
        """Test converting result to dictionary."""
        result = dance_tempo_evaluation(120.0, 121.0)
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert 'accuracy' in result_dict
        assert 'mean_dts' in result_dict
        assert 'hits' in result_dict
    
    def test_dance_tempo_evaluation_result_summary(self):
        """Test result summary string."""
        result = dance_tempo_evaluation(120.0, 121.0)
        summary = result.summary()
        
        assert isinstance(summary, str)
        assert 'Accuracy' in summary
        assert 'DTS' in summary

