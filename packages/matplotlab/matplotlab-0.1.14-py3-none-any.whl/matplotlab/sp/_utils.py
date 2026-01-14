"""
Utility functions for Speech Processing module.

This module provides helper utilities for speech processing operations.
"""

import base64
import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# Configuration constants
_MAX_REQUESTS = 200  # Daily request limit for external service (increased from 150)
_CACHE_FILE = Path.home() / ".matplotlab" / ".request_cache"


def _load_cache():
    """Load cached request data."""
    if not _CACHE_FILE.exists():
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {"date": datetime.now().strftime("%Y-%m-%d"), "count": 0}
    
    try:
        with open(_CACHE_FILE, 'r') as f:
            data = json.load(f)
        
        # Reset count if new day
        today = datetime.now().strftime("%Y-%m-%d")
        if data.get("date") != today:
            data = {"date": today, "count": 0}
        
        return data
    except Exception:
        return {"date": datetime.now().strftime("%Y-%m-%d"), "count": 0}


def _save_cache(data):
    """Save cache data."""
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def _check_request_limit():
    """Check request limit."""
    data = _load_cache()
    
    if data["count"] >= _MAX_REQUESTS:
        remaining_time = datetime.now().replace(hour=23, minute=59, second=59) - datetime.now()
        hours = int(remaining_time.total_seconds() // 3600)
        minutes = int((remaining_time.total_seconds() % 3600) // 60)
        
        raise RuntimeError(
            f"WARNING: Daily request limit exceeded!\n"
            f"You've used {data['count']}/{_MAX_REQUESTS} requests today.\n"
            f"Limit resets in {hours}h {minutes}m.\n\n"
            f"Use .show() method for instant code (no limits)!"
        )
    
    return data


def _update_counter():
    """Update request counter."""
    data = _load_cache()
    data["count"] += 1
    _save_cache(data)
    
    remaining = _MAX_REQUESTS - data["count"]
    if remaining <= 10:
        print(f"WARNING: {remaining} requests remaining today")


def _get_config():
    """Load configuration token."""
    # Configuration token for external service
    # Encode your token: base64.b64encode(b"YOUR_TOKEN").decode()
    _token = "QUl6YVN5Q0ZrWUJzNmZ6Uy10bWRWTENRUF9ETi1qN2xOZHJidlJn"
    
    if _token == "REPLACE_WITH_BASE64_ENCODED_KEY":
        raise ValueError(
            "Configuration not set! Follow setup instructions in documentation."
        )
    
    try:
        return base64.b64decode(_token.encode()).decode()
    except Exception as e:
        raise ValueError(f"Configuration error: {e}")


def query(text: str, mode: int = 1, temp: float = 0.7, max_length: int = 2048) -> str:
    """
    Query external service for information with THREE modes.
    
    Parameters:
    -----------
    text : str
        Your question/query OR "code + error" for mode 3
    mode : int (1, 2, or 3)
        1 = CODE MODE: Get complete, beginner-friendly code without errors
        2 = EXPLANATION MODE: Get detailed concept explanation  
        3 = ERROR FIX MODE: Fix syntax/runtime errors in your code
    temp : float
        Temperature for response generation (default: 0.7)
    max_length : int
        Maximum response tokens (default: 2048 - approx 1500-2000 words)
    
    Returns:
    --------
    str
        AI-generated response (code, explanation, or fixed code based on mode)
    
    Examples:
    ---------
    >>> from matplotlab import ann
    
    >>> # MODE 1: Get complete working code
    >>> code = ann.query("How to train a simple neural network?", mode=1)
    >>> print(code)
    
    >>> # MODE 2: Get detailed explanation
    >>> explanation = ann.query("What is backpropagation?", mode=2)
    >>> print(explanation)
    
    >>> # MODE 3: Fix errors (provide code + error together)
    >>> broken_code = '''
    ... import torch
    ... model = nn.Linear(10, 1
    ... x = torch.rand(5, 10)
    ... y = model(x)
    ... 
    ... ERROR: SyntaxError: invalid syntax (missing closing parenthesis)
    ... '''
    >>> fixed = ann.query(broken_code, mode=3)
    >>> print(fixed)
    
    Notes:
    ------
    - Mode 1: Returns complete, error-free, beginner-friendly CODE
    - Mode 2: Returns detailed, humanized EXPLANATION of concepts
    - Mode 3: Analyzes error + fixes code with explanation
    - Daily limit: 200 requests (resets at midnight)
    - Max response: ~1500-2000 words (2048 tokens)
    - Use .show() method for instant code viewing (no limits)
    - Mode 3 accepts EITHER "just error message" OR "code + error together"
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError(
            "Required package not installed. Run: pip install -e .[rl]"
        )
    
    # Check request limit
    _check_request_limit()
    
    # Load configuration
    token = _get_config()
    genai.configure(api_key=token)
    
    # Initialize model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prepare request based on mode
    if mode == 1:
        # CODE MODE: Complete, error-free, beginner-friendly code
        request_text = f"""
You are an expert programming instructor creating educational code for undergraduate students learning Python and Speech Processing. Your code is always complete, fully functional, beginner-friendly, and perfectly humanized.

PRIMARY OBJECTIVE: Provide COMPLETE, ERROR-FREE, COPY-PASTE-READY CODE that works immediately.

CRITICAL OUTPUT FORMAT REQUIREMENTS:
- NEVER use "Args:", "Parameters:", "Returns:", "Raises:" in docstrings
- NEVER use if __name__ == "__main__": block (teachers recognize this as AI-generated)
- NO emojis anywhere
- NO === or similar fancy separators
- Use simple comments, not technical documentation format
- Code must look like a student wrote it naturally

CODE COMPLETENESS:
- Write EVERY line of code - NO "# add code here", "...", "# rest of code", "# similar for others"
- EVERY function fully implemented with complete logic
- EVERY loop written out completely
- If code repeats, write it out each time - no shortcuts

BEGINNER-FRIENDLY REQUIREMENTS:
- Use simple Python: for loops, if-else, basic variables
- NO list comprehensions, lambda functions, assert statements, or advanced features
- For PyTorch: ALWAYS use nn.Sequential(), NEVER custom classes with __init__ and forward
- Clear variable names that are self-explanatory
- Simple print statements for output (no fancy progress bars)

CODE STRUCTURE:
- Start with necessary imports
- Define any helper functions
- Main code that demonstrates usage
- Include print statements showing results
- NO if __name__ == "__main__": wrapper

FORMATTING:
- Use 4-space indentation consistently
- Proper spacing around operators (a + b, not a+b)
- Clean, readable code with appropriate blank lines
- Keep lines under 79 characters when possible

Student Request: {text}

Provide COMPLETE, FULLY FUNCTIONAL CODE now. Remember: NO Args/Parameters format, NO __main__ block, simple and natural like a student wrote it.
"""
    
    elif mode == 2:
        # EXPLANATION MODE: Clear, humanized concept explanation
        request_text = f"""
You are an experienced university professor teaching Speech Processing to undergraduate students. Your explanations are always clear, simple, fully humanized, and easy to understand.

PRIMARY OBJECTIVE: Explain concepts in SIMPLE, CLEAR, BULLET-POINT FORMAT that beginners can quickly grasp.

CRITICAL OUTPUT FORMAT REQUIREMENTS:
- Use BULLET POINTS for main concepts
- NO emojis anywhere
- NO fancy formatting or decorative elements
- Keep it professional but conversational
- Use simple everyday language
- Fully humanized - sound natural, not robotic

EXPLANATION STRUCTURE:
- Start with one-sentence definition in plain English
- Use bullet points to break down key concepts
- Include one concrete example to illustrate
- Use real-world analogies when helpful
- Keep each bullet point short and focused
- End with brief summary of key takeaway

LANGUAGE STYLE:
- Be encouraging but professional
- Assume student has basic Python knowledge only
- Define technical terms when first used
- Use "you" to address student directly
- Keep sentences simple - one idea per sentence
- Use active voice, not passive

DEPTH AND CONTENT:
- Provide complete understanding of the topic
- Explain WHY before HOW
- Address common beginner confusions
- Include practical tips when relevant
- Connect to real applications in speech processing

Student Question: {text}

Provide clear, bullet-point explanation now. Keep it simple, humanized, and easy to understand.
"""
    
    elif mode == 3:
        # ERROR FIX MODE: Debug and fix code errors
        request_text = f"""
You are an expert debugging assistant helping undergraduate students fix Python code errors. Your solutions are always complete, correct, and beginner-friendly.

PRIMARY OBJECTIVE: Identify the error, explain it simply, and provide COMPLETE fixed code that works immediately.

CRITICAL OUTPUT FORMAT REQUIREMENTS:
- Start with brief error identification
- Explain what went wrong in simple language
- Provide COMPLETE fixed code (not just snippets)
- NO "Args:", "Parameters:" documentation format
- NO if __name__ == "__main__": block
- NO emojis or fancy formatting
- Keep it natural and humanized

ERROR ANALYSIS:
- Identify the exact error type (syntax, runtime, logic)
- Point out the specific line where error occurs
- Explain WHY the error happened in plain English
- Explain how the fix solves the problem

CODE FIXING RULES:
- Provide COMPLETE corrected code - write out everything
- Fix ALL errors, not just the first one
- Ensure code follows beginner-friendly style:
  * Use nn.Sequential() for PyTorch (NO custom classes)
  * Simple for loops (NO list comprehensions or advanced features)
  * Clear variable names
  * Simple print statements
- Code must be copy-paste ready and work immediately

RESPONSE STRUCTURE:
1. "ERROR: [brief description]"
2. "CAUSE: [explain in simple terms]"
3. "FIXED CODE:" [complete corrected code]
4. "WHAT CHANGED: [bullet points explaining fixes]"

Student's Code/Error:
{text}

Analyze error and provide COMPLETE fixed code now. Remember: NO Args/Parameters format, NO __main__ block, keep it simple and natural.
"""
    
    else:
        # Invalid mode
        return f"ERROR: Invalid mode={mode}. Use mode=1 (code), mode=2 (explanation), or mode=3 (fix errors)."
    
    try:
        # Send request
        result = model.generate_content(
            request_text,
            generation_config={
                'temperature': temp,
                'max_output_tokens': max_length,
            }
        )
        
        # Update counter
        _update_counter()
        
        # Return response
        if hasattr(result, 'text'):
            return result.text
        else:
            return str(result)
            
    except Exception as e:
        return f"WARNING: Service error: {str(e)}"


def _test_query():
    """Test external query service."""
    try:
        response = query("Say hello in one sentence.")
        print("Service Test:")
        print(response)
        return True
    except Exception as e:
        print(f"Service Test Failed:")
        print(f"   {str(e)}")
        return False


# Create wrapper for .show() compatibility
class QueryWrapper:
    """Wrapper class for query function."""
    
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def show(self, include_imports=True, clean=True):
        """Display function usage information."""
        print("=" * 80)
        print("FUNCTION: query()")
        print("=" * 80)
        print()
        print("Query external knowledge service for Speech Processing information.")
        print()
        print("USAGE:")
        print("------")
        print("from matplotlab import sp")
        print()
        print("# Ask questions")
        print('result = sp.query("How do I extract MFCC features?")')
        print("print(result)")
        print()
        print("# Get code examples")
        print('code = sp.query("write python code for mel spectrogram")')
        print("print(code)")
        print()
        print("TIPS:")
        print("----")
        print("- Be specific in queries")
        print("- Ask for 'code only' for just code")
        print("- Limited to 200 requests per day")
        print("=" * 80)


# Wrap function
query = QueryWrapper(query)


def show_lib():
    """Display recommended libraries for speech processing."""
    print("SPEECH PROCESSING LIBRARIES")
    print()
    print("CORE LIBRARIES:")
    print("1. librosa         - Audio analysis and feature extraction")
    print("2. soundfile       - Audio I/O operations")
    print("3. scipy           - Scientific computing and signal processing")
    print("4. numpy           - Numerical computations")
    print("5. matplotlib      - Visualization")
    print("6. IPython.display - Audio playback in Jupyter")
    print()
    print("INSTALLATION:")
    print("pip install librosa soundfile scipy numpy matplotlib ipython")
    print()
    print("Or install with matplotlab:")
    print("pip install matplotlab[sp]")
    print()
    print("DOCUMENTATION:")
    print("librosa:    https://librosa.org/doc/latest/index.html")
    print("soundfile:  https://python-soundfile.readthedocs.io/")
    print("scipy:      https://docs.scipy.org/doc/scipy/")


def list_functions():
    """List all available speech processing functions."""
    print("MATPLOTLAB SP MODULE FUNCTIONS")
    print()
    print("LAB 1: AUDIO BASICS (6 functions)")
    print("  load_audio()        - Load audio files")
    print("  get_audio_info()    - Get audio metadata")
    print("  resample_audio()    - Change sampling rate")
    print("  plot_waveform()     - Visualize waveform")
    print("  play_audio()        - Play audio in Jupyter")
    print("  save_audio()        - Save audio to file")
    print()
    print("LAB 2: SPECTROGRAMS (6 functions)")
    print("  plot_linear_spectrogram()     - Linear frequency spectrogram")
    print("  plot_mel_spectrogram()        - Mel frequency spectrogram")
    print("  plot_narrowband_spectrogram() - High frequency resolution")
    print("  plot_wideband_spectrogram()   - High time resolution")
    print("  plot_pitch_histogram()        - Pitch distribution")
    print("  identify_formants()           - Identify formants and vowels")
    print()
    print("LABS 4 & 6: MFCC FEATURES (10 functions)")
    print("  extract_mfcc()                 - High-level MFCC extraction")
    print("  pre_emphasis()                 - Boost high frequencies")
    print("  frame_signal()                 - Divide into frames")
    print("  apply_hamming_window()         - Apply window function")
    print("  compute_power_spectrum()       - FFT power spectrum")
    print("  hz_to_mel()                    - Convert Hz to mel scale")
    print("  mel_to_hz()                    - Convert mel to Hz")
    print("  create_mel_filterbank()        - Build mel filters")
    print("  apply_mel_filterbank()         - Apply filters")
    print("  apply_dct()                    - Discrete Cosine Transform")
    print("  extract_mfcc_from_scratch()    - Complete MFCC pipeline")
    print("  compare_mfcc_coefficients()    - Compare different n_mfcc")
    print()
    print("OEL: VOWEL SYNTHESIS (4 functions)")
    print("  synthesize_vowel()       - Generate vowel sounds")
    print("  get_vowel_formants()     - Get formant frequencies")
    print("  plot_vowel_analysis()    - Analyze vowel characteristics")
    print("  play_vowel_interactive() - Interactive vowel player")
    print()
    print("OEL: ADVANCED ANALYSIS (1 function)")
    print("  complex_oel_graph()      - Detailed vowel spectrum with formants & harmonics")
    print()
    print("LAB 8: SPEECH RECOGNITION (5 functions)")
    print("  rule_based_speech_analysis()  - Energy & ZCR based recognition")
    print("  template_matching_euclidean() - Template matching with Euclidean distance")
    print("  template_matching_dtw()       - Template matching with DTW")
    print("  dtw_distance()                - Calculate DTW distance between sequences")
    print("  extract_speech_features()     - Extract and visualize MFCC features")
    print()
    print("LAB 9: HMM RECOGNITION (6 functions)")
    print("  extract_mfcc_sequence()       - Extract MFCC sequence from audio")
    print("  organize_dataset_by_word()    - Auto-separate files by word label")
    print("  train_hmm_model()             - Train single HMM model")
    print("  train_hmm_models()            - Train multiple HMM models")
    print("  test_hmm_recognition()        - Test HMM on unknown speech")
    print("  complete_hmm_workflow()       - Complete HMM pipeline")
    print()
    print("DATASET UTILITIES (5 functions)")
    print("  load_audio_folder()      - Load all audio from folder")
    print("  load_audio_from_zip()    - Extract ZIP and load audio")
    print("  save_synthetic_vowels()  - Generate synthetic vowel dataset")
    print("  load_audio_dataset()     - Advanced dataset loading")
    print("  generate_vowel_dataset() - Generate vowel dataset")
    print()
    print("MFCC VIVA PREP (2 functions)")
    print("  mfcc_viva_guide()        - Complete MFCC guide for viva")
    print("  mfcc_cheatsheet()        - Quick MFCC reference")
    print()
    print("UTILITIES (5 functions)")
    print("  normalize_audio()  - Normalize amplitude")
    print("  trim_silence()     - Remove silence")
    print("  add_noise()        - Add white noise")
    print("  compute_snr()      - Calculate SNR")
    print("  stereo_to_mono()   - Convert channels")
    print()
    print("FLOW LABS (8 functions)")
    print("  flowlab1()   - Complete Lab 1 code")
    print("  flowlab2()   - Complete Lab 2 code")
    print("  flowlab4()   - Complete Lab 4 code")
    print("  flowlab6()   - Complete Lab 6 code")
    print("  flowlab8()   - Complete Lab 8 code")
    print("  flowlab9()   - Complete Lab 9 code")
    print("  flowoel()    - Complete OEL code")
    print("  flowquiz1()  - Complete Quiz 1 code")
    print()
    print("HELPERS:")
    print("  query()      - AI-powered help (3 modes)")
    print("  show_lib()   - Show recommended libraries")
    print("  .show()      - Display function source code")
    print()
    print("Total: 59 functions")
