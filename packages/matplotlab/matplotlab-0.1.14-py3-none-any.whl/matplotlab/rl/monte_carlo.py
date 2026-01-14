"""
Monte Carlo methods for Reinforcement Learning.

This module implements Monte Carlo prediction for value estimation,
including support for both custom MDPs and Gymnasium environments.
Based on Lab 3 and Lab 7 implementations.
"""

import numpy as np


def sample_episode(P, S, s=0, log=True):
    """
    Sample a single episode from an MDP using transition matrix.
    
    This function generates an episode by randomly sampling
    next states according to the transition probability matrix.
    The episode continues until a terminal state is reached.
    
    Parameters:
    -----------
    P : numpy.ndarray
        Transition probability matrix (states x states)
    S : list
        List of state names/labels
    s : int, optional (default=0)
        Starting state index
    log : bool, optional (default=True)
        Whether to print the episode path
    
    Returns:
    --------
    episode : numpy.ndarray
        Array of state indices representing the episode
    
    Example:
    --------
    >>> import numpy as np
    >>> S = ['c1', 'c2', 'c3', 'pass', 'rest', 'tv', 'sleep']
    >>> P = np.array([[0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0],
    ...               [0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.2],
    ...               [0.0, 0.0, 0.0, 0.6, 0.4, 0.0, 0.0],
    ...               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    ...               [0.2, 0.4, 0.4, 0.0, 0.0, 0.0, 0.0],
    ...               [0.1, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0],
    ...               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]])
    >>> episode = sample_episode(P, S, s=0)
    """
    print_str = S[s] + ', '
    episode = [s]
    
    # Continue until terminal state (last state in S is terminal)
    terminal_state = S[-1]
    while S[episode[-1]] != terminal_state:
        # Sample next state based on transition probabilities
        next_s = np.random.choice(len(P), 1, p=P[episode[-1]])[0]
        episode.append(next_s)
        print_str += str(S[episode[-1]]) + ', '
    
    if log:
        print(print_str)
    
    return np.array(episode)


def compute_return(episode_rewards, gamma):
    """
    Compute the total discounted return for an episode.
    
    G_t = R_t + gamma*R_{t+1} + gamma^2*R_{t+2} + ...
    
    Parameters:
    -----------
    episode_rewards : numpy.ndarray or list
        Rewards received at each timestep
    gamma : float
        Discount factor (0 to 1)
    
    Returns:
    --------
    G_t : float
        Total discounted return
    
    Example:
    --------
    >>> rewards = np.array([-2, -2, 10, 0])
    >>> G = compute_return(rewards, gamma=0.9)
    >>> print(f"Return: {G:.2f}")
    """
    G_t = 0
    for k in range(len(episode_rewards)):
        G_t += (gamma ** k) * episode_rewards[k]
    return G_t


def mc_value_estimation_mdp(P, S, R, gamma=0.9, num_episodes=2000, verbose=True):
    """
    Estimate state values using Monte Carlo method for matrix-based MDP.
    
    This implements first-visit Monte Carlo for value estimation
    by averaging returns from multiple episodes starting from each state.
    
    Parameters:
    -----------
    P : numpy.ndarray
        Transition probability matrix (states x states)
    S : list
        List of state names/labels
    R : numpy.ndarray
        Reward array for each state
    gamma : float, optional (default=0.9)
        Discount factor
    num_episodes : int, optional (default=2000)
        Number of episodes to sample for estimation
    verbose : bool, optional (default=True)
        Whether to print progress every 100 episodes
    
    Returns:
    --------
    V : numpy.ndarray
        Estimated value function for each state
    
    Example:
    --------
    >>> import numpy as np
    >>> S = ['c1', 'c2', 'c3', 'pass', 'rest', 'tv', 'sleep']
    >>> R = np.array([-2, -2, -2, +10, +1, -1, 0])
    >>> P = np.array([[0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0],
    ...               [0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.2],
    ...               [0.0, 0.0, 0.0, 0.6, 0.4, 0.0, 0.0],
    ...               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    ...               [0.2, 0.4, 0.4, 0.0, 0.0, 0.0, 0.0],
    ...               [0.1, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0],
    ...               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]])
    >>> V = mc_value_estimation_mdp(P, S, R, gamma=0.9, num_episodes=1000)
    >>> print("Value estimates:", V)
    """
    V = np.zeros(len(P))
    
    for i in range(num_episodes):
        # Sample episode from each state
        for s in range(len(P)):
            episode = sample_episode(P, S, s, log=False)
            episode_rewards = R[episode]
            
            # Compute return for this episode
            G_t = compute_return(episode_rewards, gamma)
            V[s] += G_t
        
        # Print progress
        if verbose and (i + 1) % 100 == 0:
            np.set_printoptions(precision=2)
            print(f"Episode {i+1}: {V / (i + 1)}")
    
    # Average over all episodes
    V = V / num_episodes
    return V


