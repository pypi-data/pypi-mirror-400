"""
Dataset Utilities for Audio Processing
======================================

Simple functions for loading audio datasets for beginners.
"""

import os
import zipfile
from pathlib import Path
import numpy as np


def load_audio_folder(folder_path, sr=16000, show_index=0):
    """
    Load all audio files from a folder and display selected file analysis.
    
    folder_path : str - Path to folder containing audio files
    sr : int - Sample rate (default: 16000 Hz)
    show_index : int - Which file to display (default: 0 = first file)
    
    Returns: dict with filenames as keys and (audio, sr) as values
    
    Example:
    dataset = load_audio_folder('my_audio_folder')
    dataset = load_audio_folder('vowels', show_index=2)  # Show 3rd file
    """
    import librosa
    import librosa.display
    import matplotlib.pyplot as plt
    
    print(f"Loading audio files from: {folder_path}")
    
    # Find all audio files
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    audio_files = []
    
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in audio_extensions):
            audio_files.append(os.path.join(folder_path, file))
    
    audio_files.sort()  # Sort alphabetically
    
    print(f"Found {len(audio_files)} audio files")
    
    # Load all files
    dataset = {}
    for i, file_path in enumerate(audio_files):
        filename = os.path.basename(file_path)
        audio, file_sr = librosa.load(file_path, sr=sr)
        dataset[filename] = (audio, sr)
        print(f"  [{i}] {filename} - {len(audio)/sr:.2f}s")
    
    # Display selected file
    if len(dataset) > 0 and 0 <= show_index < len(dataset):
        selected_file = list(dataset.keys())[show_index]
        selected_audio, selected_sr = dataset[selected_file]
        duration = len(selected_audio) / sr
        
        print(f"\nDisplaying file [{show_index}]: {selected_file}")
        
        # Create visualization
        fig, axes = plt.subplots(3, 1, figsize=(12, 8))
        
        # Waveform
        time = np.linspace(0, duration, len(selected_audio))
        axes[0].plot(time, selected_audio, color='blue', linewidth=0.5)
        axes[0].set_title(f'Waveform - {selected_file}')
        axes[0].set_xlabel('Time (seconds)')
        axes[0].set_ylabel('Amplitude')
        axes[0].grid(True, alpha=0.3)
        
        # Frequency Spectrum
        fft = np.fft.fft(selected_audio)
        freqs = np.fft.fftfreq(len(fft), 1/sr)
        magnitude = np.abs(fft)
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        axes[1].plot(positive_freqs, positive_magnitude, color='green', linewidth=0.5)
        axes[1].set_title('Frequency Spectrum')
        axes[1].set_xlabel('Frequency (Hz)')
        axes[1].set_ylabel('Magnitude')
        axes[1].set_xlim(0, sr/2)
        axes[1].grid(True, alpha=0.3)
        
        # Spectrogram
        D = librosa.stft(selected_audio)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz', ax=axes[2])
        axes[2].set_title('Spectrogram')
        fig.colorbar(img, ax=axes[2], format='%+2.0f dB')
        
        plt.tight_layout()
        plt.show()
    
    return dataset


def load_audio_from_zip(zip_path, extract_to='extracted_audio', sr=16000, show_index=0):
    """
    Extract ZIP file and load all audio files with index selection.
    
    zip_path : str - Path to ZIP file
    extract_to : str - Folder to extract files (default: 'extracted_audio')
    sr : int - Sample rate (default: 16000 Hz)
    show_index : int - Which file to display (default: 0)
    
    Returns: dict with filenames as keys and (audio, sr) as values
    
    Example:
    dataset = load_audio_from_zip('audio.zip')
    dataset = load_audio_from_zip('vowels.zip', show_index=3)  # Show 4th file
    """
    print(f"Extracting: {zip_path}")
    
    # Extract ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    print(f"Extracted to: {extract_to}")
    
    # Load from extracted folder
    return load_audio_folder(extract_to, sr=sr, show_index=show_index)


