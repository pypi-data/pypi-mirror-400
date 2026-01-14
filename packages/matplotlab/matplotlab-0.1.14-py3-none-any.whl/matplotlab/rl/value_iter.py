"""
Value Iteration for Reinforcement Learning.

This module implements the value iteration algorithm for finding
optimal policies in MDPs. Based on Lab 6 implementations.
"""

import numpy as np


def value_iteration(env, gamma=0.99, theta=1e-6, max_iterations=10000):
    """
    Find optimal value function and policy using value iteration.
    
    Value iteration computes the optimal value function by repeatedly
    applying the Bellman optimality backup:
    V(s) = max_a [ sum_s',r [ P(s'|s,a) * (r + gamma * V(s')) ] ]
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment with discrete spaces
    gamma : float, optional (default=0.99)
        Discount factor
    theta : float, optional (default=1e-6)
        Convergence threshold (stops when max value change < theta)
    max_iterations : int, optional (default=10000)
        Maximum number of iterations
    
    Returns:
    --------
    V : numpy.ndarray
        Optimal value function
    policy : numpy.ndarray
        Optimal policy extracted from V, shape (nS, nA)
    iterations : int
        Number of iterations until convergence
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> env = gym.make('FrozenLake-v1')
    >>> V, policy, iterations = value_iteration(env, gamma=0.99)
    >>> print(f"Converged in {iterations} iterations")
    >>> print("Optimal value of start state:", V[0])
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    P = env.unwrapped.P
    V = np.zeros(nS)
    
    for i in range(max_iterations):
        delta = 0
        
        for s in range(nS):
            # Compute Q-values for all actions
            q_sa = np.zeros(nA)
            for a in range(nA):
                for prob, next_state, reward, done in P[s][a]:
                    q_sa[a] += prob * (reward + gamma * V[next_state])
            
            # Take maximum Q-value (Bellman optimality)
            new_v = np.max(q_sa)
            delta = max(delta, abs(new_v - V[s]))
            V[s] = new_v
        
        # Check convergence
        if delta < theta:
            break
    
    # Extract optimal policy
    policy = extract_policy_from_v(env, V, gamma)
    
    return V, policy, i + 1


def extract_policy_from_v(env, V, gamma=0.99):
    """
    Extract greedy policy from value function.
    
    For each state, select the action that maximizes expected value:
    pi(s) = argmax_a [ sum_s',r [ P(s'|s,a) * (r + gamma * V(s')) ] ]
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment
    V : numpy.ndarray
        Value function
    gamma : float, optional (default=0.99)
        Discount factor
    
    Returns:
    --------
    policy : numpy.ndarray
        Deterministic policy, shape (nS, nA)
        policy[s, a] = 1.0 for best action, 0.0 for others
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1')
    >>> V = np.random.rand(env.observation_space.n)
    >>> policy = extract_policy_from_v(env, V, gamma=0.99)
    >>> print("Policy shape:", policy.shape)
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    P = env.unwrapped.P
    policy = np.zeros((nS, nA))
    
    for s in range(nS):
        # Compute Q-values
        q_sa = np.zeros(nA)
        for a in range(nA):
            for prob, next_state, reward, done in P[s][a]:
                q_sa[a] += prob * (reward + gamma * V[next_state])
        
        # Select best action
        best_a = np.argmax(q_sa)
        policy[s] = np.eye(nA)[best_a]
    
    return policy


def evaluate_policy(env, policy, n_episodes=1000):
    """
    Evaluate a policy by running episodes and measuring success rate.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment
    policy : numpy.ndarray
        Policy to evaluate, shape (nS, nA)
    n_episodes : int, optional (default=1000)
        Number of episodes to run
    
    Returns:
    --------
    success_rate : float
        Fraction of episodes that reached a positive reward
    avg_steps : float
        Average steps per successful episode
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('Taxi-v3')
    >>> # Random policy for demonstration
    >>> nS = env.observation_space.n
    >>> nA = env.action_space.n
    >>> policy = np.ones((nS, nA)) / nA
    >>> success_rate, avg_steps = evaluate_policy(env, policy, n_episodes=100)
    >>> print(f"Success rate: {success_rate*100:.1f}%")
    >>> print(f"Average steps: {avg_steps:.1f}")
    """
    wins = 0
    total_steps = 0
    win_steps = 0
    
    for _ in range(n_episodes):
        s, _ = env.reset()
        steps = 0
        finished = False
        
        while not finished:
            # Select action from policy
            a = np.argmax(policy[s])
            s, r, terminated, truncated, _ = env.step(a)
            steps += 1
            finished = terminated or truncated
            
            # Check for success (positive reward)
            if r > 0:
                wins += 1
                win_steps += steps
                break
        
        total_steps += steps
    
    success_rate = wins / n_episodes
    avg_steps = win_steps / wins if wins > 0 else 0
    
    return success_rate, avg_steps


def value_iteration_with_delta(env, gamma=0.99, theta=1e-6, max_iterations=10000):
    """
    Value iteration that also tracks convergence delta per iteration.
    
    Useful for analyzing convergence behavior and plotting convergence curves.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment
    gamma : float, optional (default=0.99)
        Discount factor
    theta : float, optional (default=1e-6)
        Convergence threshold
    max_iterations : int, optional (default=10000)
        Maximum number of iterations
    
    Returns:
    --------
    V : numpy.ndarray
        Optimal value function
    policy : numpy.ndarray
        Optimal policy
    iterations : int
        Number of iterations until convergence
    deltas : list
        List of maximum delta values per iteration
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import matplotlib.pyplot as plt
    >>> env = gym.make('FrozenLake-v1')
    >>> V, policy, iters, deltas = value_iteration_with_delta(env)
    >>> plt.plot(deltas)
    >>> plt.yscale('log')
    >>> plt.xlabel('Iteration')
    >>> plt.ylabel('Max Delta')
    >>> plt.title('Value Iteration Convergence')
    >>> plt.show()
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    P = env.unwrapped.P
    V = np.zeros(nS)
    deltas = []
    
    for iteration in range(max_iterations):
        delta = 0
        
        for s in range(nS):
            q = np.zeros(nA)
            for a in range(nA):
                for prob, next_state, reward, done in P[s][a]:
                    q[a] += prob * (reward + gamma * V[next_state])
            
            new_v = np.max(q)
            delta = max(delta, abs(new_v - V[s]))
            V[s] = new_v
        
        deltas.append(delta)
        
        if delta < theta:
            break
    
    policy = extract_policy_from_v(env, V, gamma)
    
    return V, policy, len(deltas), deltas
