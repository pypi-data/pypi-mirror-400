"""
Labs 4 & 6: MFCC Feature Extraction
====================================

Functions for extracting Mel-Frequency Cepstral Coefficients (MFCCs),
both using librosa and from scratch implementation.

MFCCs are the most common features for speech recognition and analysis.
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy.fftpack import dct


def extract_mfcc(waveform, sr, n_mfcc=13, n_fft=2048, hop_length=512, n_mels=40):
    """
    Extract MFCC features using librosa (high-level approach).
    
    Mel-Frequency Cepstral Coefficients are standard features for speech processing.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    n_mfcc : int, default=13
        Number of MFCC coefficients to extract
    n_fft : int, default=2048
        FFT window size
    hop_length : int, default=512
        Number of samples between frames
    n_mels : int, default=40
        Number of mel bands
    
    Returns:
    --------
    mfccs : numpy.ndarray
        MFCC features, shape (n_mfcc, time_frames)
    
    Example:
    --------
    >>> mfccs = extract_mfcc(waveform, sr, n_mfcc=13)
    >>> print(f"MFCC shape: {mfccs.shape}")
    """
    mfccs = librosa.feature.mfcc(
        y=waveform, sr=sr, n_mfcc=n_mfcc, 
        n_fft=n_fft, hop_length=hop_length, n_mels=n_mels
    )
    return mfccs


def pre_emphasis(signal, alpha=0.97):
    """
    Apply pre-emphasis filter to boost high frequencies.
    
    Pre-emphasis compensates for high-frequency loss in speech signals.
    Formula: y[t] = x[t] - alpha * x[t-1]
    
    Parameters:
    -----------
    signal : numpy.ndarray
        Input audio signal
    alpha : float, default=0.97
        Pre-emphasis coefficient (typically 0.95-0.97)
    
    Returns:
    --------
    emphasized_signal : numpy.ndarray
        Pre-emphasized signal
    
    Example:
    --------
    >>> emphasized = pre_emphasis(waveform)
    """
    return np.append(signal[0], signal[1:] - alpha * signal[:-1])


def frame_signal(signal, frame_size, frame_stride):
    """
    Divide signal into overlapping frames.
    
    Frames allow analyzing speech as quasi-stationary segments (20-40ms windows).
    
    Parameters:
    -----------
    signal : numpy.ndarray
        Input signal
    frame_size : int
        Number of samples per frame (e.g., 512 for 25ms at 16kHz)
    frame_stride : int
        Number of samples between consecutive frames (e.g., 256 for 10ms stride)
    
    Returns:
    --------
    frames : numpy.ndarray
        Framed signal, shape (num_frames, frame_size)
    
    Example:
    --------
    >>> frames = frame_signal(waveform, frame_size=512, frame_stride=256)
    >>> print(f"Number of frames: {len(frames)}")
    """
    signal_length = len(signal)
    num_frames = int(np.ceil((signal_length - frame_size) / frame_stride)) + 1
    
    # Pad signal if necessary
    pad_length = (num_frames - 1) * frame_stride + frame_size
    padded_signal = np.pad(signal, (0, pad_length - signal_length), mode='constant')
    
    # Create frame indices
    indices = np.arange(0, frame_size).reshape(1, -1) + \
              np.arange(0, num_frames * frame_stride, frame_stride).reshape(-1, 1)
    
    frames = padded_signal[indices]
    return frames


def apply_hamming_window(frames):
    """
    Apply Hamming window to each frame.
    
    Windowing reduces spectral leakage caused by frame boundaries.
    
    Parameters:
    -----------
    frames : numpy.ndarray
        Framed signal, shape (num_frames, frame_size)
    
    Returns:
    --------
    windowed_frames : numpy.ndarray
        Frames with Hamming window applied
    
    Example:
    --------
    >>> windowed = apply_hamming_window(frames)
    """
    frame_size = frames.shape[1]
    hamming = np.hamming(frame_size)
    return frames * hamming


def compute_power_spectrum(frames, n_fft=512):
    """
    Compute power spectrum of framed signal using FFT.
    
    Power spectrum = |FFT|^2, represents energy at each frequency.
    
    Parameters:
    -----------
    frames : numpy.ndarray
        Windowed frames, shape (num_frames, frame_size)
    n_fft : int, default=512
        FFT size
    
    Returns:
    --------
    power_spectrum : numpy.ndarray
        Power spectrum, shape (num_frames, n_fft//2 + 1)
    
    Example:
    --------
    >>> power_spec = compute_power_spectrum(windowed_frames)
    """
    mag_frames = np.absolute(np.fft.rfft(frames, n_fft))
    power_frames = (1.0 / n_fft) * (mag_frames ** 2)
    return power_frames


def hz_to_mel(hz):
    """
    Convert frequency from Hz to mel scale.
    
    Mel scale better approximates human perception of pitch.
    Formula: mel = 2595 * log10(1 + hz/700)
    
    Parameters:
    -----------
    hz : float or numpy.ndarray
        Frequency in Hz
    
    Returns:
    --------
    mel : float or numpy.ndarray
        Frequency in mel
    
    Example:
    --------
    >>> mel_freq = hz_to_mel(1000)
    >>> print(f"1000 Hz = {mel_freq:.1f} mel")
    """
    return 2595 * np.log10(1 + hz / 700.0)


def mel_to_hz(mel):
    """
    Convert frequency from mel scale to Hz.
    
    Inverse of hz_to_mel transformation.
    
    Parameters:
    -----------
    mel : float or numpy.ndarray
        Frequency in mel
    
    Returns:
    --------
    hz : float or numpy.ndarray
        Frequency in Hz
    
    Example:
    --------
    >>> hz_freq = mel_to_hz(1000)
    >>> print(f"1000 mel = {hz_freq:.1f} Hz")
    """
    return 700 * (10**(mel / 2595.0) - 1)


def create_mel_filterbank(n_filters, n_fft, sr, low_freq_mel=0, high_freq_mel=None):
    """
    Create mel-scale filterbank matrix.
    
    Filterbank groups FFT bins into mel-spaced frequency bands.
    Each filter is a triangular window on the mel scale.
    
    Parameters:
    -----------
    n_filters : int
        Number of mel filters (typically 20-40)
    n_fft : int
        FFT size
    sr : int
        Sampling rate
    low_freq_mel : float, default=0
        Lowest mel frequency
    high_freq_mel : float, optional
        Highest mel frequency (defaults to sr/2)
    
    Returns:
    --------
    filterbank : numpy.ndarray
        Mel filterbank matrix, shape (n_filters, n_fft//2 + 1)
    
    Example:
    --------
    >>> mel_fb = create_mel_filterbank(40, 512, 16000)
    >>> print(f"Filterbank shape: {mel_fb.shape}")
    """
    if high_freq_mel is None:
        high_freq_mel = hz_to_mel(sr / 2)
    
    # Create mel-spaced filter center frequencies
    mel_points = np.linspace(low_freq_mel, high_freq_mel, n_filters + 2)
    hz_points = mel_to_hz(mel_points)
    
    # Convert to FFT bin numbers
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)
    
    # Create filterbank
    filterbank = np.zeros((n_filters, n_fft // 2 + 1))
    
    for m in range(1, n_filters + 1):
        f_left = bin_points[m - 1]    # Left edge
        f_center = bin_points[m]       # Center
        f_right = bin_points[m + 1]    # Right edge
        
        # Rising slope
        for k in range(f_left, f_center):
            filterbank[m - 1, k] = (k - f_left) / (f_center - f_left)
        
        # Falling slope
        for k in range(f_center, f_right):
            filterbank[m - 1, k] = (f_right - k) / (f_right - f_center)
    
    return filterbank


def apply_mel_filterbank(power_spectrum, filterbank):
    """
    Apply mel filterbank to power spectrum.
    
    Converts linear frequency power spectrum to mel-frequency representation.
    
    Parameters:
    -----------
    power_spectrum : numpy.ndarray
        Power spectrum, shape (num_frames, n_fft//2 + 1)
    filterbank : numpy.ndarray
        Mel filterbank matrix, shape (n_filters, n_fft//2 + 1)
    
    Returns:
    --------
    mel_spectrum : numpy.ndarray
        Mel-frequency spectrum, shape (num_frames, n_filters)
    
    Example:
    --------
    >>> mel_spec = apply_mel_filterbank(power_spec, mel_fb)
    """
    mel_spectrum = np.dot(power_spectrum, filterbank.T)
    mel_spectrum = np.where(mel_spectrum == 0, np.finfo(float).eps, mel_spectrum)  # Avoid log(0)
    mel_spectrum = 20 * np.log10(mel_spectrum)  # Convert to dB
    return mel_spectrum


def apply_dct(mel_spectrum, n_mfcc=13):
    """
    Apply Discrete Cosine Transform (DCT) to mel spectrum.
    
    DCT decorrelates mel filterbank energies and compresses information.
    Result is the final MFCC features.
    
    Parameters:
    -----------
    mel_spectrum : numpy.ndarray
        Mel-frequency spectrum, shape (num_frames, n_filters)
    n_mfcc : int, default=13
        Number of MFCC coefficients to keep
    
    Returns:
    --------
    mfcc : numpy.ndarray
        MFCC features, shape (num_frames, n_mfcc)
    
    Example:
    --------
    >>> mfccs = apply_dct(mel_spec, n_mfcc=13)
    >>> print(f"MFCCs shape: {mfccs.shape}")
    """
    mfcc = dct(mel_spectrum, type=2, axis=1, norm='ortho')[:, :n_mfcc]
    return mfcc


def extract_mfcc_from_scratch(waveform, sr, n_mfcc=13, n_filters=40, n_fft=512, 
                               frame_size=512, frame_stride=256, alpha=0.97):
    """
    Extract MFCC features from scratch with all manual code inline.
    
    Complete MFCC extraction pipeline with every step implemented manually.
    No helper functions - all code is expanded inline for learning purposes.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    n_mfcc : int, default=13
        Number of MFCC coefficients
    n_filters : int, default=40
        Number of mel filters
    n_fft : int, default=512
        FFT size
    frame_size : int, default=512
        Frame size in samples
    frame_stride : int, default=256
        Frame stride in samples
    alpha : float, default=0.97
        Pre-emphasis coefficient
    
    Returns:
    --------
    mfcc : numpy.ndarray
        MFCC features, shape (num_frames, n_mfcc)
    
    Example:
    --------
    >>> mfccs = extract_mfcc_from_scratch(waveform, sr)
    >>> print(f"Extracted {mfccs.shape[0]} frames with {mfccs.shape[1]} coefficients")
    """
    # STEP 1: PRE-EMPHASIS
    # Boost high frequencies: y[t] = x[t] - alpha * x[t-1]
    emphasized = np.append(waveform[0], waveform[1:] - alpha * waveform[:-1])
    
    # STEP 2: FRAMING
    # Divide signal into overlapping frames
    signal_length = len(emphasized)
    num_frames = int(np.ceil((signal_length - frame_size) / frame_stride)) + 1
    
    # Pad signal if necessary
    pad_length = (num_frames - 1) * frame_stride + frame_size
    padded_signal = np.pad(emphasized, (0, pad_length - signal_length), mode='constant')
    
    # Create frame indices
    indices = np.arange(0, frame_size).reshape(1, -1) + \
              np.arange(0, num_frames * frame_stride, frame_stride).reshape(-1, 1)
    
    frames = padded_signal[indices]
    
    # STEP 3: WINDOWING
    # Apply Hamming window to each frame to reduce spectral leakage
    hamming = np.hamming(frame_size)
    windowed_frames = frames * hamming
    
    # STEP 4: POWER SPECTRUM
    # Compute FFT and power spectrum
    mag_frames = np.absolute(np.fft.rfft(windowed_frames, n_fft))
    power_spectrum = (1.0 / n_fft) * (mag_frames ** 2)
    
    # STEP 5: MEL FILTERBANK
    # Create mel-spaced filterbank
    # Convert Hz to mel: mel = 2595 * log10(1 + hz/700)
    low_freq_mel = 0
    high_freq_mel = 2595 * np.log10(1 + (sr / 2) / 700.0)
    
    # Create mel-spaced filter center frequencies
    mel_points = np.linspace(low_freq_mel, high_freq_mel, n_filters + 2)
    
    # Convert mel back to Hz: hz = 700 * (10^(mel/2595) - 1)
    hz_points = 700 * (10**(mel_points / 2595.0) - 1)
    
    # Convert Hz to FFT bin numbers
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)
    
    # Build triangular filters
    filterbank = np.zeros((n_filters, n_fft // 2 + 1))
    
    for m in range(1, n_filters + 1):
        f_left = bin_points[m - 1]
        f_center = bin_points[m]
        f_right = bin_points[m + 1]
        
        # Rising slope from left to center
        for k in range(f_left, f_center):
            filterbank[m - 1, k] = (k - f_left) / (f_center - f_left)
        
        # Falling slope from center to right
        for k in range(f_center, f_right):
            filterbank[m - 1, k] = (f_right - k) / (f_right - f_center)
    
    # Apply filterbank to power spectrum
    mel_spectrum = np.dot(power_spectrum, filterbank.T)
    
    # Avoid log of zero
    mel_spectrum = np.where(mel_spectrum == 0, np.finfo(float).eps, mel_spectrum)
    
    # Convert to dB
    mel_spectrum = 20 * np.log10(mel_spectrum)
    
    # STEP 6: DISCRETE COSINE TRANSFORM (DCT)
    # Apply DCT to decorrelate mel filterbank energies
    from scipy.fftpack import dct as scipy_dct
    mfcc = scipy_dct(mel_spectrum, type=2, axis=1, norm='ortho')[:, :n_mfcc]
    
    return mfcc


def compare_mfcc_coefficients(waveform, sr, n_mfcc_values=[13, 20, 26]):
    """
    Compare MFCC extraction with different numbers of coefficients.
    
    Visualizes how the number of coefficients affects the representation.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    n_mfcc_values : list, default=[13, 20, 26]
        List of n_mfcc values to compare
    
    Example:
    --------
    >>> compare_mfcc_coefficients(waveform, sr, [13, 20, 26])
    """
    fig, axes = plt.subplots(len(n_mfcc_values), 1, figsize=(12, 4 * len(n_mfcc_values)))
    if len(n_mfcc_values) == 1:
        axes = [axes]
    
    for i, n_mfcc in enumerate(n_mfcc_values):
        mfccs = extract_mfcc(waveform, sr, n_mfcc=n_mfcc)
        
        img = librosa.display.specshow(mfccs, x_axis='time', ax=axes[i])
        axes[i].set_title(f'MFCC (n_mfcc={n_mfcc})', fontsize=14, fontweight='bold')
        axes[i].set_ylabel('MFCC Coefficients', fontsize=12)
        fig.colorbar(img, ax=axes[i])
    
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.tight_layout()
    plt.show()
