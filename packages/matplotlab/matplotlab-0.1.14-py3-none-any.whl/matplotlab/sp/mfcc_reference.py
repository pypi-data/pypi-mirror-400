"""
Quick MFCC Reference for Viva Questions
========================================

Fast reference guide for understanding MFCC extraction process with one consistent example.
"""

import numpy as np
import matplotlib.pyplot as plt


def mfcc_viva_guide(show_plots=True):
    """
    Quick MFCC reference guide with bullet points and one example throughout all steps.
    
    Perfect for viva preparation - covers all steps with same example audio.
    
    show_plots : bool - Show visualizations (default: True)
    
    Example:
    mfcc_viva_guide()  # Shows full guide with plots
    mfcc_viva_guide(show_plots=False)  # Just prints info
    """
    
    print("="*70)
    print("MFCC EXTRACTION - COMPLETE VIVA GUIDE")
    print("="*70)
    
    print("\nWHAT IS MFCC?")
    print("-" * 70)
    print("• MFCC = Mel-Frequency Cepstral Coefficients")
    print("• Represents short-term power spectrum of audio")
    print("• Mimics human ear perception of sound")
    print("• Used in speech recognition, speaker identification")
    print("• Captures unique characteristics of speech sounds")
    
    print("\n\nWHY USE MFCC?")
    print("-" * 70)
    print("• Human ear is more sensitive to lower frequencies")
    print("• Mel scale matches human auditory perception")
    print("• Reduces dimensionality while keeping important features")
    print("• Works well for machine learning models")
    print("• Industry standard for speech processing")
    
    print("\n\nEXAMPLE AUDIO:")
    print("-" * 70)
    print("Let's extract MFCC from a 1-second speech sample")
    print("• Sample rate: 16000 Hz")
    print("• Duration: 1 second")
    print("• Total samples: 16000")
    print("• We'll follow this same audio through ALL steps below")
    
    # Generate example audio (simple speech-like signal)
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))
    
    # Simulate speech with multiple frequency components
    audio = np.sin(2 * np.pi * 150 * t)  # F0 (fundamental)
    audio += 0.5 * np.sin(2 * np.pi * 800 * t)  # Formant 1
    audio += 0.3 * np.sin(2 * np.pi * 1200 * t)  # Formant 2
    audio = audio / np.max(np.abs(audio))  # Normalize
    
    print("\n\n" + "="*70)
    print("STEP-BY-STEP MFCC EXTRACTION (USING OUR EXAMPLE)")
    print("="*70)
    
    # STEP 1: Pre-emphasis
    print("\n\nSTEP 1: PRE-EMPHASIS")
    print("-" * 70)
    print("• Purpose: Boost high frequencies")
    print("• Why: Speech has more energy in low frequencies")
    print("• Formula: y[n] = x[n] - 0.97 * x[n-1]")
    print("• Coefficient: Usually 0.95 to 0.97")
    
    pre_coef = 0.97
    pre_audio = np.append(audio[0], audio[1:] - pre_coef * audio[:-1])
    
    print(f"\nOUR EXAMPLE:")
    print(f"  Input: {len(audio)} samples")
    print(f"  Output: {len(pre_audio)} samples")
    print(f"  Before: max amplitude = {np.max(np.abs(audio)):.3f}")
    print(f"  After: max amplitude = {np.max(np.abs(pre_audio)):.3f}")
    
    # STEP 2: Framing
    print("\n\nSTEP 2: FRAMING")
    print("-" * 70)
    print("• Purpose: Divide audio into small overlapping frames")
    print("• Frame length: Usually 20-40 ms (we use 25 ms)")
    print("• Frame step: Usually 10 ms (50% overlap)")
    print("• Why: Speech is quasi-stationary over short periods")
    
    frame_length = int(0.025 * sr)  # 25 ms
    frame_step = int(0.010 * sr)    # 10 ms
    
    num_frames = 1 + (len(pre_audio) - frame_length) // frame_step
    
    print(f"\nOUR EXAMPLE:")
    print(f"  Frame length: 25 ms = {frame_length} samples")
    print(f"  Frame step: 10 ms = {frame_step} samples")
    print(f"  Number of frames: {num_frames}")
    print(f"  Overlap: 50% (common practice)")
    
    frames = []
    for i in range(num_frames):
        start = i * frame_step
        end = start + frame_length
        frame = pre_audio[start:end]
        frames.append(frame)
    frames = np.array(frames)
    
    # STEP 3: Windowing
    print("\n\nSTEP 3: WINDOWING (HAMMING WINDOW)")
    print("-" * 70)
    print("• Purpose: Reduce spectral leakage at frame edges")
    print("• Window type: Hamming window (most common)")
    print("• Formula: w[n] = 0.54 - 0.46 * cos(2πn/(N-1))")
    print("• Why: Smooth frame edges to prevent artifacts in FFT")
    
    hamming = np.hamming(frame_length)
    windowed_frames = frames * hamming
    
    print(f"\nOUR EXAMPLE:")
    print(f"  Applied Hamming window to all {num_frames} frames")
    print(f"  Window shape: {hamming.shape}")
    print(f"  Center value: {hamming[len(hamming)//2]:.3f} (near 1.0)")
    print(f"  Edge value: {hamming[0]:.3f} (near 0.0)")
    
    # STEP 4: FFT (Power Spectrum)
    print("\n\nSTEP 4: FFT & POWER SPECTRUM")
    print("-" * 70)
    print("• Purpose: Convert time domain to frequency domain")
    print("• FFT size: Usually 512 or 1024 points")
    print("• Power spectrum: |FFT|² (magnitude squared)")
    print("• Why: Analyze frequency content of each frame")
    
    nfft = 512
    power_frames = np.abs(np.fft.rfft(windowed_frames, nfft)) ** 2
    
    print(f"\nOUR EXAMPLE:")
    print(f"  FFT size: {nfft} points")
    print(f"  Frequency bins: {power_frames.shape[1]}")
    print(f"  Power spectrum shape: {power_frames.shape}")
    print(f"  Each frame → {power_frames.shape[1]} frequency values")
    
    # STEP 5: Mel Filterbank
    print("\n\nSTEP 5: MEL FILTERBANK")
    print("-" * 70)
    print("• Purpose: Group frequencies like human ear does")
    print("• Mel scale: Mimics human frequency perception")
    print("• Formula: mel = 2595 * log10(1 + f/700)")
    print("• Number of filters: Usually 20-40 (we use 26)")
    print("• Why: Humans perceive frequencies logarithmically")
    
    num_filters = 26
    low_freq = 0
    high_freq = sr / 2
    
    # Convert Hz to Mel
    low_mel = 2595 * np.log10(1 + low_freq / 700)
    high_mel = 2595 * np.log10(1 + high_freq / 700)
    mel_points = np.linspace(low_mel, high_mel, num_filters + 2)
    hz_points = 700 * (10 ** (mel_points / 2595) - 1)
    
    print(f"\nOUR EXAMPLE:")
    print(f"  Number of filters: {num_filters}")
    print(f"  Frequency range: 0 Hz to {high_freq:.0f} Hz")
    print(f"  Mel range: {low_mel:.1f} to {high_mel:.1f}")
    print(f"  Filter shape: Triangular overlapping filters")
    
    # Create filterbank
    bin_points = np.floor((nfft + 1) * hz_points / sr).astype(int)
    filterbank = np.zeros((num_filters, int(nfft / 2 + 1)))
    
    for i in range(1, num_filters + 1):
        left = bin_points[i - 1]
        center = bin_points[i]
        right = bin_points[i + 1]
        
        for j in range(left, center):
            filterbank[i - 1, j] = (j - left) / (center - left)
        for j in range(center, right):
            filterbank[i - 1, j] = (right - j) / (right - center)
    
    # Apply filterbank
    mel_energies = np.dot(power_frames, filterbank.T)
    mel_energies = np.where(mel_energies == 0, np.finfo(float).eps, mel_energies)
    log_mel = np.log(mel_energies)
    
    print(f"  After filterbank: {log_mel.shape}")
    print(f"  Each frame → {num_filters} mel energies")
    
    # STEP 6: DCT
    print("\n\nSTEP 6: DCT (DISCRETE COSINE TRANSFORM)")
    print("-" * 70)
    print("• Purpose: Decorrelate filterbank energies")
    print("• Output: MFCC coefficients")
    print("• Number of coefficients: Usually 12-13 (we use 13)")
    print("• Why: Compress information, reduce correlation")
    print("• First coefficient (C0): Usually discarded (energy term)")
    
    num_ceps = 13
    mfcc = np.zeros((log_mel.shape[0], num_ceps))
    
    for i in range(num_ceps):
        for j in range(num_filters):
            mfcc[:, i] += log_mel[:, j] * np.cos(i * np.pi * (j + 0.5) / num_filters)
    
    print(f"\nOUR EXAMPLE:")
    print(f"  Input: {log_mel.shape} (frames × mel energies)")
    print(f"  Output: {mfcc.shape} (frames × MFCC coefficients)")
    print(f"  We keep first {num_ceps} coefficients")
    print(f"  Final MFCC shape: {mfcc.shape}")
    
    # STEP 7: Final MFCC
    print("\n\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    print(f"\nFinal MFCC matrix: {mfcc.shape}")
    print(f"  {mfcc.shape[0]} frames")
    print(f"  {mfcc.shape[1]} coefficients per frame")
    print(f"\nEach frame represents ~25ms of audio")
    print(f"Total audio duration: {duration}s")
    
    print("\n\nCOMMON VIVA QUESTIONS & ANSWERS:")
    print("="*70)
    
    print("\n1. Why pre-emphasis?")
    print("   → Balance frequency spectrum, boost high frequencies")
    
    print("\n2. Why overlapping frames?")
    print("   → Smooth transitions between frames, no information loss")
    
    print("\n3. Why Hamming window?")
    print("   → Reduce spectral leakage, smooth frame boundaries")
    
    print("\n4. What is Mel scale?")
    print("   → Logarithmic frequency scale matching human hearing")
    
    print("\n5. How many MFCC coefficients?")
    print("   → Usually 12-13, sometimes up to 20")
    
    print("\n6. What does each coefficient mean?")
    print("   → C0: Energy, C1-C2: Low freq, C3+: High freq details")
    
    print("\n7. Why use MFCC over raw audio?")
    print("   → Compact representation, matches human perception, good for ML")
    
    print("\n8. What is cepstrum?")
    print("   → Spectrum of log spectrum (inverse FFT of log power spectrum)")
    
    print("\n9. Difference from spectrogram?")
    print("   → MFCC is compressed, perceptually weighted features")
    
    print("\n10. Real-world applications?")
    print("    → Speech recognition, speaker identification, emotion detection")
    
    # Show plots
    if show_plots:
        fig, axes = plt.subplots(4, 2, figsize=(14, 12))
        
        # Original audio
        axes[0, 0].plot(t, audio)
        axes[0, 0].set_title('1. Original Audio Signal')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Amplitude')
        
        # Pre-emphasized
        axes[0, 1].plot(pre_audio[:1000])
        axes[0, 1].set_title('2. After Pre-emphasis')
        axes[0, 1].set_xlabel('Sample')
        axes[0, 1].set_ylabel('Amplitude')
        
        # Single frame
        axes[1, 0].plot(frames[0])
        axes[1, 0].set_title('3. Single Frame (25ms)')
        axes[1, 0].set_xlabel('Sample')
        axes[1, 0].set_ylabel('Amplitude')
        
        # Hamming window
        axes[1, 1].plot(hamming)
        axes[1, 1].set_title('4. Hamming Window')
        axes[1, 1].set_xlabel('Sample')
        axes[1, 1].set_ylabel('Amplitude')
        
        # Windowed frame
        axes[2, 0].plot(windowed_frames[0])
        axes[2, 0].set_title('5. Windowed Frame')
        axes[2, 0].set_xlabel('Sample')
        axes[2, 0].set_ylabel('Amplitude')
        
        # Power spectrum
        axes[2, 1].plot(power_frames[0])
        axes[2, 1].set_title('6. Power Spectrum')
        axes[2, 1].set_xlabel('Frequency Bin')
        axes[2, 1].set_ylabel('Power')
        
        # Mel filterbank
        axes[3, 0].imshow(filterbank, aspect='auto', origin='lower')
        axes[3, 0].set_title('7. Mel Filterbank (26 filters)')
        axes[3, 0].set_xlabel('Frequency Bin')
        axes[3, 0].set_ylabel('Filter Number')
        
        # Final MFCC
        axes[3, 1].imshow(mfcc.T, aspect='auto', origin='lower', cmap='viridis')
        axes[3, 1].set_title('8. Final MFCC Features')
        axes[3, 1].set_xlabel('Frame Number')
        axes[3, 1].set_ylabel('MFCC Coefficient')
        
        plt.tight_layout()
        plt.show()
        
        print("\n\nPLOTS EXPLANATION:")
        print("-" * 70)
        print("Plot 1: Original audio waveform (time domain)")
        print("Plot 2: After pre-emphasis (high freq boosted)")
        print("Plot 3: One frame of 25ms (400 samples)")
        print("Plot 4: Hamming window shape")
        print("Plot 5: Frame after applying window")
        print("Plot 6: Power spectrum of one frame")
        print("Plot 7: Mel filterbank (26 triangular filters)")
        print("Plot 8: Final MFCC matrix (13 coefficients × frames)")
    
    print("\n" + "="*70)
    print("Quick reference complete! Good luck with your viva!")
    print("="*70)
    
    return mfcc


def mfcc_cheatsheet():
    """
    Super quick MFCC cheatsheet - just the key points.
    
    Example:
    mfcc_cheatsheet()
    """
    print("="*70)
    print("MFCC CHEATSHEET - QUICK REFERENCE")
    print("="*70)
    
    print("\nDEFINITION:")
    print("  MFCC = Mel-Frequency Cepstral Coefficients")
    print("  Compact representation of audio's frequency content")
    
    print("\n7 STEPS:")
    print("  1. Pre-emphasis     → Boost high frequencies (0.97)")
    print("  2. Framing          → 25ms frames, 10ms step")
    print("  3. Windowing        → Hamming window")
    print("  4. FFT              → Power spectrum (512/1024 points)")
    print("  5. Mel Filterbank   → 26 triangular filters")
    print("  6. Log              → Log of mel energies")
    print("  7. DCT              → 13 MFCC coefficients")
    
    print("\nKEY FORMULAS:")
    print("  Pre-emphasis:  y[n] = x[n] - 0.97*x[n-1]")
    print("  Mel scale:     m = 2595 * log10(1 + f/700)")
    print("  Hamming:       w[n] = 0.54 - 0.46*cos(2πn/N)")
    
    print("\nTYPICAL VALUES:")
    print("  Frame length:    25 ms (400 samples @ 16kHz)")
    print("  Frame step:      10 ms (50% overlap)")
    print("  FFT size:        512 or 1024")
    print("  Mel filters:     26 or 40")
    print("  MFCC coeffs:     13 (C0-C12)")
    
    print("\nWHY EACH STEP:")
    print("  Pre-emphasis:    Balance spectrum")
    print("  Framing:         Stationary analysis")
    print("  Windowing:       Reduce leakage")
    print("  FFT:             Time → Frequency")
    print("  Mel:             Match human ear")
    print("  Log:             Match loudness perception")
    print("  DCT:             Decorrelate features")
    
    print("\nVIVA TIPS:")
    print("  • First coefficient C0 = energy (sometimes discarded)")
    print("  • Lower coeffs = envelope, higher coeffs = details")
    print("  • Used in speech recognition, speaker ID")
    print("  • Better than raw audio for ML models")
    print("  • Mel scale = how humans hear frequencies")
    
    print("\n" + "="*70)
