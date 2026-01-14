"""
Flow Lab Functions for Speech Processing
Complete lab code in single functions
"""

import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
from scipy import signal
from IPython.display import Audio


def flowlab1():
    """Print complete Lab 1 code - Audio Basics"""
    code = '''
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
from IPython.display import Audio

print("Lab 1: Audio Basics - Digital Audio and Waveforms")
print()

filename = 'audio.wav'
waveform, sr = librosa.load(filename, sr=None)

print(f"Sampling Rate: {sr} Hz")
print(f"Duration: {len(waveform) / sr:.2f} seconds")
print(f"Number of samples: {len(waveform)}")
print()

info = {
    'duration': len(waveform) / sr,
    'samples': len(waveform),
    'sampling_rate': sr,
    'max_amplitude': np.max(np.abs(waveform)),
    'min_amplitude': np.min(waveform),
    'mean_amplitude': np.mean(waveform)
}

for key, value in info.items():
    print(f"{key}: {value}")
print()

plt.figure(figsize=(12, 4))
time = np.linspace(0, len(waveform) / sr, len(waveform))
plt.plot(time, waveform, linewidth=0.5)
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.title('Waveform')
plt.grid(True)
plt.show()

target_sr = 16000
resampled = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)
print(f"Resampled from {sr} Hz to {target_sr} Hz")
print(f"New length: {len(resampled)} samples")
print()

Audio(waveform, rate=sr)

sf.write('output.wav', waveform, sr)
print("Saved audio to output.wav")
'''
    print(code)


def flowlab2():
    """Print complete Lab 2 code - Spectrograms"""
    code = '''
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

print("Lab 2: Spectrogram Analysis")
print()

filename = 'audio.wav'
waveform, sr = librosa.load(filename, sr=16000)

print("1. Linear Spectrogram")
D = librosa.stft(waveform, n_fft=512, hop_length=256)
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

plt.figure(figsize=(12, 4))
librosa.display.specshow(S_db, sr=sr, hop_length=256, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('Linear Spectrogram')
plt.ylim(0, 8000)
plt.show()

print("2. Mel Spectrogram")
S_mel = librosa.feature.melspectrogram(y=waveform, sr=sr, n_mels=64)
S_mel_db = librosa.power_to_db(S_mel, ref=np.max)

plt.figure(figsize=(12, 4))
librosa.display.specshow(S_mel_db, x_axis='time', y_axis='mel', sr=sr)
plt.colorbar(format='%+2.0f dB')
plt.title('Mel Spectrogram')
plt.show()

print("3. Narrowband Spectrogram")
D_narrow = librosa.stft(waveform, n_fft=2048, hop_length=512)
S_narrow_db = librosa.amplitude_to_db(np.abs(D_narrow), ref=np.max)

plt.figure(figsize=(12, 4))
librosa.display.specshow(S_narrow_db, sr=sr, hop_length=512, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('Narrowband Spectrogram')
plt.ylim(0, 8000)
plt.show()

print("4. Wideband Spectrogram")
D_wide = librosa.stft(waveform, n_fft=256, hop_length=64)
S_wide_db = librosa.amplitude_to_db(np.abs(D_wide), ref=np.max)

plt.figure(figsize=(12, 4))
librosa.display.specshow(S_wide_db, sr=sr, hop_length=64, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('Wideband Spectrogram')
plt.ylim(0, 8000)
plt.show()

print("5. Pitch Histogram")
pitches, magnitudes = librosa.piptrack(y=waveform, sr=sr)
pitch_values = pitches[magnitudes > np.median(magnitudes)]
pitch_values = pitch_values[pitch_values > 0]

plt.figure(figsize=(10, 5))
plt.hist(pitch_values, bins=50, color='teal', alpha=0.7, edgecolor='black')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Count')
plt.title('Pitch Histogram')
plt.grid(True)
plt.show()

print(f"Mean pitch: {np.mean(pitch_values):.2f} Hz")
'''
    print(code)


