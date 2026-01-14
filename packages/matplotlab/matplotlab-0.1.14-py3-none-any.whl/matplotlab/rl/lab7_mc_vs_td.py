"""
RL Lab 7: Monte Carlo vs Temporal Difference Learning
======================================================

Compares Monte Carlo and TD(0) prediction methods for policy evaluation.
Analyzes convergence and value estimation differences.

Lab Objectives:
- Implement Monte Carlo prediction algorithm
- Implement TD(0) prediction algorithm
- Compare convergence rates
- Analyze value function estimates
"""

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt


def monte_carlo_prediction(env, policy, episodes=10000, gamma=0.99):
    """
    Monte Carlo prediction for policy evaluation.
    
    Updates value function only at the end of each episode using
    the actual return G_t (no bootstrapping).
    
    Parameters:
    -----------
    env : gymnasium.Env
        Environment for interaction
    policy : dict or callable
        Deterministic policy: state -> action
    episodes : int
        Number of episodes to run
    gamma : float
        Discount factor
        
    Returns:
    --------
    V : ndarray, shape (n_states,)
        Estimated value function
    V_hist : list of ndarrays
        Value function at each episode (for convergence analysis)
    """
    V = np.zeros(env.observation_space.n)
    returns = {s: [] for s in range(env.observation_space.n)}
    V_hist = []
    
    for ep in range(episodes):
        episode = []
        state, _ = env.reset()
        done = False
        
        while not done:
            action = policy[state] if isinstance(policy, dict) else policy(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            episode.append((state, reward))
            state = next_state
        
        G = 0
        visited_states = set()
        for s, r in reversed(episode):
            G = gamma * G + r
            if s not in visited_states:
                returns[s].append(G)
                V[s] = np.mean(returns[s])
                visited_states.add(s)
        
        V_hist.append(V.copy())
    
    return V, V_hist


def td0_prediction(env, policy, episodes=10000, alpha=0.05, gamma=0.99):
    """
    Temporal Difference (TD(0)) prediction for policy evaluation.
    
    Updates value function after each step using bootstrapping:
    V(s) = V(s) + alpha * (r + gamma * V(s') - V(s))
    
    Parameters:
    -----------
    env : gymnasium.Env
        Environment for interaction
    policy : dict or callable
        Deterministic policy: state -> action
    episodes : int
        Number of episodes
    alpha : float
        Learning rate (step size)
    gamma : float
        Discount factor
        
    Returns:
    --------
    V : ndarray, shape (n_states,)
        Estimated value function
    V_hist : list of ndarrays
        Value function at each episode
    """
    V = np.zeros(env.observation_space.n)
    V_hist = []
    
    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        
        while not done:
            action = policy[state] if isinstance(policy, dict) else policy(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            td_error = reward + gamma * V[next_state] - V[state]
            V[state] += alpha * td_error
            state = next_state
        
        V_hist.append(V.copy())
    
    return V, V_hist


def plot_convergence_comparison(V_mc_hist, V_td_hist, env, title_prefix=""):
    """
    Plot convergence of MC and TD value functions.
    
    Parameters:
    -----------
    V_mc_hist : list of ndarrays
        MC value history
    V_td_hist : list of ndarrays
        TD value history
    env : gymnasium.Env
        Environment (for state count)
    title_prefix : str
        Prefix for plot titles
    """
    n_states = env.observation_space.n
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    states_to_plot = [0, n_states // 3, 2 * n_states // 3, n_states - 1]
    
    for idx, state in enumerate(states_to_plot):
        ax = axes[idx // 2, idx % 2]
        mc_vals = [v[state] for v in V_mc_hist]
        td_vals = [v[state] for v in V_td_hist]
        
        ax.plot(mc_vals, label='Monte Carlo', linewidth=2)
        ax.plot(td_vals, label='TD(0)', linewidth=2)
        ax.set_title(f'{title_prefix} State {state} Convergence')
        ax.set_xlabel('Episodes')
        ax.set_ylabel('Value Estimate')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def analyze_lab7(env_name='FrozenLake-v1', is_slippery=False, episodes=5000):
    """
    Full Lab 7 analysis: Monte Carlo vs TD(0).
    
    Parameters:
    -----------
    env_name : str
        Gymnasium environment name
    is_slippery : bool
        Whether environment is slippery
    episodes : int
        Training episodes
        
    Returns:
    --------
    results : dict
        Dictionary with V_mc, V_td, V_mc_hist, V_td_hist
    """
    env = gym.make(env_name, is_slippery=is_slippery)
    
    np.random.seed(42)
    policy = {s: np.random.choice([0, 1, 2, 3]) for s in range(env.observation_space.n)}
    
    V_mc, V_mc_hist = monte_carlo_prediction(env, policy, episodes=episodes)
    V_td, V_td_hist = td0_prediction(env, policy, episodes=episodes, alpha=0.05)
    
    return {
        'V_mc': V_mc,
        'V_td': V_td,
        'V_mc_hist': V_mc_hist,
        'V_td_hist': V_td_hist,
        'env': env,
        'policy': policy
    }
