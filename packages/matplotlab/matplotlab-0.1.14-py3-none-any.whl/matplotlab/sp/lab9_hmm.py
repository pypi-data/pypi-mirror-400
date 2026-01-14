"""
Lab 9: Hidden Markov Model (HMM) Speech Recognition
===================================================

HMM-based speech recognition with training and testing functions.
"""

import numpy as np
import librosa
import os


def extract_mfcc_sequence(file_path, n_mfcc=13):
    """
    Extract MFCC feature sequence from audio file.
    
    file_path : str - Path to audio file
    n_mfcc : int - Number of MFCC coefficients (default: 13)
    
    Returns: numpy array - MFCC features (frames × coefficients)
    
    Example:
    mfcc = extract_mfcc_sequence('speech.wav')
    """
    signal, sr = librosa.load(file_path)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=n_mfcc)
    return mfcc.T  # Shape: (frames, n_mfcc)


def organize_dataset_by_word(data_folder):
    """
    Auto-separate audio files by word label (filename pattern: word-number.wav).
    
    data_folder : str - Folder containing audio files
    
    Returns: dict - {word: [file_paths]}
    
    Example:
    word_files = organize_dataset_by_word('sounds/')
    # Returns: {'yes': ['yes-1.wav', 'yes-2.wav'], 'no': ['no-1.wav', ...]}
    """
    word_files = {}
    
    for file in os.listdir(data_folder):
        if file.endswith(".wav"):
            word = file.split("-")[0]  # yes-1.wav → yes
            path = os.path.join(data_folder, file)
            
            if word not in word_files:
                word_files[word] = []
            word_files[word].append(path)
    
    print("✅ Detected Dataset:")
    for word, files in word_files.items():
        print(f"  {word}: {len(files)} files")
    
    return word_files


def train_hmm_model(file_list, n_components=5, n_mfcc=13):
    """
    Train HMM model from list of audio files.
    
    Note: Requires hmmlearn package (pip install hmmlearn)
    
    file_list : list - List of audio file paths for training
    n_components : int - Number of HMM states (default: 5)
    n_mfcc : int - Number of MFCC features (default: 13)
    
    Returns: trained HMM model
    
    Example:
    model = train_hmm_model(['yes-1.wav', 'yes-2.wav', 'yes-3.wav'])
    """
    try:
        from hmmlearn import hmm
    except ImportError:
        print("ERROR: hmmlearn not installed!")
        print("Install with: pip install hmmlearn")
        return None
    
    X = []
    lengths = []
    
    for file in file_list:
        mfcc = extract_mfcc_sequence(file, n_mfcc=n_mfcc)
        X.append(mfcc)
        lengths.append(len(mfcc))
    
    X = np.vstack(X)  # Stack all MFCC into single matrix
    
    model = hmm.GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=100)
    model.fit(X, lengths)
    
    return model


def train_hmm_models(word_files, n_components=5, n_mfcc=13):
    """
    Train HMM models for multiple words.
    
    word_files : dict - {word: [file_paths]}
    n_components : int - Number of HMM states (default: 5)
    n_mfcc : int - Number of MFCC features (default: 13)
    
    Returns: dict - {word: trained_model}
    
    Example:
    word_files = organize_dataset_by_word('sounds/')
    models = train_hmm_models(word_files)
    """
    try:
        from hmmlearn import hmm
    except ImportError:
        print("ERROR: hmmlearn not installed!")
        print("Install with: pip install hmmlearn")
        return {}
    
    hmm_models = {}
    
    for word, file_list in word_files.items():
        print(f"Training HMM for '{word}'...")
        model = train_hmm_model(file_list, n_components, n_mfcc)
        hmm_models[word] = model
    
    print("✅ HMM Training Completed")
    print(f"Trained models: {list(hmm_models.keys())}")
    
    return hmm_models


def test_hmm_recognition(hmm_models, test_file, n_mfcc=13):
    """
    Test HMM models on unknown speech and recognize the word.
    
    hmm_models : dict - {word: trained_model}
    test_file : str - Path to test audio file
    n_mfcc : int - Number of MFCC features (default: 13)
    
    Returns: dict with recognized_word and scores
    
    Example:
    result = test_hmm_recognition(models, 'test.wav')
    print(result['recognized_word'])
    """
    test_features = extract_mfcc_sequence(test_file, n_mfcc=n_mfcc)
    
    scores = {}
    
    # Loop through all trained HMM models
    for word, model in hmm_models.items():
        scores[word] = model.score(test_features)
    
    # Recognized word (maximum score)
    recognized_word = max(scores, key=scores.get)
    
    print("\n--- HMM TEST RESULT ---")
    for w, s in scores.items():
        print(f"{w} → Score: {s:.2f}")
    print(f"\nRecognized Word: {recognized_word}")
    
    return {
        'recognized_word': recognized_word,
        'scores': scores
    }


def complete_hmm_workflow(train_folder, test_file, n_components=5, n_mfcc=13):
    """
    Complete HMM speech recognition workflow: organize → train → test.
    
    train_folder : str - Folder with training audio files (word-number.wav format)
    test_file : str - Path to test audio file
    n_components : int - Number of HMM states (default: 5)
    n_mfcc : int - Number of MFCC features (default: 13)
    
    Returns: dict with recognized_word and all results
    
    Example:
    result = complete_hmm_workflow('train_sounds/', 'test.wav')
    print(f"Recognized: {result['recognized_word']}")
    """
    print("="*60)
    print("STEP 1: ORGANIZING DATASET")
    print("="*60)
    word_files = organize_dataset_by_word(train_folder)
    
    print("\n" + "="*60)
    print("STEP 2: TRAINING HMM MODELS")
    print("="*60)
    hmm_models = train_hmm_models(word_files, n_components, n_mfcc)
    
    print("\n" + "="*60)
    print("STEP 3: TESTING ON UNKNOWN SPEECH")
    print("="*60)
    result = test_hmm_recognition(hmm_models, test_file, n_mfcc)
    
    return {
        'recognized_word': result['recognized_word'],
        'scores': result['scores'],
        'word_files': word_files,
        'models': list(hmm_models.keys())
    }
