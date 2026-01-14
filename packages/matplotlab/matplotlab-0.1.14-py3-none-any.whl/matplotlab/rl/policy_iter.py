"""
Policy Iteration for Reinforcement Learning.

This module implements policy iteration algorithm, including
policy improvement and the complete policy iteration loop.
Based on Lab 5 and OEL1 implementations.
"""

import numpy as np
from .policy_eval import policy_evaluation


def q_from_v(env, V, s, gamma=1.0):
    """
    Calculate Q-values for all actions in a state from value function.
    
    Computes: Q(s,a) = sum_s',r [P(s'|s,a) * (r + gamma * V(s'))]
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment
    V : numpy.ndarray
        Value function for all states
    s : int
        State to compute Q-values for
    gamma : float, optional (default=1.0)
        Discount factor
    
    Returns:
    --------
    q : numpy.ndarray
        Q-values for each action in state s
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1')
    >>> V = np.random.rand(env.observation_space.n)
    >>> q_values = q_from_v(env, V, s=0, gamma=0.99)
    >>> print("Q-values:", q_values)
    >>> best_action = np.argmax(q_values)
    >>> print("Best action:", best_action)
    """
    nA = env.action_space.n
    P = env.unwrapped.P
    
    q = np.zeros(nA)
    
    for a in range(nA):
        for prob, next_state, reward, done in P[s][a]:
            q[a] += prob * (reward + gamma * V[next_state])
    
    return q


def policy_improvement(env, V, gamma=1.0):
    """
    Improve policy by making it greedy with respect to value function.
    
    For each state, select the action that maximizes Q(s,a).
    Returns a deterministic policy.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment
    V : numpy.ndarray
        Value function for all states
    gamma : float, optional (default=1.0)
        Discount factor
    
    Returns:
    --------
    policy : numpy.ndarray
        Improved deterministic policy, shape (nS, nA)
        policy[s, a] = 1.0 for best action, 0.0 for others
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1')
    >>> V = np.random.rand(env.observation_space.n)
    >>> policy = policy_improvement(env, V, gamma=0.99)
    >>> print("Policy shape:", policy.shape)
    >>> # Check: each state should have exactly one action with probability 1
    >>> print("Sum per state:", policy.sum(axis=1))
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    
    # Initialize deterministic policy
    policy = np.zeros([nS, nA])
    
    for s in range(nS):
        # Get Q-values for all actions
        Q = q_from_v(env, V, s, gamma)
        
        # Find best action (greedy)
        best_action = np.argmax(Q)
        
        # Set probability 1.0 for best action
        policy[s, best_action] = 1.0
    
    return policy


def policy_iteration(env, gamma=1.0, theta=1e-8, max_iterations=100):
    """
    Find optimal policy using policy iteration algorithm.
    
    Policy Iteration alternates between:
    1. Policy Evaluation: Compute V for current policy
    2. Policy Improvement: Make policy greedy w.r.t. V
    
    Stops when policy becomes stable (no changes).
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment with discrete spaces
    gamma : float, optional (default=1.0)
        Discount factor
    theta : float, optional (default=1e-8)
        Convergence threshold for policy evaluation
    max_iterations : int, optional (default=100)
        Maximum number of policy iteration steps
    
    Returns:
    --------
    policy : numpy.ndarray
        Optimal policy, shape (nS, nA)
    V : numpy.ndarray
        Optimal value function
    iterations : int
        Number of iterations until convergence
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> env = gym.make('FrozenLake-v1', is_slippery=True)
    >>> policy, V, iterations = policy_iteration(env, gamma=0.99)
    >>> print(f"Converged in {iterations} iterations")
    >>> print("Optimal policy shape:", policy.shape)
    >>> print("Value of start state:", V[0])
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    
    # Start with uniform random policy
    policy = np.ones([nS, nA]) / nA
    
    iteration_count = 0
    
    while iteration_count < max_iterations:
        # Step 1: Policy Evaluation
        V = policy_evaluation(env, policy, gamma, theta)
        
        # Step 2: Policy Improvement
        new_policy = policy_improvement(env, V, gamma)
        
        # Check if policy is stable (no changes)
        policy_stable = np.array_equal(policy, new_policy)
        
        # Update policy
        policy = new_policy
        
        iteration_count += 1
        
        if policy_stable:
            break
    
    return policy, V, iteration_count
