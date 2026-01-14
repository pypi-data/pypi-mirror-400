"""
Environment utilities for Reinforcement Learning.

This module provides helper functions for creating and working with
RL environments, including custom Grid World and Gymnasium environments.
Based on Lab 1 and Lab 2 implementations.
"""

import numpy as np
try:
    import gymnasium as gym
except ImportError:
    raise ImportError("Please install gymnasium: pip install gymnasium>=0.28.0")


def create_frozenlake_env(is_slippery=True, map_name='4x4'):
    """
    Create a FrozenLake environment.
    
    FrozenLake is a simple grid world where the agent must navigate
    from start (S) to goal (G) while avoiding holes (H).
    
    Parameters:
    -----------
    is_slippery : bool, optional (default=True)
        If True, actions are stochastic (agent may slip)
        If False, actions are deterministic
    map_name : str, optional (default='4x4')
        Size of the map: '4x4' or '8x8'
    
    Returns:
    --------
    env : gymnasium.Env
        FrozenLake environment
    
    Example:
    --------
    >>> env = create_frozenlake_env(is_slippery=True)
    >>> state, _ = env.reset()
    >>> print(f"Start state: {state}")
    >>> print(f"Number of states: {env.observation_space.n}")
    >>> print(f"Number of actions: {env.action_space.n}")
    """
    env = gym.make('FrozenLake-v1', is_slippery=is_slippery, 
                   map_name=map_name, render_mode='ansi')
    return env


def random_agent_episode(env, max_steps=100):
    """
    Run a single episode with a random agent.
    
    The agent takes random actions until the episode ends
    or max_steps is reached.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment
    max_steps : int, optional (default=100)
        Maximum steps per episode
    
    Returns:
    --------
    episode_reward : float
        Total reward collected
    episode_length : int
        Number of steps taken
    states : list
        List of states visited
    actions : list
        List of actions taken
    
    Example:
    --------
    >>> env = create_frozenlake_env()
    >>> reward, length, states, actions = random_agent_episode(env)
    >>> print(f"Episode reward: {reward}")
    >>> print(f"Episode length: {length}")
    >>> print(f"Path: {states}")
    """
    state, _ = env.reset()
    done = False
    episode_reward = 0
    episode_length = 0
    states = [state]
    actions = []
    
    while not done and episode_length < max_steps:
        # Random action
        action = env.action_space.sample()
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        
        episode_reward += reward
        episode_length += 1
        states.append(next_state)
        actions.append(action)
        
        state = next_state
    
    return episode_reward, episode_length, states, actions


def visualize_path(states, grid_shape=(4, 4), message="Agent Path"):
    """
    Print a simple visualization of the agent's path through a grid.
    
    Parameters:
    -----------
    states : list
        List of state indices visited
    grid_shape : tuple, optional (default=(4, 4))
        Shape of the grid (rows, cols)
    message : str, optional
        Message to print before the visualization
    
    Example:
    --------
    >>> states = [0, 1, 5, 6, 10, 14, 15]
    >>> visualize_path(states, grid_shape=(4, 4), message="Successful path")
    """
    rows, cols = grid_shape
    print(f"\n{message}")
    print(f"Path: {' -> '.join(map(str, states))}")
    print(f"Total steps: {len(states) - 1}")
    
    # Create grid visualization
    grid = np.zeros(grid_shape, dtype=int)
    for step, state in enumerate(states, 1):
        row = state // cols
        col = state % cols
        grid[row, col] = step
    
    print("\nGrid (numbers show step order):")
    print(grid)


class GridWorld:
    """
    Custom 3x4 Grid World environment.
    
    A simple grid world with:
    - Goal state (positive reward)
    - Danger state (negative reward)
    - Wall (impassable)
    - Normal states (small negative reward)
    
    Based on Lab 2 implementation.
    """
    
    def __init__(self, rows=3, cols=4, wall=(1, 2), goal=(0, 3), danger=(2, 3)):
        """
        Initialize Grid World.
        
        Parameters:
        -----------
        rows : int, optional (default=3)
            Number of rows
        cols : int, optional (default=4)
            Number of columns
        wall : tuple, optional (default=(1, 2))
            Position of wall (not a valid state)
        goal : tuple, optional (default=(0, 3))
            Goal state position
        danger : tuple, optional (default=(2, 3))
            Danger state position
        
        Example:
        --------
        >>> gw = GridWorld()
        >>> print(f"States: {gw.states}")
        >>> print(f"Actions: {gw.actions}")
        >>> print(f"Reward at goal: {gw.reward(gw.goal)}")
        """
        self.rows = rows
        self.cols = cols
        self.wall = wall
        self.goal = goal
        self.danger = danger
        
        # Define states (all grid positions except wall)
        self.states = [(i, j) for i in range(rows) for j in range(cols)]
        if wall in self.states:
            self.states.remove(wall)
        
        # Define actions
        self.actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    
    def reward(self, state):
        """
        Get reward for reaching a state.
        
        Parameters:
        -----------
        state : tuple
            State as (row, col)
        
        Returns:
        --------
        reward : float
            +1.0 for goal, -1.0 for danger, -0.04 for others
        """
        if state == self.goal:
            return 1.0
        elif state == self.danger:
            return -1.0
        else:
            return -0.04
    
    def is_terminal(self, state):
        """
        Check if a state is terminal.
        
        Parameters:
        -----------
        state : tuple
            State as (row, col)
        
        Returns:
        --------
        terminal : bool
            True if state is goal or danger
        """
        return state in [self.goal, self.danger]
    
    def __repr__(self):
        """String representation of the Grid World."""
        return (f"GridWorld({self.rows}x{self.cols}, "
                f"wall={self.wall}, goal={self.goal}, danger={self.danger})")
