"""Evaluation metrics for tempo estimation.

This module provides evaluation functions for dance tempo estimation,
following standard MIR (Music Information Retrieval) evaluation patterns.
"""

import numpy as np
from dataclasses import dataclass, asdict
from typing import Union, Optional
import warnings


@dataclass
class DanceTempoEvaluationResult:
    """Results from DTS evaluation.
    
    Attributes
    ----------
    dts_scores : np.ndarray
        DTS scores per frame, shape (n,), range [0, 1]
        1.0 = perfect match, 0.0 = miss beyond tolerance
    
    hits : np.ndarray
        Boolean array indicating hits, shape (n,)
        True if dts_scores > 0.0 (within tolerance), False otherwise
    
    octave_errors : np.ndarray
        Raw octave errors log₂(estimated/ref), shape (n,)
    
    distances : np.ndarray
        Distance to nearest octave (-1, 0, +1), shape (n,)
    
    accuracy : float
        Overall accuracy percentage (% of frames with DTS > 0)
    
    hit_rate : float
        Fraction of frames that hit (same as accuracy/100)
    
    mean_dts : float
        Mean DTS score across all frames
    
    std_dts : float
        Standard deviation of DTS scores
    
    hit_indices : np.ndarray
        Frame indices where DTS > 0 (hits)
    
    hit_ref_bpm : np.ndarray
        Reference BPM values at hit frames
    
    hit_est_bpm : np.ndarray
        Estimated BPM values at hit frames
    
    n_frames : int
        Total number of frames evaluated
    
    n_hits : int
        Number of hit frames
    
    tau : float
        Tolerance parameter used (in octaves)
    
    octave_weights : np.ndarray
        Octave weights used (typically [-1, 0, +1])
    """
    # Per-frame metrics
    dts_scores: np.ndarray
    hits: np.ndarray
    octave_errors: np.ndarray
    distances: np.ndarray
    
    # Aggregate statistics
    accuracy: float
    hit_rate: float
    mean_dts: float
    std_dts: float
    
    # Hit information
    hit_indices: np.ndarray
    hit_ref_bpm: np.ndarray
    hit_est_bpm: np.ndarray
    
    # Metadata
    n_hits: int

    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.
        
        Note: numpy arrays will be converted to lists.
        """
        result_dict = asdict(self)
        # Convert numpy arrays to lists for JSON serialization
        for key, value in result_dict.items():
            if isinstance(value, np.ndarray):
                result_dict[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                result_dict[key] = float(value)
        return result_dict
    
    def summary(self) -> str:
        """Return a human-readable summary string."""
        n_frames = len(self.dts_scores)
        return (
            f"DTS Evaluation Summary:\n"
            f"  Accuracy: {self.accuracy:.2f}%\n"
            f"  Hit Rate: {self.hit_rate:.3f}\n"
            f"  Mean DTS: {self.mean_dts:.3f} ± {self.std_dts:.3f}\n"
            f"  Hits: {self.n_hits}/{n_frames} frames"
        )


def dance_tempo_evaluation(
    ref_bpm: Union[float, np.ndarray],
    estimated_bpm: Union[float, np.ndarray],
    tau: float = 0.13,
    octave_weights: Optional[np.ndarray] = None,
    return_all: bool = True
) -> Union[np.ndarray, DanceTempoEvaluationResult]:
    """Compute Dance-Tempo Score (DTS) between reference and estimated BPM.
    
    DTS is a continuous metric that evaluates tempo estimation accuracy,
    accounting for octave errors (tempo at 2x or 0.5x the reference tempo).
    A score of 1.0 indicates perfect match (within tolerance), 0.0 indicates
    a miss beyond the tolerance threshold.
    
    Parameters
    ----------
    ref_bpm : float or np.ndarray, shape (n,)
        Ground-truth musical tempo in BPM.
        Can be scalar or 1D array.
    
    estimated_bpm : float or np.ndarray, shape (n,)
        Estimated tempo in BPM.
        Must match shape of ref_bpm.
    
    tau : float, default=0.13
        Tolerance in octaves. Default 0.13 ≈ 4% tolerance.
        Lower values = stricter evaluation.
    
    octave_weights : np.ndarray, optional
        Octave weights to consider. Default: [-1.0, 0.0, 1.0]
        Corresponds to 0.5x, 1x, and 2x tempo ratios.
    
    return_all : bool, default=True
        If True, return DTSEvaluationResult with all metrics.
        If False, return only dts_scores array.
    
    Returns
    -------
    If return_all=True:
        DTSEvaluationResult
            Complete evaluation results with scores, statistics, and metadata.
            Includes:
            - dts_scores: Continuous scores [0, 1]
            - hits: Boolean array (True if dts > 0.0)
            - accuracy: Percentage of hits
            - Other statistics and metadata
    
    If return_all=False:
        np.ndarray, shape (n,)
            DTS scores per frame [0, 1].
    
    Examples
    --------
    >>> # Simple usage: array inputs
    >>> ref = np.array([120, 125, 130])
    >>> est = np.array([121, 124, 131])
    >>> result = compute_dts(ref, est)
    >>> print(f"Accuracy: {result.accuracy:.1f}%")
    >>> print(f"Hits: {result.hits.sum()}/{len(result.hits)}")
    
    >>> # Scalar inputs
    >>> result = compute_dts(120.0, 121.0)
    >>> print(result.accuracy)
    
    >>> # Just get scores (no statistics)
    >>> dts = compute_dts(ref, est, return_all=False)
    
    >>> # Use hits boolean array for filtering
    >>> result = compute_dts(ref, est)
    >>> hit_refs = ref[result.hits]  # Reference BPMs at hits
    >>> hit_ests = est[result.hits]  # Estimated BPMs at hits
    
    Notes
    -----
    The DTS metric accounts for octave equivalence in tempo perception:
    - Tempo at 0.5x (half-speed) is considered equivalent
    - Tempo at 1.0x (exact match) is ideal
    - Tempo at 2.0x (double-speed) is considered equivalent
    
    The score decreases linearly from 1.0 to 0.0 as the distance from
    the nearest octave equivalent increases, reaching 0.0 at tau octaves away.
    
    A hit is defined as any frame with dts_scores > 0.0 (within tolerance).
    """
    # Input validation and normalization
    ref_bpm = np.asarray(ref_bpm, dtype=float)
    estimated_bpm = np.asarray(estimated_bpm, dtype=float)
    
    # Ensure 1D arrays (handle scalar inputs)
    ref_bpm = np.atleast_1d(ref_bpm).flatten()
    estimated_bpm = np.atleast_1d(estimated_bpm).flatten()
    
    # Validate shapes
    if ref_bpm.shape != estimated_bpm.shape:
        raise ValueError(
            f"Shape mismatch: ref_bpm {ref_bpm.shape} vs "
            f"estimated_bpm {estimated_bpm.shape}"
        )
    
    if ref_bpm.ndim > 1:
        raise ValueError("Input must be 1D array or scalar")
    
    if len(ref_bpm) == 0:
        raise ValueError("Input arrays cannot be empty")
    
    # Validate values
    if np.any(ref_bpm <= 0) or np.any(estimated_bpm <= 0):
        raise ValueError("BPM values must be positive")
    
    if tau <= 0:
        raise ValueError(f"tau must be positive, got {tau}")
    
    # Set default octave weights
    if octave_weights is None:
        octave_weights = np.array([-1.0, 0.0, 1.0])  # 0.5x, 1x, 2x
    else:
        octave_weights = np.asarray(octave_weights)
    
    # Handle NaN/Inf values
    valid_mask = np.isfinite(ref_bpm) & np.isfinite(estimated_bpm)
    if not np.all(valid_mask):
        n_invalid = np.sum(~valid_mask)
        warnings.warn(
            f"{n_invalid} values are NaN/inf, will be set to 0.0 DTS",
            UserWarning
        )
    
    # Core DTS computation
    # Compute octave errors: log₂(estimated/ref)
    e = np.log2(np.where(valid_mask, estimated_bpm / ref_bpm, 1.0))
    
    # Distance to nearest octave weight
    d = np.abs(e[:, None] - octave_weights).min(axis=1)
    
    # Clip by tolerance and convert to score
    d_clip = np.minimum(d, tau)
    dts_scores = 1.0 - d_clip / tau
    
    # Set invalid values to 0
    dts_scores[~valid_mask] = 0.0
    
    # Compute boolean hits array (threshold fixed at 0.0)
    hits = dts_scores > 0.0
    
    # If just returning scores, return early
    if not return_all:
        return dts_scores
    
    # Compute aggregate statistics from hits
    accuracy = float(np.mean(hits) * 100.0)
    hit_rate = float(np.mean(hits))
    mean_dts = float(np.mean(dts_scores[valid_mask])) if np.any(valid_mask) else 0.0
    std_dts = float(np.std(dts_scores[valid_mask])) if np.any(valid_mask) else 0.0
    
    # Hit information (using hits boolean array)
    hit_indices = np.nonzero(hits)[0]
    hit_ref_bpm = ref_bpm[hit_indices]
    hit_est_bpm = estimated_bpm[hit_indices]
    
    # Create result object
    result = DanceTempoEvaluationResult(
        dts_scores=dts_scores,
        hits=hits,
        octave_errors=e,
        distances=d,
        accuracy=accuracy,
        hit_rate=hit_rate,
        mean_dts=mean_dts,
        std_dts=std_dts,
        hit_indices=hit_indices,
        hit_ref_bpm=hit_ref_bpm,
        hit_est_bpm=hit_est_bpm,
        n_hits=len(hit_indices),
    )
    
    return result

