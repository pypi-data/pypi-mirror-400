"""
Audio Processing Utilities
===========================

General audio processing functions used across labs.
"""

import numpy as np
import librosa
from scipy import signal


def normalize_audio(waveform, target_level=0.9):
    """
    Normalize audio to a target peak amplitude.
    
    Prevents clipping and ensures consistent volume levels.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Input audio waveform
    target_level : float, default=0.9
        Target peak amplitude (0.0 to 1.0)
    
    Returns:
    --------
    normalized : numpy.ndarray
        Normalized audio
    
    Example:
    --------
    >>> normalized = normalize_audio(waveform, target_level=0.9)
    >>> print(f"Peak amplitude: {np.max(np.abs(normalized)):.2f}")
    """
    max_amp = np.max(np.abs(waveform))
    if max_amp > 0:
        return waveform * (target_level / max_amp)
    return waveform


def trim_silence(waveform, sr, top_db=20, frame_length=2048, hop_length=512):
    """
    Trim leading and trailing silence from audio.
    
    Removes quiet sections at the beginning and end of audio.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Input audio waveform
    sr : int
        Sampling rate
    top_db : float, default=20
        Threshold in dB below peak to consider as silence
    frame_length : int, default=2048
        Frame length for silence detection
    hop_length : int, default=512
        Hop length for silence detection
    
    Returns:
    --------
    trimmed : numpy.ndarray
        Audio with silence removed
    
    Example:
    --------
    >>> trimmed = trim_silence(waveform, sr, top_db=20)
    >>> print(f"Original: {len(waveform)} samples, Trimmed: {len(trimmed)} samples")
    """
    trimmed, _ = librosa.effects.trim(
        waveform, top_db=top_db, 
        frame_length=frame_length, 
        hop_length=hop_length
    )
    return trimmed


def add_noise(waveform, noise_level_db=-20):
    """
    Add Gaussian white noise to audio signal.
    
    Useful for testing robustness and data augmentation.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Input audio waveform
    noise_level_db : float, default=-20
        Noise level in dB relative to signal
    
    Returns:
    --------
    noisy : numpy.ndarray
        Audio with added noise
    
    Example:
    --------
    >>> noisy = add_noise(waveform, noise_level_db=-15)
    >>> snr = compute_snr(waveform, noisy)
    >>> print(f"SNR: {snr:.1f} dB")
    """
    # Calculate signal power
    signal_power = np.mean(waveform ** 2)
    
    # Calculate noise power for target SNR
    noise_power = signal_power / (10 ** (noise_level_db / 10))
    
    # Generate and scale noise
    noise = np.random.randn(len(waveform)) * np.sqrt(noise_power)
    
    return waveform + noise


def compute_snr(clean_signal, noisy_signal):
    """
    Compute Signal-to-Noise Ratio (SNR) in dB.
    
    Measures quality of noisy signal compared to clean reference.
    
    Parameters:
    -----------
    clean_signal : numpy.ndarray
        Clean reference signal
    noisy_signal : numpy.ndarray
        Noisy signal
    
    Returns:
    --------
    snr_db : float
        SNR in decibels
    
    Example:
    --------
    >>> snr = compute_snr(original, noisy)
    >>> print(f"SNR: {snr:.2f} dB")
    """
    # Extract noise
    noise = noisy_signal - clean_signal
    
    # Calculate powers
    signal_power = np.mean(clean_signal ** 2)
    noise_power = np.mean(noise ** 2)
    
    # Compute SNR in dB
    if noise_power > 0:
        snr_db = 10 * np.log10(signal_power / noise_power)
    else:
        snr_db = np.inf
    
    return snr_db


def stereo_to_mono(stereo_waveform):
    """
    Convert stereo audio to mono by averaging channels.
    
    Simplifies processing by reducing to single channel.
    
    Parameters:
    -----------
    stereo_waveform : numpy.ndarray
        Stereo audio, shape (2, samples) or (samples, 2)
    
    Returns:
    --------
    mono : numpy.ndarray
        Mono audio, shape (samples,)
    
    Example:
    --------
    >>> stereo, sr = load_audio('stereo_file.wav', mono=False)
    >>> mono = stereo_to_mono(stereo)
    >>> print(f"Converted from {stereo.shape} to {mono.shape}")
    """
    # Handle both (2, samples) and (samples, 2) formats
    if stereo_waveform.ndim == 2:
        if stereo_waveform.shape[0] == 2:
            # (2, samples) format
            return np.mean(stereo_waveform, axis=0)
        elif stereo_waveform.shape[1] == 2:
            # (samples, 2) format
            return np.mean(stereo_waveform, axis=1)
    
    # Already mono
    return stereo_waveform
