"""
Lab 2: Spectrogram Analysis and Visualization
============================================

Functions for creating and visualizing different types of spectrograms:
- Linear-frequency spectrograms
- Mel-frequency spectrograms
- Narrowband and wideband spectrograms
- Pitch histograms
"""

import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt


def plot_linear_spectrogram(waveform, sr, n_fft=512, hop_length=None, title="Linear Spectrogram", figsize=(12, 6)):
    """
    Plot a linear-frequency spectrogram using STFT (Short-Time Fourier Transform).
    
    Shows how frequency content changes over time with linear frequency scale.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    n_fft : int, default=512
        FFT window size
    hop_length : int, optional
        Number of samples between frames. If None, defaults to n_fft//4
    title : str
        Plot title
    figsize : tuple, default=(12, 6)
        Figure size
    
    Example:
    --------
    >>> waveform, sr = load_audio('speech.wav')
    >>> plot_linear_spectrogram(waveform, sr)
    """
    if hop_length is None:
        hop_length = n_fft // 4
    
    # Compute STFT
    D = librosa.stft(waveform, n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    # Plot
    plt.figure(figsize=figsize)
    librosa.display.specshow(S_db, sr=sr, hop_length=hop_length, x_axis='time', y_axis='hz')
    plt.colorbar(label='Magnitude (dB)', format='%+2.0f dB')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Frequency (Hz)', fontsize=12)
    plt.ylim(0, 8000)  # Limit to human speech range
    plt.tight_layout()
    plt.show()


def plot_mel_spectrogram(waveform, sr, n_mels=64, n_fft=2048, hop_length=512, fmax=8000, title="Mel Spectrogram", figsize=(12, 6)):
    """
    Plot a Mel-frequency spectrogram.
    
    Uses mel scale which better represents human perception of pitch.
    Better for speech and music analysis.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    n_mels : int, default=64
        Number of mel bands
    n_fft : int, default=2048
        FFT window size
    hop_length : int, default=512
        Number of samples between frames
    fmax : float, default=8000
        Maximum frequency
    title : str
        Plot title
    figsize : tuple
        Figure size
    
    Example:
    --------
    >>> plot_mel_spectrogram(waveform, sr, n_mels=80)
    """
    # Compute mel spectrogram
    S_mel = librosa.feature.melspectrogram(
        y=waveform, sr=sr, n_mels=n_mels, n_fft=n_fft, 
        hop_length=hop_length, fmax=fmax
    )
    S_mel_db = librosa.power_to_db(S_mel, ref=np.max)
    
    # Plot
    plt.figure(figsize=figsize)
    img = librosa.display.specshow(S_mel_db, x_axis='time', y_axis='mel', sr=sr, fmax=fmax)
    plt.colorbar(img, label='Power (dB)', format='%+2.0f dB')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Mel Frequency', fontsize=12)
    plt.tight_layout()
    plt.show()


def plot_narrowband_spectrogram(waveform, sr, n_fft=2048, hop_length=512, title="Narrowband Spectrogram", figsize=(12, 6)):
    """
    Plot a narrowband spectrogram (high frequency resolution, low time resolution).
    
    Good for seeing harmonic structure and pitch clearly.
    Uses larger FFT window for better frequency resolution.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    n_fft : int, default=2048
        Large FFT window for narrow bandwidth
    hop_length : int, default=512
        Hop length
    title : str
        Plot title
    figsize : tuple
        Figure size
    
    Example:
    --------
    >>> plot_narrowband_spectrogram(waveform, sr)
    """
    D = librosa.stft(waveform, n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    plt.figure(figsize=figsize)
    librosa.display.specshow(S_db, sr=sr, hop_length=hop_length, x_axis='time', y_axis='hz')
    plt.colorbar(label='Magnitude (dB)', format='%+2.0f dB')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Frequency (Hz)', fontsize=12)
    plt.ylim(0, 8000)
    plt.tight_layout()
    plt.show()


def plot_wideband_spectrogram(waveform, sr, n_fft=256, hop_length=64, title="Wideband Spectrogram", figsize=(12, 6)):
    """
    Plot a wideband spectrogram (low frequency resolution, high time resolution).
    
    Good for seeing temporal details and formant transitions.
    Uses smaller FFT window for better time resolution.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    n_fft : int, default=256
        Small FFT window for wide bandwidth
    hop_length : int, default=64
        Small hop for high time resolution
    title : str
        Plot title
    figsize : tuple
        Figure size
    
    Example:
    --------
    >>> plot_wideband_spectrogram(waveform, sr)
    """
    D = librosa.stft(waveform, n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    plt.figure(figsize=figsize)
    librosa.display.specshow(S_db, sr=sr, hop_length=hop_length, x_axis='time', y_axis='hz')
    plt.colorbar(label='Magnitude (dB)', format='%+2.0f dB')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Frequency (Hz)', fontsize=12)
    plt.ylim(0, 8000)
    plt.tight_layout()
    plt.show()


def plot_pitch_histogram(waveform, sr, title="Pitch Histogram", figsize=(10, 5)):
    """
    Plot histogram of estimated fundamental frequencies (pitch) in the audio.
    
    Shows the distribution of pitch values, useful for analyzing speech patterns.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series
    sr : int
        Sampling rate
    title : str
        Plot title
    figsize : tuple
        Figure size
    
    Returns:
    --------
    pitch_values : numpy.ndarray
        Array of detected pitch frequencies
    
    Example:
    --------
    >>> pitch_values = plot_pitch_histogram(waveform, sr)
    >>> print(f"Mean pitch: {np.mean(pitch_values):.1f} Hz")
    """
    # Extract pitch using librosa's piptrack
    pitches, magnitudes = librosa.piptrack(y=waveform, sr=sr)
    
    # Get pitch values where magnitude is significant
    pitch_values = pitches[magnitudes > np.median(magnitudes)]
    pitch_values = pitch_values[pitch_values > 0]  # Remove zeros
    
    # Plot histogram
    plt.figure(figsize=figsize)
    plt.hist(pitch_values, bins=50, color='teal', alpha=0.7, edgecolor='black')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    return pitch_values


def identify_formants(waveform, sr, n_formants=3, frame_length=0.025, figsize=(12, 8)):
    """
    Identify and visualize formant frequencies in speech signal.
    
    Formants are resonance frequencies of the vocal tract that characterize
    vowel sounds. This function detects peaks in the frequency spectrum.
    
    Parameters:
    -----------
    waveform : numpy.ndarray
        Audio time series (preferably a vowel segment)
    sr : int
        Sampling rate
    n_formants : int, default=3
        Number of formants to identify (typically 3-4 for vowels)
    frame_length : float, default=0.025
        Frame length in seconds for analysis
    figsize : tuple, default=(12, 8)
        Figure size
    
    Returns:
    --------
    formants : dict
        Dictionary with formant frequencies {'F1': freq1, 'F2': freq2, ...}
    
    Example:
    --------
    >>> # Analyze vowel sound
    >>> formants = identify_formants(vowel_segment, sr)
    >>> print(f"F1: {formants['F1']:.0f} Hz, F2: {formants['F2']:.0f} Hz")
    
    >>> # Identify vowel from formants
    >>> if formants['F1'] < 400 and formants['F2'] > 2000:
    >>>     print("Detected vowel: 'I' (as in 'beet')")
    """
    from scipy.signal import find_peaks
    
    # Use middle portion of the signal for stable analysis
    center = len(waveform) // 2
    frame_samples = int(frame_length * sr)
    start = max(0, center - frame_samples // 2)
    end = min(len(waveform), center + frame_samples // 2)
    frame = waveform[start:end]
    
    # Apply window to reduce spectral leakage
    window = np.hamming(len(frame))
    frame_windowed = frame * window
    
    # Compute FFT
    n_fft = max(2048, len(frame_windowed))
    spectrum = np.fft.rfft(frame_windowed, n=n_fft)
    freqs = np.fft.rfftfreq(n_fft, 1/sr)
    magnitude = np.abs(spectrum)
    magnitude_db = 20 * np.log10(magnitude + 1e-10)
    
    # Find peaks in spectrum (potential formants)
    # Focus on speech frequency range (100-4000 Hz)
    freq_mask = (freqs >= 100) & (freqs <= 4000)
    peaks, properties = find_peaks(
        magnitude_db[freq_mask],
        height=-20,
        distance=int(200 / (freqs[1] - freqs[0])),  # At least 200 Hz apart
        prominence=5
    )
    
    # Get formant frequencies
    peak_freqs = freqs[freq_mask][peaks]
    peak_mags = magnitude_db[freq_mask][peaks]
    
    # Sort by frequency and take first n_formants
    sorted_indices = np.argsort(peak_freqs)
    formant_freqs = peak_freqs[sorted_indices][:n_formants]
    formant_mags = peak_mags[sorted_indices][:n_formants]
    
    # Create formants dictionary
    formants = {f'F{i+1}': freq for i, freq in enumerate(formant_freqs)}
    
    # Visualization
    plt.figure(figsize=figsize)
    
    # Plot 1: Waveform
    plt.subplot(3, 1, 1)
    time = np.arange(len(waveform)) / sr
    plt.plot(time, waveform, linewidth=0.5, color='blue')
    plt.axvline(start/sr, color='red', linestyle='--', alpha=0.7, label='Analysis region')
    plt.axvline(end/sr, color='red', linestyle='--', alpha=0.7)
    plt.fill_between([start/sr, end/sr], plt.ylim()[0], plt.ylim()[1], 
                     color='red', alpha=0.1)
    plt.title('Waveform', fontsize=12, fontweight='bold')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Frequency Spectrum
    plt.subplot(3, 1, 2)
    plt.plot(freqs[freq_mask], magnitude_db[freq_mask], linewidth=1.5, color='teal')
    
    # Mark detected formants
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    for i, (freq, mag) in enumerate(zip(formant_freqs, formant_mags)):
        color = colors[i % len(colors)]
        plt.axvline(freq, color=color, linestyle='--', linewidth=2, 
                   label=f'F{i+1} = {freq:.0f} Hz')
        plt.plot(freq, mag, 'o', color=color, markersize=10)
    
    plt.title('Frequency Spectrum with Formants', fontsize=12, fontweight='bold')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.xlim(0, 4000)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Spectrogram with formant overlay
    plt.subplot(3, 1, 3)
    D = librosa.stft(waveform, n_fft=512, hop_length=128)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    librosa.display.specshow(S_db, sr=sr, hop_length=128, x_axis='time', y_axis='hz')
    
    # Draw formant lines
    for i, freq in enumerate(formant_freqs):
        color = colors[i % len(colors)]
        plt.axhline(freq, color=color, linestyle='--', linewidth=2, alpha=0.8,
                   label=f'F{i+1}')
    
    plt.colorbar(format='%+2.0f dB', label='Magnitude (dB)')
    plt.title('Spectrogram with Formants', fontsize=12, fontweight='bold')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim(0, 4000)
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    plt.show()
    
    # Print formant analysis
    print("\nFormant Analysis Results:")
    print("-" * 40)
    for i, freq in enumerate(formant_freqs):
        print(f"F{i+1}: {freq:.0f} Hz")
    
    # Vowel identification based on formants
    if len(formant_freqs) >= 2:
        F1, F2 = formant_freqs[0], formant_freqs[1]
        print("\nEstimated Vowel:")
        print("-" * 40)
        
        if F1 < 400:
            if F2 > 2000:
                print("Likely vowel: 'I' (as in 'beet') - High front vowel")
            elif F2 < 1000:
                print("Likely vowel: 'U' (as in 'boot') - High back vowel")
            else:
                print("Likely vowel: 'E' or 'O' - Mid vowel")
        elif F1 > 600:
            if F2 > 1500:
                print("Likely vowel: 'A' (as in 'bat') - Low front vowel")
            else:
                print("Likely vowel: 'A' (as in 'father') - Low back vowel")
        else:
            print("Likely vowel: Mid-range vowel")
        
        print(f"\nF1/F2 ratio: {F1/F2:.3f}")
    
    return formants
