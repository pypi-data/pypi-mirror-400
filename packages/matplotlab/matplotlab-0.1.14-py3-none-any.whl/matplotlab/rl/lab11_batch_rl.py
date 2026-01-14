"""
RL Lab 11: Batch RL and Parameter Sensitivity Analysis
=======================================================

Analyzes effects of discount factor (gamma), batch size, and lambda parameter
in eligibility trace methods. Compares MC, TD(0), and TD(lambda).

Lab Objectives:
- Understand batch learning approaches
- Analyze discount factor effects
- Study TD(lambda) with eligibility traces
- Compare convergence properties
"""

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt


def batch_monte_carlo(episodes=500, gamma=0.99):
    """
    Batch Monte Carlo prediction.
    
    Collects all episodes then updates values based on complete returns.
    
    Parameters:
    -----------
    episodes : int
        Number of episodes
    gamma : float
        Discount factor
        
    Returns:
    --------
    V : ndarray
        Value function
    mse_history : ndarray
        MSE per batch update
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)
    V = np.zeros(env.observation_space.n)
    returns = {s: [] for s in range(env.observation_space.n)}
    mse_history = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        trajectory = []
        done = False
        
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            trajectory.append((state, reward))
            state = next_state
        
        G = 0
        for state, reward in reversed(trajectory):
            G = reward + gamma * G
            returns[state].append(G)
    
    for state in range(env.observation_space.n):
        if returns[state]:
            V[state] = np.mean(returns[state])
            mse = np.mean((np.array(returns[state]) - V[state])**2)
            mse_history.append(mse)
    
    return V, np.array(mse_history)


def batch_td_zero(episodes=500, alpha=0.1, gamma=0.99):
    """
    Batch TD(0) prediction.
    
    Updates value after each episode using bootstrapped estimates.
    
    Parameters:
    -----------
    episodes : int
        Number of episodes
    alpha : float
        Learning rate
    gamma : float
        Discount factor
        
    Returns:
    --------
    V : ndarray
        Value function
    mse_history : ndarray
        MSE per episode
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)
    V = np.zeros(env.observation_space.n)
    mse_history = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            v_curr = V[state]
            v_next = V[next_state]
            td_error = reward + gamma * v_next - v_curr
            V[state] += alpha * td_error
            
            mse = td_error ** 2
            mse_history.append(mse)
            state = next_state
    
    return V, np.array(mse_history)


