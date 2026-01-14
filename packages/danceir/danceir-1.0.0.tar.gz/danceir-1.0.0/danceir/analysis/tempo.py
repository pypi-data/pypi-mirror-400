"""Tempo estimation from anchor sequences.

This module implements multi-anchor tempo estimation for dance motion analysis,
using tempogram computation and sinusoidal alignment.
"""

import numpy as np

from ..preprocessing import binary_to_peak


def compute_tempogram(anchor_signal, sampling_rate, window_length, hop_size, tempi=None):
    """Compute tempogram from anchor signal using short-time Fourier transform.
    
    Parameters
    ----------
    anchor_signal : np.ndarray
        Input anchor signal array of shape (n_frames, n_axes) or (n_frames,) for 1D
    sampling_rate : float
        Sampling rate in Hz
    window_length : int
        Window length in samples for STFT
    hop_size : int
        Hop size in samples for STFT
    tempi : np.ndarray, optional
        Tempo range in BPM (default: 45-140 BPM in steps of 1)
    
    Returns
    -------
    tuple
        (tempogram_ab, tempogram_raw, time_axis, tempo_axis)
        - tempogram_ab: Absolute tempogram (magnitude)
        - tempogram_raw: Complex tempogram
        - time_axis: Time axis in seconds
        - tempo_axis: Tempo axis in BPM
    """
    if tempi is None:
        tempi = np.arange(45, 140, 1)
    
    # Ensure 2D array
    if anchor_signal.ndim == 1:
        anchor_signal = anchor_signal.reshape(-1, 1)
    
    # Process first axis/channel (following original implementation)
    hann_window = np.hanning(window_length)
    half_window_length = window_length // 2
    signal_length = len(anchor_signal[:, 0])
    
    # Pad signal for windowing
    left_padding = half_window_length
    right_padding = half_window_length
    padded_signal_length = signal_length + left_padding + right_padding
    padded_signal = np.concatenate((
        np.zeros(left_padding),
        anchor_signal[:, 0],
        np.zeros(right_padding)
    ))
    
    time_indices = np.arange(padded_signal_length)
    num_frames = int(np.floor(padded_signal_length - window_length) / hop_size) + 1
    num_tempo_values = len(tempi)
    tempogram = np.zeros((num_tempo_values, num_frames), dtype=np.complex_)
    
    # Compute tempogram for each tempo
    for tempo_idx in range(num_tempo_values):
        frequency = (tempi[tempo_idx] / 60) / sampling_rate  # Convert BPM to Hz to normalized frequency
        complex_exponential = np.exp(-2 * np.pi * 1j * frequency * time_indices)
        modulated_signal = padded_signal * complex_exponential
        
        for frame_idx in range(num_frames):
            start_index = frame_idx * hop_size
            end_index = start_index + window_length
            tempogram[tempo_idx, frame_idx] = np.sum(
                hann_window * modulated_signal[start_index:end_index]
            )
    
    tempogram_raw = tempogram
    tempogram_ab = np.abs(tempogram)
    
    time_axis_seconds = np.arange(num_frames) * hop_size / sampling_rate
    tempo_axis_bpm = tempi
    
    return tempogram_ab, tempogram_raw, time_axis_seconds, tempo_axis_bpm