def flowlab4():
    """Print complete Lab 4 code - MFCC Features"""
    code = '''
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

print("Lab 4: MFCC Feature Extraction")
print()

filename = 'audio.wav'
waveform, sr = librosa.load(filename, sr=16000)

print("1. Extract MFCC using librosa")
mfcc = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=13, n_fft=2048, hop_length=512)
print(f"MFCC shape: {mfcc.shape}")
print(f"13 coefficients x {mfcc.shape[1]} frames")
print()

plt.figure(figsize=(12, 4))
librosa.display.specshow(mfcc, x_axis='time')
plt.colorbar()
plt.title('MFCC Features')
plt.ylabel('MFCC Coefficients')
plt.show()

print("2. Pre-emphasis")
alpha = 0.97
emphasized = np.append(waveform[0], waveform[1:] - alpha * waveform[:-1])
print(f"Pre-emphasis applied with alpha={alpha}")
print()

print("3. Framing")
frame_size = 512
frame_stride = 256
num_frames = int(np.ceil((len(emphasized) - frame_size) / frame_stride)) + 1
pad_length = (num_frames - 1) * frame_stride + frame_size
padded = np.pad(emphasized, (0, pad_length - len(emphasized)), mode='constant')

indices = np.arange(0, frame_size).reshape(1, -1) + np.arange(0, num_frames * frame_stride, frame_stride).reshape(-1, 1)
frames = padded[indices]
print(f"Number of frames: {len(frames)}")
print()

print("4. Windowing")
hamming = np.hamming(frame_size)
windowed_frames = frames * hamming
print(f"Applied Hamming window")
print()

print("5. Power Spectrum")
mag_frames = np.absolute(np.fft.rfft(windowed_frames, frame_size))
power_frames = (1.0 / frame_size) * (mag_frames ** 2)
print(f"Power spectrum shape: {power_frames.shape}")
print()

print("6. Mel Filterbank")
n_filters = 40
low_freq_mel = 0
high_freq_mel = 2595 * np.log10(1 + (sr / 2) / 700)
mel_points = np.linspace(low_freq_mel, high_freq_mel, n_filters + 2)
hz_points = 700 * (10**(mel_points / 2595) - 1)
bin_points = np.floor((frame_size + 1) * hz_points / sr).astype(int)

filterbank = np.zeros((n_filters, int(frame_size / 2 + 1)))
for m in range(1, n_filters + 1):
    f_left = bin_points[m - 1]
    f_center = bin_points[m]
    f_right = bin_points[m + 1]
    
    for k in range(f_left, f_center):
        filterbank[m - 1, k] = (k - f_left) / (f_center - f_left)
    for k in range(f_center, f_right):
        filterbank[m - 1, k] = (f_right - k) / (f_right - f_center)

print(f"Mel filterbank shape: {filterbank.shape}")
print()

print("7. Apply Filterbank")
mel_spectrum = np.dot(power_frames, filterbank.T)
mel_spectrum = np.where(mel_spectrum == 0, np.finfo(float).eps, mel_spectrum)
mel_spectrum_db = 20 * np.log10(mel_spectrum)
print(f"Mel spectrum shape: {mel_spectrum_db.shape}")
print()

print("8. DCT")
from scipy.fftpack import dct
mfcc_manual = dct(mel_spectrum_db, type=2, axis=1, norm='ortho')[:, :13]
print(f"MFCC shape: {mfcc_manual.shape}")
print()

print("9. Compare different n_mfcc values")
fig, axes = plt.subplots(3, 1, figsize=(12, 8))

for i, n_mfcc in enumerate([13, 20, 26]):
    mfcc_temp = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=n_mfcc)
    librosa.display.specshow(mfcc_temp, x_axis='time', ax=axes[i])
    axes[i].set_title(f'MFCC (n_mfcc={n_mfcc})')
    axes[i].set_ylabel('MFCC Coefficients')
    fig.colorbar(axes[i].images[0], ax=axes[i])

plt.tight_layout()
plt.show()
'''
    print(code)


