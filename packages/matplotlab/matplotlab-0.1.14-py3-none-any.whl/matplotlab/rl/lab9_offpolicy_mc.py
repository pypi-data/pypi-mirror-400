"""
RL Lab 9: Off-Policy Learning and Importance Sampling
======================================================

Implements off-policy Monte Carlo with importance sampling,
compares with Q-Learning, and analyzes variance.

Lab Objectives:
- Understand off-policy learning
- Implement importance sampling (weighted and ordinary)
- Compare off-policy MC vs Q-Learning
- Analyze variance properties
"""

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt


def ordinary_importance_sampling(episodes=1000, gamma=0.99):
    """
    Off-Policy Monte Carlo with Ordinary Importance Sampling.
    
    Uses Blackjack environment. Target policy: stick on 20+.
    Behavior policy: random.
    
    Parameters:
    -----------
    episodes : int
        Number of episodes
    gamma : float
        Discount factor
        
    Returns:
    --------
    V : ndarray
        Value function for dealer upcard (12-21)
    V_history : ndarray, shape (episodes,)
        Mean absolute value change per episode
    """
    env = gym.make('Blackjack-v1')
    V = np.zeros((22, 11))
    counts = np.zeros((22, 11))
    V_history = np.zeros(episodes)
    
    for episode in range(episodes):
        trajectory = []
        state, _ = env.reset()
        done = False
        
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            trajectory.append((state, action, reward))
            state = next_state
        
        G = 0
        W = 1.0
        
        for t in range(len(trajectory) - 1, -1, -1):
            state, action, reward = trajectory[t]
            player_sum, dealer_card, has_ace = state
            
            G = reward + gamma * G
            
            counts[player_sum, dealer_card] += W
            V[player_sum, dealer_card] += W * (G - V[player_sum, dealer_card]) / counts[player_sum, dealer_card]
            
            target_action = 0 if player_sum >= 20 else 1
            if action != target_action:
                break
            
            W *= 1.0 / 0.5
        
        V_history[episode] = np.sum(np.abs(np.diff(V.flatten()))) / 100
    
    return V, V_history


def weighted_importance_sampling(episodes=1000, gamma=0.99):
    """
    Off-Policy Monte Carlo with Weighted Importance Sampling.
    
    Uses Blackjack environment. Target policy: stick on 20+.
    Behavior policy: random.
    
    Parameters:
    -----------
    episodes : int
        Number of episodes
    gamma : float
        Discount factor
        
    Returns:
    --------
    V : ndarray
        Value function for dealer upcard (12-21)
    V_history : ndarray, shape (episodes,)
        Mean value change per episode
    """
    env = gym.make('Blackjack-v1')
    V = np.zeros((22, 11))
    W_sum = np.zeros((22, 11))
    V_history = np.zeros(episodes)
    
    for episode in range(episodes):
        trajectory = []
        state, _ = env.reset()
        done = False
        
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            trajectory.append((state, action, reward))
            state = next_state
        
        G = 0
        W = 1.0
        
        for t in range(len(trajectory) - 1, -1, -1):
            state, action, reward = trajectory[t]
            player_sum, dealer_card, has_ace = state
            
            G = reward + gamma * G
            
            W_sum[player_sum, dealer_card] += W
            if W_sum[player_sum, dealer_card] > 0:
                V[player_sum, dealer_card] += W * G / W_sum[player_sum, dealer_card]
            
            target_action = 0 if player_sum >= 20 else 1
            if action != target_action:
                break
            
            W *= 1.0 / 0.5
        
        V_history[episode] = np.sum(np.abs(np.diff(V.flatten()))) / 100
    
    return V, V_history


def q_learning_blackjack(episodes=500, alpha=0.1, gamma=0.99, epsilon=0.1):
    """
    Q-Learning on Blackjack for comparison with off-policy MC.
    
    Parameters:
    -----------
    episodes : int
        Training episodes
    alpha : float
        Learning rate
    gamma : float
        Discount factor
    epsilon : float
        Exploration rate
        
    Returns:
    --------
    Q : dict
        Q-table (state -> action values)
    rewards : ndarray
        Rewards per episode
    """
    env = gym.make('Blackjack-v1')
    Q = {}
    rewards = np.zeros(episodes)
    
    def get_q(state, action):
        key = (state, action)
        return Q.get(key, 0.0)
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            if np.random.random() < epsilon:
                action = env.action_space.sample()
            else:
                q0 = get_q(state, 0)
                q1 = get_q(state, 1)
                action = 0 if q0 >= q1 else 1
            
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            q_curr = get_q(state, action)
            q_next_0 = get_q(next_state, 0)
            q_next_1 = get_q(next_state, 1)
            q_next_max = max(q_next_0, q_next_1)
            
            new_q = q_curr + alpha * (reward + gamma * q_next_max - q_curr)
            Q[(state, action)] = new_q
            
            state = next_state
            episode_reward += reward
        
        rewards[episode] = episode_reward
    
    return Q, rewards


