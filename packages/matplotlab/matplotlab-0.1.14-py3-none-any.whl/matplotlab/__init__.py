"""
Matplotlab - Extended Plotting and ML Utilities
================================================

A comprehensive library covering:
- Reinforcement Learning (rl)
- Artificial Neural Networks (ann)
- Speech Processing (sp)
- Knowledge Representation and Reasoning (krr)

Usage:
    from matplotlab import rl, ann, sp, krr

Author: ML Community
Date: 2025
"""

__version__ = "0.1.14"
__author__ = "ML Community"

# Import submodules with graceful fallback for optional dependencies
from . import rl

# ANN module requires torch
try:
    from . import ann
except (ImportError, ModuleNotFoundError) as e:
    if 'torch' in str(e) or '_custom_ops' in str(e):
        import warnings
        warnings.warn(
            f"ANN module not available due to PyTorch issue: {e}. "
            "RL module is available. Try: pip install --upgrade torch torchvision",
            ImportWarning
        )
    else:
        raise

# SP module requires optional dependencies (librosa, soundfile, etc)
try:
    from . import sp
except ImportError as e:
    if 'librosa' in str(e) or 'soundfile' in str(e):
        import warnings
        warnings.warn(
            "SP (Speech Processing) module requires optional dependencies. "
            "Install with: pip install matplotlab[sp]",
            ImportWarning
        )
        sp = None
    else:
        raise

# KRR module - Knowledge Representation and Reasoning
try:
    from . import krr
except ImportError as e:
    if 'pgmpy' in str(e):
        import warnings
        warnings.warn(
            "KRR module requires pgmpy. Install with: pip install pgmpy",
            ImportWarning
        )
        krr = None
    else:
        raise

__all__ = ["rl", "ann", "sp", "krr"]