def estimate_tempo_per_anchor(tempogram_ab_list, tempogram_raw_list, fps, signal_length,
                              window_length, hop_size, tempi):
    """Estimate tempo for each anchor using tempogram analysis.
    
    Parameters
    ----------
    tempogram_ab_list : list of np.ndarray
        List of absolute tempograms (one per anchor)
    tempogram_raw_list : list of np.ndarray
        List of complex tempograms (one per anchor)
    fps : float
        Sampling rate in Hz
    signal_length : int
        Length of original anchor signal
    window_length : int
        Window length used for tempogram computation
    hop_size : int
        Hop size used for tempogram computation
    tempi : np.ndarray
        Tempo range in BPM
    
    Returns
    -------
    list of dict
        List of dictionaries (one per anchor) containing:
        - 'magnitude': Magnitude per window
        - 'bpm': BPM estimate per window
        - 'phase': Phase per window
        - 'complex': Complex value per window
        - 'median_tempo': Median tempo in BPM
        - 'beat_pulse': Estimated beat pulse signal
    """
    hann_window = np.hanning(window_length)
    half_window_length = window_length // 2
    padded_curve_length = signal_length + half_window_length
    
    tempo_data = []
    
    for tempogram_ab, tempogram_raw in zip(tempogram_ab_list, tempogram_raw_list):
        num_frames = tempogram_raw.shape[1]
        estimated_beat_pulse = np.zeros(padded_curve_length)
        bpm_list, complex_list, mag_list, phase_list = [], [], [], []
        
        for frame_idx in range(num_frames):
            # Find strongest tempo bin for current frame
            peak_idx = np.argmax(tempogram_ab[:, frame_idx])
            peak_bpm = tempi[peak_idx]
            frequency = (peak_bpm / 60) / fps  # Convert BPM to Hz
            
            complex_value = tempogram_raw[peak_idx, frame_idx]
            phase = -np.angle(complex_value) / (2 * np.pi)
            magnitude = np.abs(complex_value)
            
            # Reconstruct sinusoidal kernel
            start_index = frame_idx * hop_size
            end_index = start_index + window_length
            time_kernel = np.arange(start_index, end_index)
            sinusoidal_kernel = hann_window * np.cos(
                2 * np.pi * (time_kernel * frequency - phase)
            )
            
            # Accumulate weighted sinusoid
            valid_end = min(end_index, padded_curve_length)
            valid_len = valid_end - start_index
            if valid_len > 0:
                estimated_beat_pulse[start_index:valid_end] += (
                    magnitude * sinusoidal_kernel[:valid_len]
                )
            
            mag_list.append(magnitude)
            bpm_list.append(peak_bpm)
            phase_list.append(phase)
            complex_list.append(complex_value)
        
        tempo_data.append({
            "magnitude": mag_list,
            "bpm": bpm_list,
            "phase": phase_list,
            "complex": complex_list,
            "median_tempo": np.median(bpm_list),
            "beat_pulse": estimated_beat_pulse,
        })
    
    return tempo_data


def compute_alignment(signal, frequency, fps):
    """Compute alignment between signal and sinusoidal template at given frequency.
    
    Parameters
    ----------
    signal : np.ndarray
        Input signal array (1D)
    frequency : float
        Frequency in Hz
    fps : float
        Sampling rate in Hz
    
    Returns
    -------
    tuple
        (best_correlation, best_lag, full_correlation, lags)
        - best_correlation: Best correlation value (-1 to 1)
        - best_lag: Lag in seconds at best correlation
        - full_correlation: Full correlation array
        - lags: Lag array in seconds
    """
    x = np.asarray(signal).flatten()
    x = x - np.mean(x)
    
    # Skip empty/constant signals
    if np.allclose(x, 0) or np.std(x) < 1e-8:
        return 0.0, 0.0, np.zeros_like(x), np.arange(len(x)) / fps
    
    # Reference sinusoid
    sine = np.sin(2 * np.pi * frequency * np.arange(len(x)) / fps)
    sine -= np.mean(sine)
    
    denom = np.sqrt(np.sum(x**2) * np.sum(sine**2))
    if denom < 1e-12:  # Avoid division by zero
        return 0.0, 0.0, np.zeros_like(x), np.arange(len(x)) / fps
    
    corr = np.correlate(x, sine, mode="full") / denom
    lags = np.arange(-len(x) + 1, len(x)) / fps
    
    best_idx = np.argmax(np.abs(corr))
    best_corr = float(corr[best_idx])
    best_lag = float(lags[best_idx])
    
    return best_corr, best_lag, corr, lags


def create_aligned_pulse(anchor_sequence, frequency, fps):
    """Create aligned sinusoidal pulse signal from anchor sequence.
    
    Parameters
    ----------
    anchor_sequence : np.ndarray
        Anchor signal array (1D)
    frequency : float
        Frequency in Hz
    fps : float
        Sampling rate in Hz
    
    Returns
    -------
    np.ndarray
        Aligned pulse signal (half-wave rectified sinusoid)
    """
    anchor_seq = np.asarray(anchor_sequence).flatten()
    anchor_seq = anchor_seq - np.mean(anchor_seq)
    
    # Compute period and number of cycles
    period_samples = fps / frequency  # samples per cycle
    n_cycles = int(np.ceil(len(anchor_seq) / period_samples))
    total_samples = int(n_cycles * period_samples)
    
    # Generate sinusoidal pulse
    sine = np.sin(2 * np.pi * frequency * np.arange(int(2 * total_samples)) / fps)
    sine -= np.mean(sine)
    sine = np.clip(sine, 0, None)  # Half-wave rectification
    
    # Cross-correlate to find best alignment
    corr = np.correlate(anchor_seq, sine, mode='full')
    lags = np.arange(-len(sine) + 1, len(anchor_seq))
    best_lag = lags[np.argmax(corr)]
    
    # Align pulse
    aligned_pulse = np.roll(sine, best_lag)
    
    return aligned_pulse


