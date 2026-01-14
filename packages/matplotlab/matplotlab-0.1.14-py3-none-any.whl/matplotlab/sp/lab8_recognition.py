"""
Lab 8: Speech Recognition Functions
====================================

Rule-based recognition, template matching, and DTW-based speech recognition.
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt
import os


def rule_based_speech_analysis(audio_path):
    """
    Analyze speech using rule-based energy and zero-crossing rate detection.
    
    audio_path : str - Path to audio file
    
    Returns: dict with energy_label, zcr_label, pattern
    
    Example:
    result = rule_based_speech_analysis('speech.wav')
    print(result['pattern'])
    """
    # Load speech signal
    signal, sr = librosa.load(audio_path)
    
    # RULE 1: ENERGY DETECTION
    energy = np.sum(signal**2) / len(signal)
    
    if energy > 0.01:
        energy_label = "Loud Sound Detected"
    else:
        energy_label = "Silent Sound Detected"
    
    # RULE 2: ZERO CROSSING RATE (ZCR)
    zcr = np.mean(librosa.feature.zero_crossing_rate(signal))
    
    if zcr > 0.1:
        zcr_label = "Unvoiced Consonant"
    else:
        zcr_label = "Voiced Sound"
    
    # FINAL RULE-BASED DECISION
    if energy > 0.01 and zcr > 0.1:
        pattern = "CONSONANT HEAVY WORD"
    else:
        pattern = "VOWEL DOMINANT WORD"
    
    # Print results
    print("\n--- RULE BASED SPEECH ANALYSIS ---")
    print(f"Energy: {energy_label} ({energy:.4f})")
    print(f"ZCR: {zcr_label} ({zcr:.4f})")
    print(f"Rule Based Recognized Pattern: {pattern}")
    
    return {
        'energy': energy,
        'energy_label': energy_label,
        'zcr': zcr,
        'zcr_label': zcr_label,
        'pattern': pattern
    }


def template_matching_euclidean(template_folder, test_audio):
    """
    Template matching speech recognition using Euclidean distance.
    
    template_folder : str - Folder containing template WAV files
    test_audio : str - Path to test audio file
    
    Returns: dict with recognized_word and scores
    
    Example:
    result = template_matching_euclidean('templates/', 'test.wav')
    print(result['recognized_word'])
    """
    
    def extract_mfcc(file):
        signal, sr = librosa.load(file)
        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
        return np.mean(mfcc, axis=1)  # Mean MFCC vector
    
    def euclidean_distance(x, y):
        return np.linalg.norm(x - y)
    
    # Load templates
    templates = {}
    for file in os.listdir(template_folder):
        if file.endswith(".wav"):
            word = file.replace(".wav", "")
            path = os.path.join(template_folder, file)
            templates[word] = extract_mfcc(path)
    
    print(f"Templates Loaded: {list(templates.keys())}")
    
    # Load test sample
    test_features = extract_mfcc(test_audio)
    
    # Template matching using Euclidean distance
    scores = {}
    for word in templates:
        dist = euclidean_distance(test_features, templates[word])
        scores[word] = dist
    
    # Recognized word (minimum distance)
    recognized_word = min(scores, key=scores.get)
    
    print("\n--- TEMPLATE MATCHING RESULT ---")
    for key, value in scores.items():
        print(f"{key} → Distance: {value:.2f}")
    print(f"\nRecognized Word: {recognized_word}")
    
    return {
        'recognized_word': recognized_word,
        'scores': scores,
        'templates': list(templates.keys())
    }


def dtw_distance(X, Y):
    """
    Calculate Dynamic Time Warping (DTW) distance between two sequences.
    
    X : numpy array - First sequence (frames × features)
    Y : numpy array - Second sequence (frames × features)
    
    Returns: float - DTW distance
    
    Example:
    distance = dtw_distance(mfcc1, mfcc2)
    """
    n, m = len(X), len(Y)
    dtw = np.zeros((n, m))
    
    for i in range(n):
        for j in range(m):
            cost = np.linalg.norm(X[i] - Y[j])  # Euclidean Distance
            
            if i == 0 and j == 0:
                dtw[i, j] = cost
            elif i == 0:
                dtw[i, j] = cost + dtw[i, j-1]
            elif j == 0:
                dtw[i, j] = cost + dtw[i-1, j]
            else:
                dtw[i, j] = cost + min(
                    dtw[i-1, j],      # vertical
                    dtw[i, j-1],      # horizontal
                    dtw[i-1, j-1]     # diagonal
                )
    
    return dtw[n-1, m-1]


def template_matching_dtw(template_folder, test_audio):
    """
    Template matching speech recognition using DTW (Dynamic Time Warping).
    
    template_folder : str - Folder containing template WAV files
    test_audio : str - Path to test audio file
    
    Returns: dict with recognized_word and scores
    
    Example:
    result = template_matching_dtw('templates/', 'test.wav')
    print(result['recognized_word'])
    """
    
    def extract_mfcc(file):
        signal, sr = librosa.load(file, sr=None)
        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
        return mfcc.T  # Transpose for time sequence (frames × features)
    
    # Load template speech files
    templates = {}
    for file in os.listdir(template_folder):
        if file.endswith(".wav"):
            word = file.replace(".wav", "")
            path = os.path.join(template_folder, file)
            templates[word] = extract_mfcc(path)
    
    print(f"Templates Loaded: {list(templates.keys())}")
    
    # Load test speech file
    test_features = extract_mfcc(test_audio)
    
    # Match test with all templates using DTW
    scores = {}
    for word in templates:
        dist = dtw_distance(test_features, templates[word])
        scores[word] = dist
    
    # Final recognized word (minimum DTW distance)
    recognized_word = min(scores, key=scores.get)
    
    print("\n--- DTW TEMPLATE MATCHING RESULT ---")
    for key, value in scores.items():
        print(f"{key} → DTW Distance: {value:.2f}")
    print(f"\nFINAL RECOGNIZED WORD: {recognized_word}")
    
    return {
        'recognized_word': recognized_word,
        'scores': scores,
        'templates': list(templates.keys())
    }


def extract_speech_features(audio_path, n_mfcc=13):
    """
    Extract MFCC features from speech signal and display visualization.
    
    audio_path : str - Path to audio file
    n_mfcc : int - Number of MFCC coefficients (default: 13)
    
    Returns: numpy array - MFCC features
    
    Example:
    mfcc = extract_speech_features('speech.wav')
    """
    signal, sr = librosa.load(audio_path, sr=None)
    
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=n_mfcc)
    
    plt.figure(figsize=(10, 4))
    plt.imshow(mfcc, aspect='auto', origin='lower')
    plt.title("MFCC Features")
    plt.xlabel("Time Frames")
    plt.ylabel("MFCC Coefficients")
    plt.colorbar(label='Amplitude')
    plt.tight_layout()
    plt.show()
    
    print(f"MFCC shape: {mfcc.shape}")
    print(f"Number of frames: {mfcc.shape[1]}")
    print(f"Number of coefficients: {mfcc.shape[0]}")
    
    return mfcc
