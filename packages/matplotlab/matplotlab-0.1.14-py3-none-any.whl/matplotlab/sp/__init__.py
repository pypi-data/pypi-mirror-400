"""
Speech Processing Module for matplotlab
========================================

This module provides functions for audio signal processing, feature extraction,
and speech analysis covering Labs 1-6 and OEL.

Labs Coverage:
- Lab 1: Digital Audio and Waveform Visualization
- Lab 2: Spectrograms and Pitch Analysis
- Lab 4: MFCC Feature Extraction
- Lab 6: MFCC from Scratch Implementation
- OEL: Vowel Synthesis and Formant Analysis

Main Categories:
1. Audio Loading and Processing
2. Waveform Visualization
3. Spectrogram Analysis
4. MFCC Feature Extraction
5. Pitch and Formant Analysis
6. Vowel Synthesis
7. Audio Quality Analysis
"""

# Import necessary modules
from ._code_inspector import ShowableFunction
from ._utils import query, show_lib, list_functions

# Flow lab functions
from .lab_flows import (
    flowlab1,
    flowlab2,
    flowlab4,
    flowlab6,
    flowlab8,
    flowlab9,
    flowlab10,
    flowlab11,
    flowoel,
    flowquiz1,
    list_sp_labs
)

# Lab 1: Audio Loading and Waveform Visualization
from .audio_basics import (
    load_audio,
    get_audio_info,
    resample_audio,
    plot_waveform,
    play_audio,
    save_audio
)

# Lab 2: Spectrograms and Analysis  
from .spectrograms import (
    plot_linear_spectrogram,
    plot_mel_spectrogram,
    plot_narrowband_spectrogram,
    plot_wideband_spectrogram,
    plot_pitch_histogram,
    identify_formants
)

# Lab 4 & 6: MFCC Feature Extraction
from .mfcc_features import (
    extract_mfcc,
    extract_mfcc_from_scratch,
    pre_emphasis,
    frame_signal,
    apply_hamming_window,
    compute_power_spectrum,
    create_mel_filterbank,
    apply_mel_filterbank,
    apply_dct,
    compare_mfcc_coefficients
)

# OEL: Vowel Synthesis
from .vowel_synthesis import (
    synthesize_vowel,
    get_vowel_formants,
    plot_vowel_analysis,
    play_vowel_interactive
)

# Audio Processing Utilities
from .audio_processing import (
    normalize_audio,
    trim_silence,
    add_noise,
    compute_snr,
    stereo_to_mono
)

# Dataset Utilities
from .dataset_utils import (
    load_audio_folder,
    load_audio_from_zip,
    save_synthetic_vowels,
    load_audio_dataset,
    generate_vowel_dataset
)

# MFCC Reference (Viva Preparation)
from .mfcc_reference import (
    mfcc_viva_guide,
    mfcc_cheatsheet
)

# Complex OEL Graph
from .complex_oel import complex_oel_graph

# Lab 8: Speech Recognition (Rule-based, Template Matching, DTW)
from .lab8_recognition import (
    rule_based_speech_analysis,
    template_matching_euclidean,
    dtw_distance,
    template_matching_dtw,
    extract_speech_features
)

# Lab 9: HMM-based Speech Recognition
from .lab9_hmm import (
    extract_mfcc_sequence,
    organize_dataset_by_word,
    train_hmm_model,
    train_hmm_models,
    test_hmm_recognition,
    complete_hmm_workflow
)

# ============================================================================
# Wrap functions with ShowableFunction to add .show() method
# ============================================================================