def flowlab6():
    """Print complete Lab 6 code - MFCC from Scratch"""
    code = '''
import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy.fftpack import dct

print("Lab 6: MFCC from Scratch - Step by Step")
print()

filename = 'audio.wav'
waveform, sr = librosa.load(filename, sr=16000)

print("Step 1: Pre-emphasis")
def pre_emphasis(signal, alpha=0.97):
    return np.append(signal[0], signal[1:] - alpha * signal[:-1])

emphasized = pre_emphasis(waveform)
print(f"Applied pre-emphasis with alpha=0.97")
print()

print("Step 2: Framing")
def frame_signal(signal, frame_size, frame_stride):
    signal_length = len(signal)
    num_frames = int(np.ceil((signal_length - frame_size) / frame_stride)) + 1
    pad_length = (num_frames - 1) * frame_stride + frame_size
    padded_signal = np.pad(signal, (0, pad_length - signal_length), mode='constant')
    
    indices = np.arange(0, frame_size).reshape(1, -1) + np.arange(0, num_frames * frame_stride, frame_stride).reshape(-1, 1)
    frames = padded_signal[indices]
    return frames

frame_size = 512
frame_stride = 256
frames = frame_signal(emphasized, frame_size, frame_stride)
print(f"Created {len(frames)} frames")
print()

print("Step 3: Hamming Window")
def apply_hamming_window(frames):
    frame_size = frames.shape[1]
    hamming = np.hamming(frame_size)
    return frames * hamming

windowed = apply_hamming_window(frames)
print(f"Applied Hamming window to all frames")
print()

print("Step 4: Power Spectrum")
def compute_power_spectrum(frames, n_fft=512):
    mag_frames = np.absolute(np.fft.rfft(frames, n_fft))
    power_frames = (1.0 / n_fft) * (mag_frames ** 2)
    return power_frames

power_spec = compute_power_spectrum(windowed)
print(f"Power spectrum shape: {power_spec.shape}")
print()

print("Step 5: Mel Scale Conversion")
def hz_to_mel(hz):
    return 2595 * np.log10(1 + hz / 700.0)

def mel_to_hz(mel):
    return 700 * (10**(mel / 2595.0) - 1)

print(f"1000 Hz = {hz_to_mel(1000):.2f} mel")
print(f"1000 mel = {mel_to_hz(1000):.2f} Hz")
print()

print("Step 6: Create Mel Filterbank")
def create_mel_filterbank(n_filters, n_fft, sr):
    low_freq_mel = 0
    high_freq_mel = hz_to_mel(sr / 2)
    mel_points = np.linspace(low_freq_mel, high_freq_mel, n_filters + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)
    
    filterbank = np.zeros((n_filters, int(n_fft / 2 + 1)))
    
    for m in range(1, n_filters + 1):
        f_left = bin_points[m - 1]
        f_center = bin_points[m]
        f_right = bin_points[m + 1]
        
        for k in range(f_left, f_center):
            filterbank[m - 1, k] = (k - f_left) / (f_center - f_left)
        for k in range(f_center, f_right):
            filterbank[m - 1, k] = (f_right - k) / (f_right - f_center)
    
    return filterbank

n_filters = 40
mel_fb = create_mel_filterbank(n_filters, frame_size, sr)
print(f"Mel filterbank shape: {mel_fb.shape}")
print()

print("Step 7: Apply Mel Filterbank")
def apply_mel_filterbank(power_spectrum, filterbank):
    mel_spectrum = np.dot(power_spectrum, filterbank.T)
    mel_spectrum = np.where(mel_spectrum == 0, np.finfo(float).eps, mel_spectrum)
    mel_spectrum = 20 * np.log10(mel_spectrum)
    return mel_spectrum

mel_spec = apply_mel_filterbank(power_spec, mel_fb)
print(f"Mel spectrum shape: {mel_spec.shape}")
print()

print("Step 8: DCT")
def apply_dct(mel_spectrum, n_mfcc=13):
    mfcc = dct(mel_spectrum, type=2, axis=1, norm='ortho')[:, :n_mfcc]
    return mfcc

mfcc = apply_dct(mel_spec, n_mfcc=13)
print(f"Final MFCC shape: {mfcc.shape}")
print()

print("Step 9: Visualize Results")
plt.figure(figsize=(12, 10))

plt.subplot(4, 1, 1)
plt.plot(waveform[:1000])
plt.title('Original Signal')
plt.ylabel('Amplitude')

plt.subplot(4, 1, 2)
plt.plot(emphasized[:1000])
plt.title('After Pre-emphasis')
plt.ylabel('Amplitude')

plt.subplot(4, 1, 3)
plt.imshow(mel_spec.T, aspect='auto', origin='lower', cmap='viridis')
plt.colorbar()
plt.title('Mel Spectrum')
plt.ylabel('Mel Filters')

plt.subplot(4, 1, 4)
plt.imshow(mfcc.T, aspect='auto', origin='lower', cmap='viridis')
plt.colorbar()
plt.title('MFCC')
plt.ylabel('Coefficients')

plt.tight_layout()
plt.show()

print("MFCC extraction from scratch complete!")
'''
    print(code)


