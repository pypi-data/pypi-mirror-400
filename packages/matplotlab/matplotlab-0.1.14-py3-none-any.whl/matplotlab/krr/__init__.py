"""
Knowledge Representation and Reasoning (KRR) Module for matplotlab
==================================================================

This module provides functions for knowledge representation and reasoning,
covering fuzzy logic, probabilistic reasoning with Bayesian networks, and
symbolic reasoning with Prolog.

Labs Coverage:
- Lab 8: Fuzzy Logic & Fuzzy Reasoning
- Lab 11: Bayesian Networks & Probabilistic Reasoning
- Lab 12: Knowledge Representation (pgmpy-based Bayesian Networks)
- OEL2: Prolog Knowledge Base - Role Hierarchy & Access Control

Main Categories:
1. Fuzzy Logic Systems (Lab 8)
2. Bayesian Networks (Labs 11, 12)
3. Probabilistic Inference
4. Prolog Knowledge Bases (OEL2)
5. Symbolic Reasoning
6. Access Control & Role Management
"""

# Flow lab functions
from .lab_flows import (
    flowlab6,
    flowlab7,
    flowlab8,
    flowlab11,
    flowlab12,
    flowoel2,
    show_prolog_kb,
    flowtemplate,
    list_krr_labs
)

# ============================================================================
# Export all public symbols
# ============================================================================

__all__ = [
    # Flow labs (9 functions)
    'flowlab6',
    'flowlab7',
    'flowlab8',
    'flowlab11',
    'flowlab12',
    'flowoel2',
    'show_prolog_kb',
    'flowtemplate',
    'list_krr_labs'
]
