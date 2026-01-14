"""
OEL: Vowel Synthesis and Analysis
==================================

Functions for synthesizing vowels using formant frequencies
and analyzing vowel characteristics.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from IPython.display import Audio


# Standard formant frequencies for vowels (F1, F2 in Hz)
VOWEL_FORMANTS = {
    'A': {'F1': 700, 'F2': 1220, 'name': 'A as in "father"'},
    'E': {'F1': 530, 'F2': 1840, 'name': 'E as in "bed"'},
    'I': {'F1': 270, 'F2': 2290, 'name': 'I as in "see"'},
    'O': {'F1': 570, 'F2': 840, 'name': 'O as in "law"'},
    'U': {'F1': 440, 'F2': 1020, 'name': 'U as in "too"'}
}


def synthesize_vowel(vowel='A', f0=150, duration=1.0, sr=16000):
    """
    Synthesize a vowel sound using formant synthesis.
    
    Creates vowel by filtering a glottal pulse train through formant resonances.
    
    Parameters:
    -----------
    vowel : str, default='A'
        Vowel to synthesize: 'A', 'E', 'I', 'O', or 'U'
    f0 : float, default=150
        Fundamental frequency (pitch) in Hz
        Typical ranges: Male 85-180 Hz, Female 165-255 Hz
    duration : float, default=1.0
        Duration in seconds
    sr : int, default=16000
        Sampling rate
    
    Returns:
    --------
    audio : numpy.ndarray
        Synthesized vowel waveform
    sr : int
        Sampling rate
    
    Example:
    --------
    >>> audio, sr = synthesize_vowel('A', f0=150, duration=1.0)
    >>> play_audio(audio, sr)
    """
    if vowel not in VOWEL_FORMANTS:
        raise ValueError(f"Vowel must be one of {list(VOWEL_FORMANTS.keys())}")
    
    # Get formant frequencies
    F1 = VOWEL_FORMANTS[vowel]['F1']
    F2 = VOWEL_FORMANTS[vowel]['F2']
    
    # Generate time array
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Generate glottal pulse train (sawtooth wave approximation)
    glottal_source = signal.sawtooth(2 * np.pi * f0 * t)
    
    # Create formant filters (resonant bandpass filters)
    # F1 filter
    bandwidth1 = 50  # Hz
    b1, a1 = signal.iirpeak(F1 / (sr / 2), Q=F1 / bandwidth1)
    
    # F2 filter
    bandwidth2 = 70  # Hz
    b2, a2 = signal.iirpeak(F2 / (sr / 2), Q=F2 / bandwidth2)
    
    # Apply formant filters
    audio = signal.lfilter(b1, a1, glottal_source)
    audio = signal.lfilter(b2, a2, audio)
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # Apply envelope (fade in/out)
    fade_samples = int(0.05 * sr)  # 50ms fade
    envelope = np.ones_like(audio)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    audio *= envelope
    
    return audio, sr


def get_vowel_formants(vowel=None):
    """
    Get formant frequencies for specified vowel(s).
    
    Returns dictionary with F1 and F2 frequencies.
    
    Parameters:
    -----------
    vowel : str or None
        Specific vowel ('A', 'E', 'I', 'O', 'U') or None for all vowels
    
    Returns:
    --------
    formants : dict
        Dictionary with formant information
    
    Example:
    --------
    >>> formants = get_vowel_formants('A')
    >>> print(f"Vowel A: F1={formants['F1']} Hz, F2={formants['F2']} Hz")
    >>> 
    >>> all_vowels = get_vowel_formants()
    >>> for v, f in all_vowels.items():
    ...     print(f"{v}: F1={f['F1']} Hz, F2={f['F2']} Hz")
    """
    if vowel is None:
        return VOWEL_FORMANTS.copy()
    
    if vowel not in VOWEL_FORMANTS:
        raise ValueError(f"Vowel must be one of {list(VOWEL_FORMANTS.keys())}")
    
    return VOWEL_FORMANTS[vowel].copy()


def plot_vowel_analysis(vowel='A', f0=150, duration=1.0, sr=16000):
    """
    Synthesize vowel and plot waveform, spectrum, and formant locations.
    
    Comprehensive visualization showing time-domain and frequency-domain representations.
    
    Parameters:
    -----------
    vowel : str, default='A'
        Vowel to analyze
    f0 : float, default=150
        Fundamental frequency in Hz
    duration : float, default=1.0
        Duration in seconds
    sr : int, default=16000
        Sampling rate
    
    Example:
    --------
    >>> plot_vowel_analysis('E', f0=200)
    """
    # Synthesize vowel
    audio, _ = synthesize_vowel(vowel, f0, duration, sr)
    
    # Get formants
    formants = get_vowel_formants(vowel)
    F1, F2 = formants['F1'], formants['F2']
    
    # Compute spectrum
    n_fft = 2048
    spectrum = np.fft.rfft(audio[:sr], n=n_fft)  # Use first second
    freqs = np.fft.rfftfreq(n_fft, 1/sr)
    magnitude = np.abs(spectrum)
    magnitude_db = 20 * np.log10(magnitude + 1e-10)
    
    # Create subplots
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot waveform
    t = np.linspace(0, duration, len(audio))
    axes[0].plot(t[:int(0.05*sr)], audio[:int(0.05*sr)], color='darkblue', linewidth=1.5)
    axes[0].set_title(f'Vowel {vowel} - Waveform (first 50ms)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Time (seconds)', fontsize=12)
    axes[0].set_ylabel('Amplitude', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    
    # Plot spectrum with formants
    axes[1].plot(freqs, magnitude_db, color='teal', linewidth=1.5, label='Spectrum')
    axes[1].axvline(F1, color='red', linestyle='--', linewidth=2, label=f'F1 = {F1} Hz')
    axes[1].axvline(F2, color='orange', linestyle='--', linewidth=2, label=f'F2 = {F2} Hz')
    axes[1].axvline(f0, color='purple', linestyle=':', linewidth=1.5, label=f'f0 = {f0} Hz')
    axes[1].set_title(f'Vowel {vowel} - Frequency Spectrum', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Frequency (Hz)', fontsize=12)
    axes[1].set_ylabel('Magnitude (dB)', fontsize=12)
    axes[1].set_xlim(0, 3500)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print info
    print(f"\n{formants['name']}")
    print(f"Fundamental Frequency (f0): {f0} Hz")
    print(f"First Formant (F1): {F1} Hz")
    print(f"Second Formant (F2): {F2} Hz")


def play_vowel_interactive(vowel='A', f0=150):
    """
    Synthesize and play vowel sound interactively in Jupyter.
    
    Best used with ipywidgets for interactive vowel exploration.
    
    Parameters:
    -----------
    vowel : str, default='A'
        Vowel to synthesize
    f0 : float, default=150
        Fundamental frequency in Hz
    
    Returns:
    --------
    audio_widget : IPython.display.Audio
        Audio player widget
    
    Example:
    --------
    >>> # Basic usage
    >>> play_vowel_interactive('A', f0=150)
    >>> 
    >>> # Interactive with ipywidgets
    >>> from ipywidgets import interact
    >>> def play_vowel(vowel, pitch):
    ...     return play_vowel_interactive(vowel, pitch)
    >>> 
    >>> interact(play_vowel, 
    ...          vowel=['A', 'E', 'I', 'O', 'U'],
    ...          pitch=(80, 300, 10))
    """
    # Synthesize vowel
    audio, sr = synthesize_vowel(vowel, f0, duration=0.8)
    
    # Get vowel info
    formants = get_vowel_formants(vowel)
    
    # Display info
    print(f"Vowel: {vowel} - {formants['name']}")
    print(f"Pitch (f0): {f0} Hz")
    print(f"F1: {formants['F1']} Hz, F2: {formants['F2']} Hz")
    
    # Return audio widget
    return Audio(audio, rate=sr, autoplay=True)