def flowoel():
    """Print complete OEL code - Vowel Synthesis"""
    code = '''
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from IPython.display import Audio

print("OEL: Vowel Synthesis and Formant Analysis")
print()

print("1. Define Vowel Formants")
vowel_formants = {
    'A': {'F1': 700, 'F2': 1220, 'F3': 2600},
    'E': {'F1': 530, 'F2': 1840, 'F3': 2480},
    'I': {'F1': 270, 'F2': 2290, 'F3': 3010},
    'O': {'F1': 570, 'F2': 840, 'F3': 2410},
    'U': {'F1': 440, 'F2': 1020, 'F3': 2240}
}

for vowel, formants in vowel_formants.items():
    print(f"Vowel {vowel}: F1={formants['F1']} Hz, F2={formants['F2']} Hz, F3={formants['F3']} Hz")
print()

print("2. Synthesize Vowel 'A'")
def synthesize_vowel(f0, F1, F2, F3, duration, sr=16000):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    glottal_pulse = signal.sawtooth(2 * np.pi * f0 * t)
    
    b1, a1 = signal.iirpeak(F1 / (sr / 2), Q=F1 / 50)
    b2, a2 = signal.iirpeak(F2 / (sr / 2), Q=F2 / 70)
    b3, a3 = signal.iirpeak(F3 / (sr / 2), Q=F3 / 100)
    
    vowel = signal.lfilter(b1, a1, glottal_pulse)
    vowel = signal.lfilter(b2, a2, vowel)
    vowel = signal.lfilter(b3, a3, vowel)
    
    vowel = vowel / np.max(np.abs(vowel))
    
    fade_samples = int(0.05 * sr)
    vowel[:fade_samples] *= np.linspace(0, 1, fade_samples)
    vowel[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    return vowel, sr

f0 = 150
vowel_a, sr = synthesize_vowel(f0, 700, 1220, 2600, 0.5)
print(f"Synthesized vowel 'A' with f0={f0} Hz")
print()

print("3. Analyze Vowel")
plt.figure(figsize=(12, 8))

plt.subplot(2, 1, 1)
plt.plot(vowel_a[:int(0.05 * sr)])
plt.title('Waveform (first 50ms)')
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.grid(True)

plt.subplot(2, 1, 2)
D = np.fft.rfft(vowel_a[:1024])
freqs = np.fft.rfftfreq(1024, 1/sr)
magnitude_db = 20 * np.log10(np.abs(D) + 1e-10)
plt.plot(freqs, magnitude_db)
plt.axvline(700, color='r', linestyle='--', label='F1=700 Hz')
plt.axvline(1220, color='g', linestyle='--', label='F2=1220 Hz')
plt.axvline(2600, color='b', linestyle='--', label='F3=2600 Hz')
plt.axvline(f0, color='purple', linestyle=':', label=f'f0={f0} Hz')
plt.title('Frequency Spectrum')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
plt.xlim(0, 3500)
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

print("4. Synthesize All Vowels")
vowels = {}
for vowel_name, formants in vowel_formants.items():
    vowel_sound, _ = synthesize_vowel(150, formants['F1'], formants['F2'], formants['F3'], 0.3)
    vowels[vowel_name] = vowel_sound
    print(f"Synthesized vowel '{vowel_name}'")

print()

print("5. Create Vowel Sequence")
gap = np.zeros(int(0.1 * sr))
sequence = np.concatenate([
    vowels['A'], gap,
    vowels['E'], gap,
    vowels['I'], gap,
    vowels['O'], gap,
    vowels['U']
])

print(f"Created vowel sequence: A-E-I-O-U")
print(f"Total duration: {len(sequence) / sr:.2f} seconds")
print()

print("6. Interactive Vowel Generation")
print("Change f0 and hear different pitches:")

for pitch in [100, 150, 200]:
    vowel_test, _ = synthesize_vowel(pitch, 700, 1220, 2600, 0.3)
    print(f"Vowel 'A' with f0={pitch} Hz")
    Audio(vowel_test, rate=sr)

print()

print("7. Formant Transition (A to I)")
n_steps = 20
F1_start, F1_end = 700, 270
F2_start, F2_end = 1220, 2290
F1_values = np.linspace(F1_start, F1_end, n_steps)
F2_values = np.linspace(F2_start, F2_end, n_steps)

transition = np.array([])
for i in range(n_steps):
    frame, _ = synthesize_vowel(150, F1_values[i], F2_values[i], 2500, 0.025)
    transition = np.concatenate([transition, frame])

print(f"Created smooth transition from 'A' to 'I'")
print(f"Duration: {len(transition) / sr:.2f} seconds")

Audio(transition, rate=sr)

print()
print("OEL Complete!")
'''
    print(code)


