"""
Complex OEL Graph - Advanced Vowel Spectrum Analysis
====================================================

Detailed frequency spectrum analysis with formants and harmonics visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import get_window, find_peaks


def complex_oel_graph(file_path, f0_guess=120, duration_ms=50):
    """
    Calculates and plots the frequency spectrum of a vowel from a WAV file.
    Shows formants (F1, F2, F3) and harmonics for detailed vowel analysis.
    
    file_path : str - Path to the WAV audio file
    f0_guess : int - Assumed fundamental frequency in Hz (default: 120)
    duration_ms : int - Audio segment duration in milliseconds (default: 50)
    
    Example:
    complex_oel_graph('vowel_a.wav')
    complex_oel_graph('speech.wav', f0_guess=150, duration_ms=100)
    """
    
    # 1. Load Audio and Prepare Segment
    # Read the file to get the sampling rate (fs) and the audio data
    fs, audio_data = wavfile.read(file_path)

    # Convert to single channel (mono) and normalize the volume
    if audio_data.ndim > 1:
        audio_data = audio_data[:, 0]
    audio_data = audio_data / np.max(np.abs(audio_data))

    # Take a short segment (e.g., 50ms) for clear analysis
    segment_length = int((duration_ms / 1000.0) * fs)
    segment = audio_data[:segment_length]

    # Apply a Hanning window to prepare the segment for FFT
    window = get_window('hann', segment_length)
    windowed_segment = segment * window

    # 2. Calculate Spectrum (FFT)
    # Perform the Fast Fourier Transform
    fft_result = np.fft.fft(windowed_segment)
    
    # Get magnitude and corresponding frequencies (only the first half)
    half_length = segment_length // 2
    magnitude = np.abs(fft_result[:half_length])
    frequencies = np.fft.fftfreq(segment_length, d=1/fs)[:half_length]

    # Convert magnitude to Decibels (dB) for a standard spectrum plot
    db_spectrum = 20 * np.log10(magnitude + 1e-6)

    # 3. Estimate Formants (The major peaks F1, F2, F3)
    # Find peaks above a certain height and distance apart
    peak_indices, _ = find_peaks(db_spectrum, height=8, distance=100)
    
    # Filter for the speech range (< 4000 Hz) and find the top 3 strongest peaks
    speech_range_indices = frequencies[peak_indices] < 4000
    formant_indices = peak_indices[speech_range_indices]
    top_3_indices = formant_indices[np.argsort(db_spectrum[formant_indices])[-3:]]
    estimated_formants = np.sort(frequencies[top_3_indices])

    # 4. Estimate Harmonics (Multiples of the fundamental frequency F0)
    harmonic_frequencies = np.arange(f0_guess, 4000, f0_guess)

    # 5. Create the Plot
    plt.figure(figsize=(10, 5))
    
    # Plot the main spectrum curve
    plt.plot(frequencies, db_spectrum, color='purple', linewidth=1.5, alpha=0.8)
    
    # Plot vertical lines and labels for the Formants (red dashed)
    formant_labels = [f"F{i+1}" for i in range(len(estimated_formants))]
    for i, f_freq in enumerate(estimated_formants):
        plt.axvline(f_freq, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        plt.text(f_freq + 30, 20, f"{formant_labels[i]}={f_freq:.0f}Hz", color='red', fontsize=10)

    # Plot vertical lines for the Harmonics (gray dotted)
    for h_freq in harmonic_frequencies:
        plt.axvline(h_freq, color='gray', linestyle=':', linewidth=0.5, alpha=0.5)

    # Set up the plot details
    plt.title('Vowel Frequency Spectrum', fontsize=14)
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Magnitude (dB)', fontsize=12)
    plt.xlim(0, 4000) 
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    
    plt.show()
    
    # Print formant information
    print("\nFormant Frequencies Detected:")
    for i, f_freq in enumerate(estimated_formants):
        print(f"  F{i+1}: {f_freq:.1f} Hz")
    
    print(f"\nFundamental Frequency (F0): {f0_guess} Hz (assumed)")
    print(f"Harmonics shown at multiples of F0: {f0_guess}, {f0_guess*2}, {f0_guess*3}, ...")
