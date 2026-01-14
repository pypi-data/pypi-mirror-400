"""
Temporal Difference (TD) Learning for Reinforcement Learning.

This module implements TD(0) prediction for policy evaluation.
Based on Lab 7 implementations.
"""

import numpy as np


def td_prediction(env, policy, num_episodes=10000, alpha=0.1, gamma=0.99, track_values=False):
    """
    TD(0) prediction algorithm for policy evaluation.
    
    TD(0) updates the value function after each step using:
    V(s) = V(s) + alpha * [r + gamma*V(s') - V(s)]
    
    Unlike Monte Carlo (which waits until end of episode),
    TD learning updates immediately using bootstrapping.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment with discrete observation space
    policy : numpy.ndarray or dict
        Policy to evaluate. Can be:
        - Array of shape (nS, nA) with action probabilities
        - Dict mapping state -> action
    num_episodes : int, optional (default=10000)
        Number of episodes to run
    alpha : float, optional (default=0.1)
        Learning rate (step size)
    gamma : float, optional (default=0.99)
        Discount factor
    track_values : bool, optional (default=False)
        If True, store V after each episode for plotting convergence
    
    Returns:
    --------
    V : numpy.ndarray
        Estimated value function
    V_track : list (only if track_values=True)
        List of V arrays after each episode, for convergence analysis
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1', is_slippery=True)
    >>> nS = env.observation_space.n
    >>> nA = env.action_space.n
    >>> # Random policy
    >>> policy = np.ones([nS, nA]) / nA
    >>> V = td_prediction(env, policy, num_episodes=5000, alpha=0.1)
    >>> print("State values:", V)
    >>> 
    >>> # With convergence tracking
    >>> V, V_track = td_prediction(env, policy, num_episodes=1000, track_values=True)
    >>> print(f"Tracked {len(V_track)} value functions")
    """
    nS = env.observation_space.n
    V = np.zeros(nS)
    
    # Track value function over time if requested
    V_track = [] if track_values else None
    
    for episode in range(num_episodes):
        state, _ = env.reset()
        done = False
        
        while not done:
            # Select action based on policy
            if isinstance(policy, dict):
                action = policy[state]
            else:
                action = np.random.choice(env.action_space.n, p=policy[state])
            
            # Take action and observe result
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # TD(0) update
            td_target = reward + gamma * V[next_state]
            td_error = td_target - V[state]
            V[state] = V[state] + alpha * td_error
            
            # Move to next state
            state = next_state
        
        # Store value function if tracking
        if track_values:
            V_track.append(V.copy())
    
    if track_values:
        return V, V_track
    else:
        return V