def flowquiz1():
    """Print complete Quiz 1 code"""
    code = '''
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

print("Quiz 1: Waveform Segmentation & Spectrogram Analysis")
print()

print("Q1. Waveform Segmentation & Analysis")
print()

filename = 'two_words.wav'
waveform, sr = librosa.load(filename, sr=None)

print("Step 1: Plot first 50 ms")
first_50ms_samples = int(0.05 * sr)
first_50ms = waveform[:first_50ms_samples]
time_50ms = np.linspace(0, 0.05, first_50ms_samples)

plt.figure(figsize=(12, 4))
plt.plot(time_50ms, first_50ms)
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.title('First 50 ms of Audio')
plt.grid(True)
plt.show()

print("Step 2: Normalize amplitude")
max_amplitude = np.max(np.abs(waveform))
normalized_waveform = waveform / max_amplitude
print(f"Normalized to range [-1, 1]")
print()

print("Step 3: Segment into two words")
mid_point = len(normalized_waveform) // 2
word1 = normalized_waveform[:mid_point]
word2 = normalized_waveform[mid_point:]
print(f"Word 1: {len(word1)} samples")
print(f"Word 2: {len(word2)} samples")
print()

print("Step 4: Plot segments and compute energy")
plt.figure(figsize=(12, 8))

plt.subplot(2, 1, 1)
plt.plot(word1)
plt.title('Word 1')
plt.ylabel('Amplitude')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(word2)
plt.title('Word 2')
plt.ylabel('Amplitude')
plt.grid(True)

plt.tight_layout()
plt.show()

energy1 = np.sum(word1 ** 2)
energy2 = np.sum(word2 ** 2)
print(f"Word 1 energy: {energy1:.2f}")
print(f"Word 2 energy: {energy2:.2f}")
print()

print("Step 5: Determine voiced/unvoiced")
zcr1 = np.sum(np.abs(np.diff(np.sign(word1)))) / (2 * len(word1))
zcr2 = np.sum(np.abs(np.diff(np.sign(word2)))) / (2 * len(word2))
print(f"Word 1 ZCR: {zcr1:.6f}")
print(f"Word 2 ZCR: {zcr2:.6f}")

if zcr1 < zcr2:
    print("Word 1: VOICED-DOMINANT")
    print("Word 2: UNVOICED-DOMINANT")
else:
    print("Word 1: UNVOICED-DOMINANT")
    print("Word 2: VOICED-DOMINANT")
print()

print("Q2. Spectrogram Exploration")
print()

print("Compute STFT and Mel spectrograms")
D_stft = librosa.stft(normalized_waveform)
S_stft_db = librosa.amplitude_to_db(np.abs(D_stft), ref=np.max)

S_mel = librosa.feature.melspectrogram(y=normalized_waveform, sr=sr)
S_mel_db = librosa.power_to_db(S_mel, ref=np.max)

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
librosa.display.specshow(S_stft_db, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('STFT Spectrogram')
plt.ylim(50, 8000)

plt.subplot(1, 2, 2)
librosa.display.specshow(S_mel_db, sr=sr, x_axis='time', y_axis='mel')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel-Spectrogram')

plt.tight_layout()
plt.show()

print()
print("Analysis:")
print("Mel-Spectrogram is better for speech recognition because:")
print("1. Matches human auditory perception")
print("2. Focuses on perceptually important frequencies")
print("3. Reduces dimensionality efficiently")
print("4. Standard input for MFCC features")
print()
print("Formants visible as horizontal dark bands at:")
print("F1: 300-1000 Hz, F2: 800-2500 Hz, F3: 2000-3500 Hz")
print()

print("Quiz 1 Complete!")
'''
    print(code)


