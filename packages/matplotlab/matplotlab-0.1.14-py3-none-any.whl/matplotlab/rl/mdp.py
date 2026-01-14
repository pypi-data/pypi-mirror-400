"""
MDP (Markov Decision Process) utilities for Grid World.

This module contains functions for working with Grid World MDPs,
including state transitions, rewards, and transition probabilities.
Based on Lab 2 implementations.
"""

import numpy as np


# Grid dimensions (default for Lab 2)
DEFAULT_ROWS = 3
DEFAULT_COLS = 4
DEFAULT_WALL = (1, 2)
DEFAULT_GOAL = (0, 3)
DEFAULT_DANGER = (2, 3)


def define_states_actions(rows=DEFAULT_ROWS, cols=DEFAULT_COLS, wall=DEFAULT_WALL):
    """
    Define all valid states and actions for a Grid World.
    
    Parameters:
    -----------
    rows : int, optional (default=3)
        Number of rows in the grid
    cols : int, optional (default=4)
        Number of columns in the grid
    wall : tuple, optional (default=(1, 2))
        Position of the wall (not a valid state)
    
    Returns:
    --------
    states : list
        List of all valid (row, col) state tuples
    actions : list
        List of action strings: ["UP", "DOWN", "LEFT", "RIGHT"]
    
    Example:
    --------
    >>> states, actions = define_states_actions()
    >>> print(f"Total states: {len(states)}")
    >>> print(f"Actions: {actions}")
    """
    # Create all grid positions
    states = [(i, j) for i in range(rows) for j in range(cols)]
    
    # Remove wall position
    if wall in states:
        states.remove(wall)
    
    # Define possible actions
    actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    
    return states, actions


def reward(state, goal=DEFAULT_GOAL, danger=DEFAULT_DANGER):
    """
    Get the reward for a given state.
    
    Parameters:
    -----------
    state : tuple
        Current state as (row, col)
    goal : tuple, optional (default=(0, 3))
        Goal state position
    danger : tuple, optional (default=(2, 3))
        Danger state position
    
    Returns:
    --------
    reward : float
        +1.0 for goal state, -1.0 for danger state, -0.04 for others
    
    Example:
    --------
    >>> r = reward((0, 3))  # Goal state
    >>> print(r)
    1.0
    >>> r = reward((1, 1))  # Normal state
    >>> print(r)
    -0.04
    """
    if state == goal:
        return 1.0
    elif state == danger:
        return -1.0
    else:
        return -0.04


def next_state(state, action, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, wall=DEFAULT_WALL):
    """
    Calculate the next state given current state and action.
    
    Handles grid boundaries and wall collisions.
    If the action would move into a wall or out of bounds,
    the agent stays in the current state.
    
    Parameters:
    -----------
    state : tuple
        Current state as (row, col)
    action : str
        Action to take: "UP", "DOWN", "LEFT", or "RIGHT"
    rows : int, optional (default=3)
        Number of rows in the grid
    cols : int, optional (default=4)
        Number of columns in the grid
    wall : tuple, optional (default=(1, 2))
        Position of the wall
    
    Returns:
    --------
    next_state : tuple
        The resulting state after taking the action
    
    Example:
    --------
    >>> s = (2, 0)
    >>> next_s = next_state(s, "UP")
    >>> print(next_s)
    (1, 0)
    >>> next_s = next_state(s, "LEFT")  # Would go out of bounds
    >>> print(next_s)
    (2, 0)
    """
    i, j = state
    
    # Calculate new position based on action
    if action == "UP":
        i = max(i - 1, 0)
    elif action == "DOWN":
        i = min(i + 1, rows - 1)
    elif action == "LEFT":
        j = max(j - 1, 0)
    elif action == "RIGHT":
        j = min(j + 1, cols - 1)
    
    # If move hits wall, stay in same state
    if (i, j) == wall:
        return state
    
    return (i, j)


def transition_probabilities(state, action, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, 
                            wall=DEFAULT_WALL, goal=DEFAULT_GOAL, danger=DEFAULT_DANGER,
                            intended_prob=0.8, slip_prob=0.1):
    """
    Calculate transition probabilities for a state-action pair.
    
    In Grid World, actions are stochastic:
    - 80% chance of going in the intended direction
    - 10% chance of slipping left
    - 10% chance of slipping right
    
    Terminal states (goal, danger) have 100% probability of staying.
    
    Parameters:
    -----------
    state : tuple
        Current state as (row, col)
    action : str
        Intended action: "UP", "DOWN", "LEFT", or "RIGHT"
    rows : int, optional (default=3)
        Number of rows in the grid
    cols : int, optional (default=4)
        Number of columns in the grid
    wall : tuple, optional (default=(1, 2))
        Position of the wall
    goal : tuple, optional (default=(0, 3))
        Goal state position
    danger : tuple, optional (default=(2, 3))
        Danger state position
    intended_prob : float, optional (default=0.8)
        Probability of moving in intended direction
    slip_prob : float, optional (default=0.1)
        Probability of slipping left or right
    
    Returns:
    --------
    probs : dict
        Dictionary mapping next_state -> probability
    
    Example:
    --------
    >>> state = (2, 0)
    >>> action = "UP"
    >>> probs = transition_probabilities(state, action)
    >>> for next_s, prob in probs.items():
    ...     print(f"{next_s}: {prob:.2f}")
    (1, 0): 0.80
    (2, 0): 0.20
    """
    # Terminal states stay put
    if state in [goal, danger]:
        return {state: 1.0}
    
    probs = {}
    
    # Get intended next state
    intended = next_state(state, action, rows, cols, wall)
    
    # Define perpendicular slip directions
    if action == "UP":
        left, right = "LEFT", "RIGHT"
    elif action == "DOWN":
        left, right = "RIGHT", "LEFT"
    elif action == "LEFT":
        left, right = "DOWN", "UP"
    else:  # RIGHT
        left, right = "UP", "DOWN"
    
    # Get slip states
    slip_left = next_state(state, left, rows, cols, wall)
    slip_right = next_state(state, right, rows, cols, wall)
    
    # Accumulate probabilities (states can overlap)
    probs[intended] = probs.get(intended, 0) + intended_prob
    probs[slip_left] = probs.get(slip_left, 0) + slip_prob
    probs[slip_right] = probs.get(slip_right, 0) + slip_prob
    
    return probs