def variance_analysis_is(n_runs=10, episodes=500):
    """
    Analyze variance of importance sampling estimators.
    
    Compares ordinary vs weighted importance sampling variance.
    
    Parameters:
    -----------
    n_runs : int
        Number of independent runs
    episodes : int
        Episodes per run
        
    Returns:
    --------
    ois_results : list
        OIS value estimates per run
    wis_results : list
        WIS value estimates per run
    """
    ois_results = []
    wis_results = []
    
    for run in range(n_runs):
        V_ois, _ = ordinary_importance_sampling(episodes=episodes)
        V_wis, _ = weighted_importance_sampling(episodes=episodes)
        
        ois_results.append(V_ois.flatten())
        wis_results.append(V_wis.flatten())
    
    ois_results = np.array(ois_results)
    wis_results = np.array(wis_results)
    
    return ois_results, wis_results


def plot_offpolicy_comparison():
    """
    Plot comparison of off-policy methods.
    
    Visualizes ordinary vs weighted importance sampling and Q-Learning.
    """
    print("Computing ordinary importance sampling...")
    V_ois, hist_ois = ordinary_importance_sampling(episodes=500)
    
    print("Computing weighted importance sampling...")
    V_wis, hist_wis = weighted_importance_sampling(episodes=500)
    
    print("Computing Q-Learning...")
    Q_ql, rewards_ql = q_learning_blackjack(episodes=500)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Convergence comparison
    axes[0, 0].plot(hist_ois, label='Ordinary IS', linewidth=2)
    axes[0, 0].plot(hist_wis, label='Weighted IS', linewidth=2)
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Value Change')
    axes[0, 0].set_title('Convergence: OIS vs WIS')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # OIS value function
    axes[0, 1].imshow(V_ois[11:22, :], aspect='auto', cmap='viridis')
    axes[0, 1].set_xlabel('Dealer Card')
    axes[0, 1].set_ylabel('Player Sum (11+)')
    axes[0, 1].set_title('Ordinary Importance Sampling Value Function')
    plt.colorbar(axes[0, 1].images[0], ax=axes[0, 1])
    
    # WIS value function
    axes[1, 0].imshow(V_wis[11:22, :], aspect='auto', cmap='viridis')
    axes[1, 0].set_xlabel('Dealer Card')
    axes[1, 0].set_ylabel('Player Sum (11+)')
    axes[1, 0].set_title('Weighted Importance Sampling Value Function')
    plt.colorbar(axes[1, 0].images[0], ax=axes[1, 0])
    
    # Q-Learning rewards
    axes[1, 1].plot(rewards_ql, label='Q-Learning', linewidth=2)
    axes[1, 1].set_xlabel('Episode')
    axes[1, 1].set_ylabel('Total Reward')
    axes[1, 1].set_title('Q-Learning Episode Rewards')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def variance_analysis_comparison():
    """
    Analyze and plot variance of IS estimators.
    """
    print("Running variance analysis (10 independent runs)...")
    ois_results, wis_results = variance_analysis_is(n_runs=10, episodes=300)
    
    ois_mean = np.mean(ois_results, axis=0)
    ois_std = np.std(ois_results, axis=0)
    wis_mean = np.mean(wis_results, axis=0)
    wis_std = np.std(wis_results, axis=0)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].bar(['OIS', 'WIS'], [np.mean(ois_std), np.mean(wis_std)], color=['blue', 'orange'])
    axes[0].set_ylabel('Mean Standard Deviation')
    axes[0].set_title('Variance Comparison: OIS vs WIS')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    axes[1].plot(ois_mean, label='OIS Mean', linewidth=2)
    axes[1].fill_between(range(len(ois_mean)), 
                        ois_mean - ois_std, 
                        ois_mean + ois_std, 
                        alpha=0.3, label='OIS ±1 std')
    axes[1].plot(wis_mean, label='WIS Mean', linewidth=2)
    axes[1].fill_between(range(len(wis_mean)), 
                        wis_mean - wis_std, 
                        wis_mean + wis_std, 
                        alpha=0.3, label='WIS ±1 std')
    axes[1].set_xlabel('State Index')
    axes[1].set_ylabel('Value Estimate')
    axes[1].set_title('Value Estimates with Uncertainty Bands')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def analyze_lab9():
    """
    Run complete Lab 9 analysis.
    
    Returns:
    --------
    results : dict
        Dictionary with all analysis results
    """
    print("Lab 9: Off-Policy Learning and Importance Sampling")
    print("-" * 50)
    
    print("1. Ordinary Importance Sampling...")
    V_ois, hist_ois = ordinary_importance_sampling(episodes=300)
    print(f"   OIS converged: mean value = {np.mean(V_ois[11:22]):.4f}")
    
    print("2. Weighted Importance Sampling...")
    V_wis, hist_wis = weighted_importance_sampling(episodes=300)
    print(f"   WIS converged: mean value = {np.mean(V_wis[11:22]):.4f}")
    
    print("3. Q-Learning...")
    Q_ql, rewards_ql = q_learning_blackjack(episodes=300)
    print(f"   QL final reward: {rewards_ql[-1]:.2f}")
    
    print("4. Variance Analysis...")
    ois_results, wis_results = variance_analysis_is(n_runs=5, episodes=200)
    ois_var = np.std(np.mean(ois_results, axis=1))
    wis_var = np.std(np.mean(wis_results, axis=1))
    print(f"   OIS variance: {ois_var:.4f}")
    print(f"   WIS variance: {wis_var:.4f}")
    
    return {
        'V_ois': V_ois,
        'V_wis': V_wis,
        'Q_ql': Q_ql,
        'rewards_ql': rewards_ql,
        'ois_variance': ois_var,
        'wis_variance': wis_var
    }
