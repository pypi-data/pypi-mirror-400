"""
Lab 1: Audio Loading and Waveform Visualization
===============================================

Functions for loading, processing, and visualizing audio files.
Covers basic audio operations like loading, resampling, and waveform plotting.
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt
from IPython.display import Audio, display


def load_audio(filename, sr=None, mono=True):
    """
    Load an audio file using librosa.
    
    Parameters:
    -----------
    filename : str
        Path to the audio file (.wav, .mp3, .flac, .ogg, etc.)
    sr : int, optional
        Target sampling rate. If None, uses original sampling rate
    mono : bool, default=True
        Convert stereo to mono if True
    
    Returns:
    --------
    waveform : numpy.ndarray
        Audio time series
    sampling_rate : int
        Sampling rate of the audio
    
    Example:
    --------
    >>> waveform, sr = load_audio('speech.wav')
    >>> print(f"Duration: {len(waveform)/sr:.2f} seconds")
    """
    waveform, sampling_rate = librosa.load(filename, sr=sr, mono=mono)
    return waveform, sampling_rate


def get_audio_info(waveform, sr):
    """
    Get basic information about an audio signal.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    
    Returns:
    --------
    info : dict
        Dictionary containing:
        - duration: Length in seconds
        - samples: Number of samples
        - sampling_rate: Samples per second
        - channels: Number of channels
        - max_amplitude: Maximum absolute amplitude
        - min_amplitude: Minimum amplitude
        - mean_amplitude: Mean amplitude
    
    Example:
    --------
    >>> info = get_audio_info(waveform, sr)
    >>> print(f"Duration: {info['duration']:.2f}s")
    """
    info = {
        'duration': len(waveform) / sr,
        'samples': len(waveform),
        'sampling_rate': sr,
        'channels': 1 if waveform.ndim == 1 else waveform.shape[0],
        'max_amplitude': float(np.max(np.abs(waveform))),
        'min_amplitude': float(np.min(waveform)),
        'mean_amplitude': float(np.mean(waveform))
    }
    return info


def resample_audio(waveform, orig_sr, target_sr):
    """
    Resample audio to a different sampling rate.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    orig_sr : int
        Original sampling rate
    target_sr : int
        Target sampling rate
    
    Returns:
    --------
    resampled : numpy.ndarray
        Resampled audio
    
    Example:
    --------
    >>> # Downsample from 44.1kHz to 16kHz
    >>> resampled = resample_audio(waveform, 44100, 16000)
    """
    resampled = librosa.resample(waveform, orig_sr=orig_sr, target_sr=target_sr)
    return resampled


def plot_waveform(waveform, sr, title="Waveform", figsize=(12, 4)):
    """
    Plot the waveform (amplitude vs time) of an audio signal.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    title : str, default="Waveform"
        Plot title
    figsize : tuple, default=(12, 4)
        Figure size (width, height)
    
    Example:
    --------
    >>> waveform, sr = load_audio('speech.wav')
    >>> plot_waveform(waveform, sr, title='My Speech Recording')
    """
    plt.figure(figsize=figsize)
    librosa.display.waveshow(waveform, sr=sr)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Amplitude', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def play_audio(waveform, sr):
    """
    Play audio in Jupyter notebook.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    
    Returns:
    --------
    IPython.display.Audio
        Audio player widget
    
    Example:
    --------
    >>> waveform, sr = load_audio('speech.wav')
    >>> play_audio(waveform, sr)
    """
    return display(Audio(waveform, rate=sr))


def save_audio(filename, waveform, sr):
    """
    Save audio to a file.
    
    Parameters:
    -----------
    filename : str
        Output filename (e.g., 'output.wav')
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    
    Example:
    --------
    >>> # Save processed audio
    >>> save_audio('processed.wav', waveform, sr)
    """
    import soundfile as sf
    sf.write(filename, waveform, sr)
    print(f"✓ Audio saved to '{filename}'")