def flowlab8():
    """Print complete Lab 8 code - Speech Recognition (Rule-based, Template Matching, DTW)"""
    code = '''
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os

print("Lab 8: Speech Recognition - Rule-based, Template Matching, DTW")
print()

# ============================================================================
# TASK 1: RULE-BASED SPEECH RECOGNITION
# ============================================================================
print("TASK 1: RULE-BASED SPEECH ANALYSIS")
print("-" * 60)

audio_path = "speech.wav"
signal, sr = librosa.load(audio_path)

# RULE 1: ENERGY DETECTION
energy = np.sum(signal**2) / len(signal)
energy_label = "Loud Sound Detected" if energy > 0.01 else "Silent Sound Detected"

# RULE 2: ZERO CROSSING RATE (ZCR)
zcr = np.mean(librosa.feature.zero_crossing_rate(signal))
zcr_label = "Unvoiced Consonant" if zcr > 0.1 else "Voiced Sound"

# FINAL RULE-BASED DECISION
if energy > 0.01 and zcr > 0.1:
    pattern = "CONSONANT HEAVY WORD"
else:
    pattern = "VOWEL DOMINANT WORD"

print(f"Energy: {energy_label}")
print(f"ZCR: {zcr_label}")
print(f"Pattern: {pattern}")
print()

# ============================================================================
# TASK 2: TEMPLATE MATCHING (WITHOUT DTW)
# ============================================================================
print("TASK 2: TEMPLATE MATCHING RECOGNITION")
print("-" * 60)

def extract_mfcc(file):
    signal, sr = librosa.load(file)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
    return np.mean(mfcc, axis=1)  # Mean MFCC vector

# Load templates
template_folder = "sounds/"
templates = {}

for file in os.listdir(template_folder):
    if file.endswith(".wav"):
        word = file.replace(".wav", "")
        path = os.path.join(template_folder, file)
        templates[word] = extract_mfcc(path)

# Template matching
test_audio = "sounds/test.wav"
test_features = extract_mfcc(test_audio)

def euclidean_distance(x, y):
    return np.linalg.norm(x - y)

scores = {}
for word in templates:
    dist = euclidean_distance(test_features, templates[word])
    scores[word] = dist

recognized_word = min(scores, key=scores.get)

print("Template Matching Results:")
for word, dist in scores.items():
    print(f"  {word} → Distance: {dist:.2f}")
print(f"Recognized: {recognized_word}")
print()

# ============================================================================
# TASK 3: DTW-BASED TEMPLATE MATCHING
# ============================================================================
print("TASK 3: DTW-BASED TEMPLATE MATCHING")
print("-" * 60)

def extract_mfcc_sequence(file):
    signal, sr = librosa.load(file)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
    return mfcc.T  # Shape: (frames, features)

def dtw_distance(X, Y):
    n, m = len(X), len(Y)
    dtw = np.zeros((n, m))
    
    for i in range(n):
        for j in range(m):
            cost = np.linalg.norm(X[i] - Y[j])
            
            if i == 0 and j == 0:
                dtw[i, j] = cost
            elif i == 0:
                dtw[i, j] = cost + dtw[i, j-1]
            elif j == 0:
                dtw[i, j] = cost + dtw[i-1, j]
            else:
                dtw[i, j] = cost + min(dtw[i-1, j], dtw[i, j-1], dtw[i-1, j-1])
    
    return dtw[n-1, m-1]

# Load templates for DTW
dtw_templates = {}
for file in os.listdir(template_folder):
    if file.endswith(".wav"):
        word = file.replace(".wav", "")
        path = os.path.join(template_folder, file)
        dtw_templates[word] = extract_mfcc_sequence(path)

# DTW Matching
test_features_seq = extract_mfcc_sequence(test_audio)
dtw_scores = {}

for word in dtw_templates:
    dist = dtw_distance(test_features_seq, dtw_templates[word])
    dtw_scores[word] = dist

dtw_recognized = min(dtw_scores, key=dtw_scores.get)

print("DTW Template Matching Results:")
for word, dist in dtw_scores.items():
    print(f"  {word} → DTW Distance: {dist:.2f}")
print(f"Recognized: {dtw_recognized}")
print()

print("Lab 8 Complete!")
'''
    print(code)


