"""
Lab Workflow Reference Functions - Complete Notebook Code Display
==================================================================

These functions show you the COMPLETE code from your actual Jupyter notebooks.
The code is embedded directly in the library - no external files needed.

When you call flowlab1(), flowlab2(), etc., it displays the ENTIRE notebook code
exactly as it appears in your lab files, with all cells and code.

Usage:
------
>>> from matplotlab import rl
>>> rl.flowlab1()   # Shows complete Lab 1 notebook code
>>> rl.flowlab2()   # Shows complete Lab 2 notebook code  
>>> rl.flowlab3()   # Shows complete Lab 3 notebook code
>>> rl.flowlab4()   # Shows complete Lab 4 notebook code
>>> rl.flowlab5()   # Shows complete Lab 5 notebook code
>>> rl.flowlab6()   # Shows complete Lab 6 notebook code
>>> rl.flowlab7()   # Shows complete Lab 7 notebook code (MC vs TD)
>>> rl.flowlab8()   # Shows complete Lab 8 notebook code (Q-Learning & FA)
>>> rl.flowlab9()   # Shows complete Lab 9 notebook code (Off-Policy Learning)
>>> rl.flowlab10()  # Shows complete Lab 10 notebook code (Function Approximation)
>>> rl.flowlab11()  # Shows complete Lab 11 notebook code (Batch RL Analysis)
>>> rl.flowlab12()  # Shows complete Lab 12 notebook code (Deep Q-Networks)
>>> rl.flowoel()    # Shows complete OEL workflow
>>> rl.flowoel2()   # Shows complete OEL 2 notebook code (Comprehensive Analysis)

Note: All code is embedded in the library. No external files or folders needed.
"""

import sys
from ._lab_code import LAB_CODE


def _safe_print(text):
    """Print text safely with unicode handling."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Handle unicode encoding errors on Windows
        sys.stdout.buffer.write(text.encode('utf-8'))
        sys.stdout.buffer.write(b'\n')


def _display_lab_header(lab_name, lab_id):
    """Display simple header for lab"""
    _safe_print(f"\n# {lab_name}")
    _safe_print(f"# Lab Code {lab_id}\n")


def flowlab1():
    """Display complete Lab 1 notebook code"""
    code = LAB_CODE.get(1, "Lab 1 code not found")
    _display_lab_header("LAB 1: Reinforcement Learning Basics", 1)
    _safe_print(code)


def flowlab2():
    """Display complete Lab 2 notebook code"""
    code = LAB_CODE.get(2, "Lab 2 code not found")
    _display_lab_header("LAB 2: Grid World and MDP", 2)
    _safe_print(code)


def flowlab3():
    """Display complete Lab 3 notebook code"""
    code = LAB_CODE.get(3, "Lab 3 code not found")
    _display_lab_header("LAB 3: Monte Carlo Methods", 3)
    _safe_print(code)


def flowlab4():
    """Display complete Lab 4 notebook code"""
    code = LAB_CODE.get(4, "Lab 4 code not found")
    _display_lab_header("LAB 4: Temporal Difference & Policy Evaluation", 4)
    _safe_print(code)


def flowlab5():
    """Display complete Lab 5 notebook code"""
    code = LAB_CODE.get(5, "Lab 5 code not found")
    _display_lab_header("LAB 5: Advanced Policy Methods", 5)
    _safe_print(code)


def flowlab6():
    """Display complete Lab 6 notebook code"""
    code = LAB_CODE.get(6, "Lab 6 code not found")
    _display_lab_header("LAB 6: State-Action-Reward Framework", 6)
    _safe_print(code)


def flowlab7():
    """Display complete Lab 7 notebook code"""
    code = LAB_CODE.get(7, "Lab 7 code not found")
    _display_lab_header("LAB 7: Monte Carlo vs Temporal Difference", 7)
    _safe_print(code)


def flowlab8():
    """Display complete Lab 8 notebook code"""
    code = LAB_CODE.get(8, "Lab 8 code not found")
    _display_lab_header("LAB 8: Q-Learning & Function Approximation", 8)
    _safe_print(code)


def flowlab9():
    """Display complete Lab 9 notebook code"""
    code = LAB_CODE.get(9, "Lab 9 code not found")
    _display_lab_header("LAB 9: Off-Policy Monte Carlo Learning", 9)
    _safe_print(code)


def flowlab10():
    """Display complete Lab 10 notebook code"""
    code = LAB_CODE.get(10, "Lab 10 code not found")
    _display_lab_header("LAB 10: Function Approximation Methods", 10)
    _safe_print(code)


def flowlab11():
    """Display complete Lab 11 notebook code"""
    code = LAB_CODE.get(11, "Lab 11 code not found")
    _display_lab_header("LAB 11: Batch Reinforcement Learning", 11)
    _safe_print(code)


def flowlab12():
    """Display complete Lab 12 notebook code"""
    code = LAB_CODE.get(12, "Lab 12 code not found")
    _display_lab_header("LAB 12: Deep Q-Networks (DQN)", 12)
    _safe_print(code)


def flowoel():
    """Display complete OEL 1 notebook code"""
    code = LAB_CODE.get('OEL1', "OEL 1 code not found")
    _display_lab_header("OEL 1: Out-of-Lab Project", 'OEL1')
    _safe_print(code)


def flowoel2():
    """Display complete OEL 2 notebook code"""
    code = LAB_CODE.get('OEL2', "OEL 2 code not found")
    _display_lab_header("OEL 2: Comprehensive Analysis Project", 'OEL2')
    _safe_print(code)