def batch_td_lambda(episodes=500, alpha=0.1, gamma=0.99, lambda_=0.5):
    """
    Batch TD(lambda) with eligibility traces.
    
    Combines TD bootstrapping with MC return information via traces.
    
    Parameters:
    -----------
    episodes : int
        Number of episodes
    alpha : float
        Learning rate
    gamma : float
        Discount factor
    lambda_ : float
        Eligibility trace decay (0=TD(0), 1=MC)
        
    Returns:
    --------
    V : ndarray
        Value function
    mse_history : ndarray
        MSE per episode
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)
    V = np.zeros(env.observation_space.n)
    mse_history = []
    
    for episode in range(episodes):
        e = np.zeros(env.observation_space.n)
        state, _ = env.reset()
        done = False
        
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            e[state] += 1
            v_curr = V[state]
            v_next = V[next_state]
            td_error = reward + gamma * v_next - v_curr
            
            V += alpha * td_error * e
            e *= gamma * lambda_
            
            mse_history.append(td_error ** 2)
            state = next_state
    
    return V, np.array(mse_history)


def discount_factor_analysis(gammas=[0.5, 0.7, 0.9, 0.99]):
    """
    Analyze effect of discount factor on different algorithms.
    
    Parameters:
    -----------
    gammas : list
        Discount factors to test
        
    Returns:
    --------
    results : dict
        Value functions for each method and gamma
    """
    results = {
        'mc': {},
        'td0': {},
        'tdlambda': {}
    }
    
    for gamma in gammas:
        print(f"  gamma={gamma}...", end=' ')
        V_mc, _ = batch_monte_carlo(episodes=200, gamma=gamma)
        V_td, _ = batch_td_zero(episodes=200, alpha=0.1, gamma=gamma)
        V_tl, _ = batch_td_lambda(episodes=200, alpha=0.1, gamma=gamma, lambda_=0.5)
        
        results['mc'][gamma] = V_mc
        results['td0'][gamma] = V_td
        results['tdlambda'][gamma] = V_tl
        print("done")
    
    return results


def lambda_sensitivity_analysis(lambdas=[0.0, 0.2, 0.5, 0.8, 1.0]):
    """
    Analyze TD(lambda) sensitivity to lambda parameter.
    
    Parameters:
    -----------
    lambdas : list
        Lambda values to test
        
    Returns:
    --------
    results : dict
        Convergence metrics for each lambda
    """
    results = {}
    
    for lam in lambdas:
        print(f"  lambda={lam}...", end=' ')
        V, mse_hist = batch_td_lambda(episodes=300, alpha=0.1, gamma=0.99, lambda_=lam)
        mean_mse = np.mean(mse_hist[-50:])
        results[lam] = {
            'V': V,
            'mse_history': mse_hist,
            'final_mse': mean_mse
        }
        print(f"final MSE: {mean_mse:.4f}")
    
    return results


def convergence_analysis(max_episodes=500):
    """
    Detailed convergence analysis of batch algorithms.
    
    Parameters:
    -----------
    max_episodes : int
        Maximum episodes to simulate
        
    Returns:
    --------
    results : dict
        Convergence trajectories
    """
    print("Computing convergence trajectories...")
    
    episode_milestones = [50, 100, 200, 300, 500]
    results = {'mc': [], 'td0': [], 'tdlambda': []}
    
    for eps in episode_milestones:
        V_mc, _ = batch_monte_carlo(episodes=eps)
        V_td, _ = batch_td_zero(episodes=eps, alpha=0.1)
        V_tl, _ = batch_td_lambda(episodes=eps, alpha=0.1, lambda_=0.5)
        
        results['mc'].append(V_mc)
        results['td0'].append(V_td)
        results['tdlambda'].append(V_tl)
    
    return results, episode_milestones


def plot_discount_factor_effect(results):
    """
    Plot discount factor effects on algorithms.
    
    Parameters:
    -----------
    results : dict
        Results from discount_factor_analysis()
    """
    gammas = list(results['mc'].keys())
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    for i, method_key in enumerate(['mc', 'td0', 'tdlambda']):
        mean_values = []
        for gamma in gammas:
            mean_values.append(np.mean(results[method_key][gamma]))
        
        axes[i].bar(range(len(gammas)), mean_values, color='steelblue')
        axes[i].set_xticks(range(len(gammas)))
        axes[i].set_xticklabels([f'{g}' for g in gammas])
        axes[i].set_xlabel('Discount Factor (gamma)')
        axes[i].set_ylabel('Mean Value')
        axes[i].set_title(f'{method_key.upper()} - Gamma Effect')
        axes[i].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_lambda_analysis(results):
    """
    Plot TD(lambda) lambda sensitivity.
    
    Parameters:
    -----------
    results : dict
        Results from lambda_sensitivity_analysis()
    """
    lambdas = sorted(results.keys())
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for lam in lambdas:
        axes[0].plot(results[lam]['mse_history'], label=f'λ={lam}', alpha=0.7, linewidth=2)
    
    axes[0].set_xlabel('Step')
    axes[0].set_ylabel('MSE')
    axes[0].set_title('TD(λ) Convergence for Different Lambda Values')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim([0, 0.5])
    
    final_mses = [results[lam]['final_mse'] for lam in lambdas]
    axes[1].plot(lambdas, final_mses, marker='o', linewidth=2, markersize=8)
    axes[1].set_xlabel('Lambda')
    axes[1].set_ylabel('Final MSE')
    axes[1].set_title('TD(λ) Final Performance vs Lambda')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_convergence_comparison(conv_results, milestones):
    """
    Plot convergence trajectories.
    
    Parameters:
    -----------
    conv_results : dict
        Results from convergence_analysis()
    milestones : list
        Episode milestones
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    
    for i, eps in enumerate(milestones):
        row = i // 3
        col = i % 3
        
        V_mc = conv_results['mc'][i]
        V_td = conv_results['td0'][i]
        V_tl = conv_results['tdlambda'][i]
        
        x = np.arange(len(V_mc))
        width = 0.25
        
        axes[row, col].bar(x - width, V_mc, width, label='MC', alpha=0.8)
        axes[row, col].bar(x, V_td, width, label='TD(0)', alpha=0.8)
        axes[row, col].bar(x + width, V_tl, width, label='TD(λ)', alpha=0.8)
        
        axes[row, col].set_title(f'After {eps} Episodes')
        axes[row, col].set_ylabel('Value')
        axes[row, col].legend()
        axes[row, col].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def analyze_lab11():
    """
    Run complete Lab 11 analysis.
    
    Returns:
    --------
    results : dict
        All analysis results
    """
    print("Lab 11: Batch RL and Parameter Sensitivity")
    print("-" * 50)
    
    print("\n1. Discount Factor Analysis:")
    gamma_results = discount_factor_analysis(gammas=[0.5, 0.7, 0.9, 0.99])
    
    print("\n2. TD(λ) Lambda Sensitivity:")
    lambda_results = lambda_sensitivity_analysis(lambdas=[0.0, 0.2, 0.5, 0.8, 1.0])
    
    print("\n3. Convergence Analysis:")
    conv_results, milestones = convergence_analysis(max_episodes=500)
    
    print("\nSummary:")
    for lam, data in lambda_results.items():
        print(f"  λ={lam}: Final MSE = {data['final_mse']:.4f}")
    
    return {
        'gamma_analysis': gamma_results,
        'lambda_analysis': lambda_results,
        'convergence': (conv_results, milestones)
    }