def flowlab9():
    """Print complete Lab 9 code - HMM-based Speech Recognition"""
    code = '''
import librosa
import numpy as np
import os
from hmmlearn import hmm

print("Lab 9: HMM-based Speech Recognition")
print()

# ============================================================================
# TASK 1: MFCC FEATURE EXTRACTION
# ============================================================================
print("TASK 1: MFCC FEATURE EXTRACTION")
print("-" * 60)

def extract_mfcc(file):
    signal, sr = librosa.load(file)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
    return mfcc.T  # Shape: (frames, 13)

# Extract from audio
audio_file = "speech.wav"
mfcc_features = extract_mfcc(audio_file)
print(f"MFCC shape: {mfcc_features.shape}")
print(f"Features extracted successfully!")
print()

# ============================================================================
# TASK 2: ORGANIZE DATASET BY WORD
# ============================================================================
print("TASK 2: ORGANIZE DATASET BY WORD")
print("-" * 60)

data_folder = "sounds/"
word_files = {}

for file in os.listdir(data_folder):
    if file.endswith(".wav"):
        word = file.split("-")[0]  # yes-1.wav → yes
        path = os.path.join(data_folder, file)
        
        if word not in word_files:
            word_files[word] = []
        word_files[word].append(path)

print(f"Dataset organized:")
for word, files in word_files.items():
    print(f"  {word}: {len(files)} files")
print()

# ============================================================================
# TASK 3: CREATE AND TRAIN HMM MODELS
# ============================================================================
print("TASK 3: CREATE AND TRAIN HMM MODELS")
print("-" * 60)

hmm_models = {
    "yes": hmm.GaussianHMM(n_components=5, covariance_type="diag", n_iter=100),
    "no":  hmm.GaussianHMM(n_components=5, covariance_type="diag", n_iter=100)
}

def train_hmm_model(model, file_list):
    X = []
    lengths = []
    
    for file in file_list:
        mfcc = extract_mfcc(file)
        X.append(mfcc)
        lengths.append(len(mfcc))
    
    X = np.vstack(X)
    model.fit(X, lengths)
    return model

# Train all models
for word, file_list in word_files.items():
    if word in hmm_models:
        hmm_models[word] = train_hmm_model(hmm_models[word], file_list)
        print(f"Trained HMM for '{word}'")

print()

# ============================================================================
# TASK 4: TEST HMM MODELS
# ============================================================================
print("TASK 4: TEST HMM MODELS")
print("-" * 60)

test_file = "sounds/test_yes.wav"
test_mfcc = extract_mfcc(test_file)

scores = {}
for word, model in hmm_models.items():
    scores[word] = model.score(test_mfcc)

recognized_word = max(scores, key=scores.get)

print("HMM Test Results:")
for word, score in scores.items():
    print(f"  {word} → Score: {score:.2f}")
print(f"Recognized Word: {recognized_word}")
print()

print("Lab 9 Complete!")
'''
    print(code)


def flowlab8():
    """Complete Lab 8: Speech Recognition with Rule-Based & Template Matching"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(8, "Lab 8 code not found")
    print(code)


def flowlab9():
    """Complete Lab 9: HMM-Based Speech Recognition"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(9, "Lab 9 code not found")
    print(code)


def flowlab10():
    """Complete Lab 10: CNN-Based Audio Digit Classification"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(10, "Lab 10 code not found")
    print(code)


def flowlab11():
    """Complete Lab 11: LSTM-Based Audio Processing & Recognition"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(11, "Lab 11 code not found")
    print(code)


def list_sp_labs():
    """List all available SP lab functions"""
    labs = {
        1: "flowlab1() - Audio Basics & Digital Audio",
        2: "flowlab2() - MFCC Features & Spectrograms",
        3: "flowlab3() - Frequency Domain Analysis",
        4: "flowlab4() - Advanced Audio Processing",
        5: "flowlab5() - Audio Classification",
        6: "flowlab6() - Speech Synthesis & TTS",
        7: "flowlab7() - Advanced Speech Recognition",
        8: "flowlab8() - Speech Recognition with Rule-Based & Template Matching",
        9: "flowlab9() - HMM-Based Speech Recognition",
        10: "flowlab10() - CNN-Based Audio Digit Classification",
        11: "flowlab11() - LSTM-Based Audio Processing & Recognition"
    }
    print("\n" + "=" * 80)
    print("AVAILABLE SP LAB FUNCTIONS")
    print("=" * 80)
    for lab_id, description in labs.items():
        print(f"  Lab {lab_id:2}: {description}")
    print("=" * 80 + "\n")