def save_synthetic_vowels(output_folder='vowel_dataset', duration=1.0, sr=16000):
    """
    Generate synthetic vowel dataset and save to folder for later loading.
    
    Creates audio files for vowels: a, e, i, o, u
    Useful workflow: generate → save → load → process
    
    output_folder : str - Folder to save audio files (default: 'vowel_dataset')
    duration : float - Duration of each vowel in seconds (default: 1.0)
    sr : int - Sample rate (default: 16000 Hz)
    
    Returns: output_folder path
    
    Example:
    folder = save_synthetic_vowels()
    folder = save_synthetic_vowels('my_vowels', duration=2.0)
    
    Then load:
    dataset = load_audio_folder(folder)
    """
    from scipy.io import wavfile
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Vowel formant frequencies (F1, F2, F3)
    vowels = {
        'a': [730, 1090, 2440],
        'e': [530, 1840, 2480],
        'i': [270, 2290, 3010],
        'o': [570, 840, 2410],
        'u': [300, 870, 2240]
    }
    
    print(f"Generating synthetic vowels in: {output_folder}")
    
    for vowel, formants in vowels.items():
        # Generate time array
        t = np.linspace(0, duration, int(sr * duration))
        
        # Generate vowel sound by adding formant frequencies
        signal = np.zeros(len(t))
        for formant in formants:
            signal += np.sin(2 * np.pi * formant * t)
        
        # Normalize
        signal = signal / np.max(np.abs(signal))
        signal = (signal * 32767).astype(np.int16)
        
        # Save
        filename = os.path.join(output_folder, f'vowel_{vowel}.wav')
        wavfile.write(filename, sr, signal)
        print(f"  Saved: vowel_{vowel}.wav")
    
    print(f"\nGenerated {len(vowels)} vowel files in '{output_folder}'")
    print(f"Load with: load_audio_folder('{output_folder}')")
    
    return output_folder
import librosa
import matplotlib.pyplot as plt