def estimate_dance_tempo(multi_anchor_segments, fps, window_length, hop_size, tempi_range,
                         signal_length=None, peak_duration=0.1):
    """Estimate global tempo from multiple anchor segments.
    
    This is the core multi-anchor tempo estimation algorithm that:
    1. Computes tempograms for each anchor segment
    2. Estimates tempo per anchor
    3. Tests alignment between anchors and sinusoidal templates
    4. Selects best global tempo based on alignment
    
    Parameters
    ----------
    multi_anchor_segments : dict
        Dictionary where keys are segment names and values are dicts with:
        - 'segments': list of anchor sequences (binary or continuous)
        - 'names': list of segment names corresponding to segments
    fps : float
        Sampling rate in Hz
    window_length : int
        Window length for tempogram computation
    hop_size : int
        Hop size for tempogram computation
    tempi_range : np.ndarray
        Tempo range in BPM (e.g., np.arange(45, 140, 1))
    signal_length : int, optional
        Original signal length. If None, inferred from first segment
    peak_duration : float, optional
        Duration for converting binary anchors to peaks (default: 0.1 seconds)
    
    Returns
    -------
    dict
        Dictionary with segment names as keys, each containing:
        - 'gtempo': Global tempo estimate in BPM
        - 'best_segment': Name of best aligned segment
        - 'beat_pulse': Aligned beat pulse signal
        - 'anchor_seq': Best anchor sequence used
        - 'per_anchor': List of per-anchor tempo estimates
        - 'alignment': Dictionary with alignment results
    """
    tempo_data = {}
    
    for seg_key, seg_info in multi_anchor_segments.items():
        segments = seg_info["segments"]
        segment_names = seg_info["names"]
        
        if signal_length is None and len(segments) > 0:
            signal_length = len(segments[0])
        
        # Convert anchors to peak signals and compute tempograms
        anchors_peak = []
        tempogram_ab_list = []
        tempogram_raw_list = []
        
        for anchor in segments:
            anchor_peak = binary_to_peak(anchor, peak_duration=peak_duration, sampling_rate=fps)
            anchors_peak.append(anchor_peak)
            
            temp_ab, temp_raw, _, _ = compute_tempogram(
                anchor_peak, fps, window_length, hop_size, tempi_range
            )
            tempogram_ab_list.append(temp_ab)
            tempogram_raw_list.append(temp_raw)
        
        # Estimate tempo per anchor
        per_anchor = estimate_tempo_per_anchor(
            tempogram_ab_list,
            tempogram_raw_list,
            fps,
            signal_length,
            window_length,
            hop_size,
            tempi_range
        )
        
        # Build test frequencies from anchor-wise median tempos
        test_frequencies = [
            np.round(d["median_tempo"] / 60.0, 2) for d in per_anchor
        ]
        
        # Test alignment between anchors and frequencies
        alignment_results = {}
        best_global = {"freq": None, "corr": 0.0, "lag": None}
        
        for freq in test_frequencies:
            for anchor_peak in anchors_peak:
                best_corr, best_lag, _, _ = compute_alignment(anchor_peak, freq, fps)
                alignment_results[freq] = (best_corr, best_lag)
                
                if abs(best_corr) > abs(best_global["corr"]):
                    best_global.update({
                        "freq": freq,
                        "corr": best_corr,
                        "lag": best_lag
                    })
        
        # Determine best segment and create aligned pulse
        if best_global["freq"] is not None:
            best_index = test_frequencies.index(best_global["freq"])
            best_segment_name = segment_names[best_index]
            best_anchor_seq = anchors_peak[best_index]
            best_freq = best_global["freq"]
            
            aligned_pulse = create_aligned_pulse(best_anchor_seq, best_freq, fps)
        else:
            best_segment_name = None
            best_anchor_seq = None
            aligned_pulse = None
        
        # Compute global tempo in BPM
        if best_global["freq"] is None:
            # Fallback: use median of medians
            gtempo = float(np.round(
                np.median([d["median_tempo"] for d in per_anchor]),
                2
            ))
        else:
            gtempo = float(np.round(best_global["freq"] * 60.0, 2))
        
        
        all_anchor_seq = {
            seg: peak
            for seg, peak in zip(segment_names, anchors_peak)
        }
        
        tempo_data[seg_key] = {
            "gtempo": gtempo,
            "best_segment": best_segment_name,
            "rhytmic_anchor_pulse": aligned_pulse[:len(best_anchor_seq)],
            "best_anchor_seq": best_anchor_seq,
            "all_anchor_seq": all_anchor_seq,
            "per_anchor_tempo_features": per_anchor,
            "alignment": {
                "best": best_global,
                "all": alignment_results,
            },
        }
    
    return tempo_data