def analytical_solution(P, R, gamma):
    """
    Compute exact value function using analytical solution.
    
    Solves: V = (I - gamma*P)^(-1) * R
    
    This provides the ground truth value function for comparison
    with Monte Carlo estimates.
    
    Parameters:
    -----------
    P : numpy.ndarray
        Transition probability matrix
    R : numpy.ndarray
        Reward array
    gamma : float
        Discount factor
    
    Returns:
    --------
    V : numpy.ndarray
        Exact value function
    
    Example:
    --------
    >>> import numpy as np
    >>> P = np.array([[0.5, 0.5], [0.3, 0.7]])
    >>> R = np.array([1.0, -1.0])
    >>> V = analytical_solution(P, R, gamma=0.9)
    >>> print("Exact values:", V)
    """
    I = np.identity(len(P))
    V = np.linalg.solve(I - gamma * P, R)
    return V


def mc_prediction(env, policy, num_episodes=1000, gamma=0.99, first_visit=True):
    """
    Monte Carlo prediction for estimating V(s) under a given policy.
    
    This implements Monte Carlo policy evaluation for Gymnasium environments.
    Works with any discrete observation space environment.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Gymnasium environment with discrete observation space
    policy : numpy.ndarray or dict
        Policy to evaluate. Can be:
        - Array of shape (nS, nA) with action probabilities
        - Dict mapping state -> action
    num_episodes : int, optional (default=1000)
        Number of episodes to sample
    gamma : float, optional (default=0.99)
        Discount factor
    first_visit : bool, optional (default=True)
        If True, use first-visit MC; else use every-visit MC
    
    Returns:
    --------
    V : numpy.ndarray
        Estimated value function for each state
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1', is_slippery=True)
    >>> # Random policy
    >>> policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n
    >>> V = mc_prediction(env, policy, num_episodes=5000)
    >>> print("State values:", V)
    """
    nS = env.observation_space.n
    
    # Initialize
    returns_sum = np.zeros(nS)
    returns_count = np.zeros(nS)
    V = np.zeros(nS)
    
    for episode_num in range(num_episodes):
        # Generate episode
        episode_states = []
        episode_rewards = []
        
        state, _ = env.reset()
        done = False
        
        while not done:
            episode_states.append(state)
            
            # Select action based on policy
            if isinstance(policy, dict):
                action = policy[state]
            else:
                action = np.random.choice(env.action_space.n, p=policy[state])
            
            state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            episode_rewards.append(reward)
        
        # Calculate returns for each state in episode
        G = 0
        visited_states = set()
        
        for t in range(len(episode_states) - 1, -1, -1):
            state_t = episode_states[t]
            reward_t = episode_rewards[t]
            G = gamma * G + reward_t
            
            # First-visit MC: only count first occurrence
            if first_visit and state_t in visited_states:
                continue
            
            visited_states.add(state_t)
            returns_sum[state_t] += G
            returns_count[state_t] += 1
    
    # Calculate average returns
    for s in range(nS):
        if returns_count[s] > 0:
            V[s] = returns_sum[s] / returns_count[s]
    
    return V