def load_audio_file(file_path, sr=16000):
    """
    Load a single audio file and show waveform, spectrum, and spectrogram.
    
    Perfect for beginners! Just give the file path and see everything.
    
    file_path : str
        Path to audio file (e.g., 'audio.wav' or '/content/audio.wav')
    sr : int
        Sampling rate (default: 16000 Hz)
    
    Returns audio and sampling rate.
    
    Example:
    >>> audio, sr = load_audio_file('my_audio.wav')
    >>> audio, sr = load_audio_file('/content/drive/MyDrive/audio.wav')
    """
    print(f"Loading: {file_path}")
    
    # Load audio
    audio, file_sr = librosa.load(file_path, sr=sr)
    
    # Show info
    print(f"\nAudio Info:")
    print(f"  Duration: {len(audio)/sr:.2f} seconds")
    print(f"  Sampling Rate: {sr} Hz")
    print(f"  Total Samples: {len(audio)}")
    
    # Create plots
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))
    
    # 1. Waveform
    time = np.arange(len(audio)) / sr
    axes[0].plot(time, audio, color='blue', linewidth=0.5)
    axes[0].set_title('Waveform', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Time (seconds)')
    axes[0].set_ylabel('Amplitude')
    axes[0].grid(True, alpha=0.3)
    
    # 2. Spectrum
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    magnitude = np.abs(fft)
    axes[1].plot(freqs, magnitude, color='green', linewidth=1)
    axes[1].set_title('Frequency Spectrum', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Magnitude')
    axes[1].set_xlim(0, 8000)
    axes[1].grid(True, alpha=0.3)
    
    # 3. Spectrogram
    D = librosa.stft(audio, n_fft=512, hop_length=128)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    img = librosa.display.specshow(S_db, sr=sr, hop_length=128, 
                                    x_axis='time', y_axis='hz', ax=axes[2])
    axes[2].set_title('Spectrogram', fontsize=14, fontweight='bold')
    axes[2].set_ylim(0, 8000)
    plt.colorbar(img, ax=axes[2], format='%+2.0f dB')
    
    plt.tight_layout()
    plt.show()
    
    print("\nDone! Audio loaded and visualized.")
    return audio, sr


def load_dataset_from_zip(zip_path, sr=16000):
    """
    Load audio dataset from ZIP file. Super simple for beginners!
    
    Just give ZIP file path, it extracts and loads all audio files.
    
    zip_path : str
        Path to ZIP file (e.g., 'dataset.zip')
    sr : int
        Sampling rate (default: 16000 Hz)
    
    Returns dictionary with audio files.
    
    Example:
    >>> dataset = load_dataset_from_zip('vowels.zip')
    >>> dataset = load_dataset_from_zip('/content/dataset.zip')
    """
    print(f"Loading dataset from: {zip_path}")
    
    # Extract ZIP
    extract_folder = 'extracted_audio'
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print(f"Extracted to: {extract_folder}")
    
    # Find all audio files
    audio_files = []
    for root, dirs, files in os.walk(extract_folder):
        for file in files:
            if file.endswith(('.wav', '.mp3', '.flac')):
                audio_files.append(os.path.join(root, file))
    
    print(f"Found {len(audio_files)} audio files")
    
    # Load first file as preview
    if audio_files:
        print(f"\nShowing preview of first file:")
        first_audio, first_sr = load_audio_file(audio_files[0], sr=sr)
    
    # Return all file paths
    dataset = {'files': audio_files, 'sample_audio': first_audio, 'sr': first_sr}
    return dataset


def load_audio_dataset(
    source,
    sr=None,
    mono=True,
    extract_path='./audio_data',
    auto_detect_split=True,
    file_extensions=('.wav', '.mp3', '.flac', '.ogg', '.m4a'),
    max_files=None,
    verbose=True,
    show_preview=True
):
    """
    Universal audio dataset loader - handles multiple scenarios.
    
    Intelligently loads audio datasets from:
    - ZIP files (auto-extracts)
    - Google Drive URLs (Colab compatible)
    - Local directories
    - Automatically detects train/test splits
    - Handles various folder structures (flat or nested by class)
    
    Parameters:
    -----------
    source : str
        Path to ZIP file, directory, or Google Drive URL
        Examples:
        - '/path/to/dataset.zip'
        - '/path/to/audio_folder'
        - 'https://drive.google.com/uc?id=FILE_ID'
    
    sr : int, optional
        Target sampling rate. If None, keeps original rate
    
    mono : bool, default=True
        Convert to mono if True
    
    extract_path : str, default='./audio_data'
        Where to extract ZIP files
    
    auto_detect_split : bool, default=True
        Automatically detect train/test/val splits
    
    file_extensions : tuple, default=('.wav', '.mp3', '.flac', '.ogg', '.m4a')
        Audio file extensions to load
    
    max_files : int, optional
        Maximum number of files to load per category (for testing)
    
    verbose : bool, default=True
        Print loading progress
    
    show_preview : bool, default=True
        Show visual preview of dataset with sample audio and waveforms
    
    Returns:
    --------
    dataset : dict
        Dictionary with structure:
        {
            'train': {
                'class_A': [(audio1, sr), (audio2, sr), ...],
                'class_B': [(audio1, sr), (audio2, sr), ...],
                ...
            },
            'test': {
                'class_A': [(audio1, sr), (audio2, sr), ...],
                ...
            },
            'metadata': {
                'source': source_path,
                'total_files': int,
                'classes': list,
                'splits': list,
                'sampling_rate': sr
            }
        }
        
        If no train/test split detected, returns:
        {
            'data': {
                'class_A': [(audio1, sr), ...],
                ...
            },
            'metadata': {...}
        }
    
    Example:
    --------
    >>> # Load from ZIP file
    >>> dataset = load_audio_dataset('vowels_dataset.zip')
    >>> print(f"Train classes: {list(dataset['train'].keys())}")
    >>> print(f"Train samples for 'A': {len(dataset['train']['A'])}")
    >>> 
    >>> # Load from directory with train/test
    >>> dataset = load_audio_dataset('/path/to/audio_data')
    >>> audio, sr = dataset['train']['vowel_a'][0]
    >>> 
    >>> # Load from Google Drive (Colab)
    >>> url = 'https://drive.google.com/uc?id=1ABC123...'
    >>> dataset = load_audio_dataset(url, extract_path='/content/audio')
    >>> 
    >>> # Load with specific sampling rate
    >>> dataset = load_audio_dataset('dataset.zip', sr=16000, max_files=10)
    """
    
    # Initialize result structure
    dataset = {'metadata': {}}
    
    # Step 1: Handle source type
    if verbose:
        print(f"Loading dataset from: {source}")
    
    source_path = _prepare_source(source, extract_path, verbose)
    
    # Step 2: Detect dataset structure
    structure = _detect_dataset_structure(source_path, auto_detect_split, verbose)
    
    # Step 3: Load audio files
    if structure['has_split']:
        dataset = _load_split_dataset(
            source_path, structure, sr, mono, 
            file_extensions, max_files, verbose
        )
    else:
        dataset = _load_flat_dataset(
            source_path, structure, sr, mono,
            file_extensions, max_files, verbose
        )
    
    # Step 4: Add metadata
    dataset['metadata'] = {
        'source': str(source_path),
        'total_files': sum(
            len(files) for split in dataset.keys() if split != 'metadata'
            for files in dataset[split].values()
        ),
        'classes': structure['classes'],
        'splits': structure['splits'],
        'sampling_rate': sr if sr else 'original',
        'structure': structure['type']
    }
    
    if verbose:
        print("\nDataset loaded successfully!")
        print(f"   Total files: {dataset['metadata']['total_files']}")
        print(f"   Classes: {len(dataset['metadata']['classes'])}")
        print(f"   Splits: {dataset['metadata']['splits']}")
        
        # Show sample preview if requested
        if show_preview:
            _show_dataset_preview(dataset, sr if sr else None)
    
    return dataset


def _prepare_source(source, extract_path, verbose):
    """Prepare source: download, extract ZIP, or validate directory."""
    
    # Check if Google Drive URL
    if isinstance(source, str) and source.startswith('http'):
        if verbose:
            print("   Downloading from Google Drive...")
        return _download_from_drive(source, extract_path, verbose)
    
    # Check if ZIP file
    source_path = Path(source)
    if source_path.suffix == '.zip':
        if verbose:
            print(f"   Extracting ZIP file...")
        extract_dir = Path(extract_path)
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the main folder (skip __MACOSX and hidden folders)
        extracted_folders = [
            f for f in extract_dir.iterdir() 
            if f.is_dir() and not f.name.startswith('.') and f.name != '__MACOSX'
        ]
        
        if len(extracted_folders) == 1:
            return extracted_folders[0]
        else:
            return extract_dir
    
    # Must be a directory
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source}")
    
    if not source_path.is_dir():
        raise ValueError(f"Source must be a directory or ZIP file: {source}")
    
    return source_path


def _download_from_drive(url, extract_path, verbose):
    """Download file from Google Drive (for Colab)."""
    try:
        import gdown
    except ImportError:
        raise ImportError(
            "gdown is required for Google Drive downloads. "
            "Install with: pip install gdown"
        )
    
    extract_dir = Path(extract_path)
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    # Download to temp file
    output_file = extract_dir / 'dataset.zip'
    gdown.download(url, str(output_file), quiet=not verbose)
    
    # Extract if ZIP
    if output_file.suffix == '.zip':
        if verbose:
            print("   Extracting downloaded file...")
        with zipfile.ZipFile(output_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        output_file.unlink()  # Remove ZIP
        
        # Return extracted folder
        extracted_folders = [
            f for f in extract_dir.iterdir() 
            if f.is_dir() and not f.name.startswith('.')
        ]
        if len(extracted_folders) == 1:
            return extracted_folders[0]
    
    return extract_dir


def _detect_dataset_structure(root_path, auto_detect_split, verbose):
    """Detect if dataset has train/test splits and class folders."""
    
    structure = {
        'has_split': False,
        'splits': [],
        'classes': [],
        'type': 'flat'
    }
    
    root = Path(root_path)
    subdirs = [d for d in root.iterdir() if d.is_dir()]
    subdir_names = [d.name.lower() for d in subdirs]
    
    # Check for train/test/val splits
    split_keywords = ['train', 'test', 'val', 'validation', 'dev']
    found_splits = [name for name in subdir_names if any(kw in name for kw in split_keywords)]
    
    if auto_detect_split and found_splits:
        structure['has_split'] = True
        structure['splits'] = found_splits
        structure['type'] = 'split'
        
        # Detect classes within splits
        first_split = [d for d in subdirs if d.name.lower() in found_splits][0]
        class_dirs = [d.name for d in first_split.iterdir() if d.is_dir()]
        
        if class_dirs:
            structure['classes'] = class_dirs
            structure['type'] = 'split_with_classes'
        else:
            # Classes might be at root level
            structure['classes'] = ['all']
            structure['type'] = 'split_flat'
    
    else:
        # No splits - check if classes are organized in folders
        structure['splits'] = ['data']
        
        # Check if subdirectories contain audio files or more subdirectories
        has_audio_in_root = any(
            f.suffix.lower() in ('.wav', '.mp3', '.flac', '.ogg', '.m4a')
            for f in root.iterdir() if f.is_file()
        )
        
        if subdirs and not has_audio_in_root:
            structure['classes'] = [d.name for d in subdirs]
            structure['type'] = 'classes'
        else:
            structure['classes'] = ['all']
            structure['type'] = 'flat'
    
    if verbose:
        print(f"   Structure: {structure['type']}")
        if structure['has_split']:
            print(f"   Splits detected: {structure['splits']}")
        print(f"   Classes: {len(structure['classes'])} ({', '.join(structure['classes'][:5])}...)" 
              if len(structure['classes']) > 5 
              else f"   Classes: {structure['classes']}")
    
    return structure


def _load_split_dataset(root_path, structure, sr, mono, extensions, max_files, verbose):
    """Load dataset with train/test splits."""
    
    dataset = {}
    root = Path(root_path)
    
    for split_name in structure['splits']:
        split_dir = root / split_name
        if not split_dir.exists():
            continue
        
        if verbose:
            print(f"\nLoading {split_name} split...")
        
        dataset[split_name] = {}
        
        if structure['type'] == 'split_with_classes':
            # Classes organized in folders
            for class_name in structure['classes']:
                class_dir = split_dir / class_name
                if not class_dir.exists():
                    continue
                
                audio_files = _get_audio_files(class_dir, extensions, max_files)
                dataset[split_name][class_name] = _load_audio_files(
                    audio_files, sr, mono, verbose
                )
                
                if verbose:
                    print(f"   {class_name}: {len(dataset[split_name][class_name])} files")
        
        else:
            # Flat structure - all files in split folder
            audio_files = _get_audio_files(split_dir, extensions, max_files)
            dataset[split_name]['all'] = _load_audio_files(
                audio_files, sr, mono, verbose
            )
            
            if verbose:
                print(f"   Loaded {len(dataset[split_name]['all'])} files")
    
    return dataset


def _load_flat_dataset(root_path, structure, sr, mono, extensions, max_files, verbose):
    """Load dataset without train/test splits."""
    
    dataset = {'data': {}}
    root = Path(root_path)
    
    if verbose:
        print(f"\nLoading dataset...")
    
    if structure['type'] == 'classes':
        # Classes in separate folders
        for class_name in structure['classes']:
            class_dir = root / class_name
            if not class_dir.exists():
                continue
            
            audio_files = _get_audio_files(class_dir, extensions, max_files)
            dataset['data'][class_name] = _load_audio_files(
                audio_files, sr, mono, verbose
            )
            
            if verbose:
                print(f"   {class_name}: {len(dataset['data'][class_name])} files")
    
    else:
        # All files in one folder
        audio_files = _get_audio_files(root, extensions, max_files)
        dataset['data']['all'] = _load_audio_files(
            audio_files, sr, mono, verbose
        )
        
        if verbose:
            print(f"   Loaded {len(dataset['data']['all'])} files")
    
    return dataset


def _get_audio_files(directory, extensions, max_files=None):
    """Get list of audio files in directory."""
    
    audio_files = []
    for ext in extensions:
        audio_files.extend(directory.glob(f'*{ext}'))
        audio_files.extend(directory.glob(f'*{ext.upper()}'))
    
    audio_files = sorted(audio_files)
    
    if max_files:
        audio_files = audio_files[:max_files]
    
    return audio_files


def _load_audio_files(file_paths, sr, mono, verbose):
    """Load audio files and return list of (audio, sr) tuples."""
    
    loaded_audio = []
    
    for file_path in file_paths:
        try:
            audio, file_sr = librosa.load(file_path, sr=sr, mono=mono)
            loaded_audio.append((audio, file_sr if sr is None else sr))
        except Exception as e:
            if verbose:
                print(f"   WARNING: Failed to load {file_path.name}: {str(e)}")
    
    return loaded_audio


def generate_vowel_dataset(
    vowels=['A', 'E', 'I', 'O', 'U'],
    n_samples_per_vowel=50,
    f0_range=(100, 250),
    duration_range=(0.5, 1.5),
    sr=16000,
    save_path=None,
    train_test_split=0.8
):
    """
    Generate synthetic vowel dataset for training/testing.
    
    Creates artificial vowel sounds with varying pitch and duration.
    Useful for quick prototyping and testing without real data.
    
    Parameters:
    -----------
    vowels : list, default=['A', 'E', 'I', 'O', 'U']
        Vowels to generate
    
    n_samples_per_vowel : int, default=50
        Number of samples per vowel
    
    f0_range : tuple, default=(100, 250)
        Range of fundamental frequencies (pitch) in Hz
    
    duration_range : tuple, default=(0.5, 1.5)
        Range of durations in seconds
    
    sr : int, default=16000
        Sampling rate
    
    save_path : str, optional
        If provided, saves dataset to this directory
    
    train_test_split : float, default=0.8
        Fraction of data for training (rest for testing)
    
    Returns:
    --------
    dataset : dict
        Dictionary with train/test splits
    
    Example:
    --------
    >>> # Generate dataset
    >>> dataset = generate_vowel_dataset(n_samples_per_vowel=100)
    >>> print(f"Train: {len(dataset['train']['A'])} samples per vowel")
    >>> 
    >>> # Save to disk
    >>> dataset = generate_vowel_dataset(
    ...     n_samples_per_vowel=200,
    ...     save_path='./vowel_dataset'
    ... )
    """
    from .vowel_synthesis import synthesize_vowel
    
    print(f"Generating synthetic vowel dataset...")
    print(f"   Vowels: {vowels}")
    print(f"   Samples per vowel: {n_samples_per_vowel}")
    
    dataset = {'train': {}, 'test': {}, 'metadata': {}}
    n_train = int(n_samples_per_vowel * train_test_split)
    
    for vowel in vowels:
        print(f"   Generating {vowel}...", end=' ')
        
        train_samples = []
        test_samples = []
        
        for i in range(n_samples_per_vowel):
            # Random parameters
            f0 = np.random.uniform(f0_range[0], f0_range[1])
            duration = np.random.uniform(duration_range[0], duration_range[1])
            
            # Generate audio
            audio, file_sr = synthesize_vowel(vowel, f0, duration, sr)
            
            # Split train/test
            if i < n_train:
                train_samples.append((audio, file_sr))
            else:
                test_samples.append((audio, file_sr))
        
        dataset['train'][vowel] = train_samples
        dataset['test'][vowel] = test_samples
        
        print(f"OK (train: {len(train_samples)}, test: {len(test_samples)})")
    
    # Save if requested
    if save_path:
        _save_dataset(dataset, save_path, sr)
    
    # Metadata
    dataset['metadata'] = {
        'vowels': vowels,
        'n_samples_per_vowel': n_samples_per_vowel,
        'f0_range': f0_range,
        'duration_range': duration_range,
        'sampling_rate': sr,
        'train_test_split': train_test_split
    }
    
    print(f"\nDataset generated successfully!")
    print(f"   Total samples: {n_samples_per_vowel * len(vowels)}")
    
    return dataset


def _save_dataset(dataset, save_path, sr):
    """Save generated dataset to disk."""
    
    save_dir = Path(save_path)
    
    for split in ['train', 'test']:
        if split not in dataset:
            continue
        
        split_dir = save_dir / split
        split_dir.mkdir(parents=True, exist_ok=True)
        
        for vowel, samples in dataset[split].items():
            vowel_dir = split_dir / vowel
            vowel_dir.mkdir(exist_ok=True)
            
            for i, (audio, file_sr) in enumerate(samples):
                filename = vowel_dir / f"{vowel}_{i:04d}.wav"
                sf.write(filename, audio, file_sr)
    
    print(f"   Saved to: {save_path}")


def _show_dataset_preview(dataset, sr):
    """Show visual preview of loaded dataset with sample audio."""
    import matplotlib.pyplot as plt
    from IPython.display import Audio, display
    
    print("\n" + "="*60)
    print("DATASET PREVIEW")
    print("="*60)
    
    # Find first split and class with data
    first_split = None
    first_class = None
    sample_audio = None
    sample_sr = None
    
    # Try to get sample from train first, then other splits
    for split_name in ['train', 'test', 'val', 'data']:
        if split_name in dataset and dataset[split_name]:
            first_split = split_name
            # Get first class
            first_class = list(dataset[split_name].keys())[0]
            if dataset[split_name][first_class]:
                sample_audio, sample_sr = dataset[split_name][first_class][0]
                break
    
    if sample_audio is None:
        print("No audio samples found in dataset!")
        return
    
    # Print dataset structure
    print(f"\n1. DATASET STRUCTURE:")
    for split_name in dataset.keys():
        if split_name == 'metadata':
            continue
        print(f"\n   [{split_name.upper()}]")
        for class_name, samples in dataset[split_name].items():
            print(f"      - {class_name}: {len(samples)} samples")
    
    # Show sample info
    print(f"\n2. SAMPLE AUDIO INFO:")
    print(f"   Split: {first_split}")
    print(f"   Class: {first_class}")
    print(f"   Sampling Rate: {sample_sr} Hz")
    print(f"   Duration: {len(sample_audio)/sample_sr:.2f} seconds")
    print(f"   Samples: {len(sample_audio)}")
    print(f"   Shape: {sample_audio.shape}")
    print(f"   Min/Max Amplitude: {sample_audio.min():.3f} / {sample_audio.max():.3f}")
    
    # Plot waveform
    print(f"\n3. WAVEFORM VISUALIZATION:")
    fig, axes = plt.subplots(2, 1, figsize=(12, 6))
    
    # Full waveform
    time = np.arange(len(sample_audio)) / sample_sr
    axes[0].plot(time, sample_audio, color='steelblue', linewidth=0.5)
    axes[0].set_title(f'Sample Waveform: {first_split}/{first_class}', 
                      fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Time (seconds)')
    axes[0].set_ylabel('Amplitude')
    axes[0].grid(True, alpha=0.3)
    
    # Zoomed view (first 0.1 seconds or 10% of signal)
    zoom_samples = min(int(0.1 * sample_sr), len(sample_audio) // 10)
    zoom_time = time[:zoom_samples]
    axes[1].plot(zoom_time, sample_audio[:zoom_samples], color='darkgreen', linewidth=1)
    axes[1].set_title('Zoomed View (first portion)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Time (seconds)')
    axes[1].set_ylabel('Amplitude')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Show one more sample from different class if available
    print(f"\n4. ADDITIONAL SAMPLES:")
    classes = list(dataset[first_split].keys())
    shown = 0
    for class_name in classes[:3]:  # Show up to 3 classes
        if dataset[first_split][class_name]:
            audio, sr_val = dataset[first_split][class_name][0]
            print(f"\n   Class '{class_name}':")
            print(f"      Duration: {len(audio)/sr_val:.2f}s, "
                  f"SR: {sr_val}Hz, "
                  f"Amplitude range: [{audio.min():.3f}, {audio.max():.3f}]")
            
            # Play audio in Jupyter (if available)
            try:
                print(f"      Audio player:")
                display(Audio(audio, rate=sr_val))
                shown += 1
                if shown >= 2:  # Show audio player for max 2 samples
                    break
            except:
                pass  # Not in Jupyter environment
    
    print("\n" + "="*60)
    print("Preview complete! Dataset ready to use.")
    print("="*60 + "\n")
