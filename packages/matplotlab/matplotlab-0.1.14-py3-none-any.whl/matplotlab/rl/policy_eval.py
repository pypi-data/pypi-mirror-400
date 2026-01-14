"""
Policy Evaluation for Reinforcement Learning.

This module implements policy evaluation using the Bellman expectation equation.
Based on Lab 4 implementations.
"""

import numpy as np


def policy_evaluation(env, policy, gamma=1.0, theta=1e-8, max_iterations=1000):
    """
    Evaluate a policy by computing the value function V(s).
    
    Uses iterative policy evaluation with the Bellman expectation equation:
    V(s) = sum_a [pi(a|s) * sum_s',r [P(s'|s,a) * (r + gamma * V(s'))]]
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment with discrete observation/action spaces
    policy : numpy.ndarray
        Policy to evaluate, shape (nS, nA) with action probabilities
    gamma : float, optional (default=1.0)
        Discount factor
    theta : float, optional (default=1e-8)
        Convergence threshold for stopping
    max_iterations : int, optional (default=1000)
        Maximum number of iterations to prevent infinite loops
    
    Returns:
    --------
    V : numpy.ndarray
        Estimated value function for each state
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1', is_slippery=True)
    >>> nS = env.observation_space.n
    >>> nA = env.action_space.n
    >>> # Random policy
    >>> policy = np.ones([nS, nA]) / nA
    >>> V = policy_evaluation(env, policy, gamma=0.99)
    >>> print("State values:", V)
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    V = np.zeros(nS)
    P = env.unwrapped.P
    
    iteration = 0
    while iteration < max_iterations:
        delta = 0
        
        # Update each state
        for s in range(nS):
            v_old = V[s]
            v_new = 0
            
            # Sum over all actions
            for a in range(nA):
                action_prob = policy[s][a]
                
                # Sum over all possible next states
                for prob, next_state, reward, done in P[s][a]:
                    v_new += action_prob * prob * (reward + gamma * V[next_state])
            
            V[s] = v_new
            delta = max(delta, abs(v_old - V[s]))
        
        iteration += 1
        
        # Check convergence
        if delta < theta:
            break
    
    return V


def bellman_expectation_backup(env, V, policy, s, gamma=1.0):
    """
    Perform a single Bellman expectation backup for a state.
    
    Computes: V(s) = sum_a [pi(a|s) * Q(s,a)]
    Where: Q(s,a) = sum_s',r [P(s'|s,a) * (r + gamma * V(s'))]
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment
    V : numpy.ndarray
        Current value function
    policy : numpy.ndarray
        Policy array (nS, nA)
    s : int
        State to update
    gamma : float, optional (default=1.0)
        Discount factor
    
    Returns:
    --------
    v : float
        Updated value for state s
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1')
    >>> nS = env.observation_space.n
    >>> nA = env.action_space.n
    >>> policy = np.ones([nS, nA]) / nA
    >>> V = np.zeros(nS)
    >>> new_v = bellman_expectation_backup(env, V, policy, s=0, gamma=0.99)
    """
    nA = env.action_space.n
    P = env.unwrapped.P
    
    v = 0
    for a in range(nA):
        action_prob = policy[s][a]
        
        for prob, next_state, reward, done in P[s][a]:
            v += action_prob * prob * (reward + gamma * V[next_state])
    
    return v