_functions_to_wrap = [
    # Lab 1
    load_audio, get_audio_info, resample_audio, plot_waveform, 
    play_audio, save_audio,
    
    # Lab 2
    plot_linear_spectrogram, plot_mel_spectrogram, plot_narrowband_spectrogram,
    plot_wideband_spectrogram, plot_pitch_histogram, identify_formants,
    
    # Lab 4 & 6
    extract_mfcc, extract_mfcc_from_scratch, pre_emphasis, frame_signal,
    apply_hamming_window, compute_power_spectrum, create_mel_filterbank,
    apply_mel_filterbank, apply_dct, compare_mfcc_coefficients,
    
    # OEL
    synthesize_vowel, get_vowel_formants, plot_vowel_analysis, 
    play_vowel_interactive,
    
    # Utilities
    normalize_audio, trim_silence, add_noise, compute_snr, stereo_to_mono,
    
    # Dataset
    load_audio_folder, load_audio_from_zip, save_synthetic_vowels,
    load_audio_dataset, generate_vowel_dataset,
    
    # MFCC Reference
    mfcc_viva_guide, mfcc_cheatsheet,
    
    # Complex OEL
    complex_oel_graph,
    
    # Lab 8: Speech Recognition
    rule_based_speech_analysis, template_matching_euclidean,
    dtw_distance, template_matching_dtw, extract_speech_features,
    
    # Lab 9: HMM
    extract_mfcc_sequence, organize_dataset_by_word,
    train_hmm_model, train_hmm_models,
    test_hmm_recognition, complete_hmm_workflow,
    
    # Flow labs
    flowlab1, flowlab2, flowlab4, flowlab6, flowlab8, flowlab9, flowlab10, flowlab11, flowoel, flowquiz1, list_sp_labs
]

for func in _functions_to_wrap:
    # Only wrap if not already wrapped
    if not isinstance(func, ShowableFunction):
        wrapped = ShowableFunction(func)
        globals()[func.__name__] = wrapped

# Clean up internal variables
del ShowableFunction
del wrapped

# ============================================================================
# Export all public symbols
# ============================================================================

__all__ = [
    # Module utilities
    'query',
    'show_lib',
    'list_functions',
    
    # Lab 1: Audio Basics (6 functions)
    'load_audio', 'get_audio_info', 'resample_audio', 'plot_waveform',
    'play_audio', 'save_audio',
    
    # Lab 2 (6 functions)
    'plot_linear_spectrogram', 'plot_mel_spectrogram', 'plot_narrowband_spectrogram',
    'plot_wideband_spectrogram', 'plot_pitch_histogram', 'identify_formants',
    
    # Lab 4 & 6: MFCC (10 functions)
    'extract_mfcc', 'extract_mfcc_from_scratch', 'pre_emphasis', 'frame_signal',
    'apply_hamming_window', 'compute_power_spectrum', 'create_mel_filterbank',
    'apply_mel_filterbank', 'apply_dct', 'compare_mfcc_coefficients',
    
    # OEL: Vowel Synthesis (4 functions)
    'synthesize_vowel', 'get_vowel_formants', 'plot_vowel_analysis',
    'play_vowel_interactive',
    
    # Utilities (5 functions)
    'normalize_audio', 'trim_silence', 'add_noise', 'compute_snr', 'stereo_to_mono',
    
    # Dataset Utilities (5 functions)
    'load_audio_folder', 'load_audio_from_zip', 'save_synthetic_vowels',
    'load_audio_dataset', 'generate_vowel_dataset',
    
    # MFCC Reference (2 functions)
    'mfcc_viva_guide', 'mfcc_cheatsheet',
    
    # Complex OEL Graph (1 function)
    'complex_oel_graph',
    
    # Lab 8: Speech Recognition (5 functions)
    'rule_based_speech_analysis', 'template_matching_euclidean',
    'dtw_distance', 'template_matching_dtw', 'extract_speech_features',
    
    # Lab 9: HMM Speech Recognition (6 functions)
    'extract_mfcc_sequence', 'organize_dataset_by_word',
    'train_hmm_model', 'train_hmm_models',
    'test_hmm_recognition', 'complete_hmm_workflow',
    
    # Flow labs (11 functions)
    'flowlab1', 'flowlab2', 'flowlab4', 'flowlab6', 'flowlab8', 'flowlab9', 'flowlab10', 'flowlab11', 'flowoel', 'flowquiz1', 'list_sp_labs'
]
