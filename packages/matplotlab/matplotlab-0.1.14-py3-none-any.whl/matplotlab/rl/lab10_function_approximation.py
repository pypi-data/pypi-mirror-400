"""
RL Lab 10: Function Approximation Scaling
==========================================

Compares tabular methods vs linear and neural network function approximation.
Demonstrates memory efficiency, learning curves, and generalization.

Lab Objectives:
- Understand function approximation vs tabular methods
- Implement linear feature approximation
- Implement neural network approximation
- Analyze memory usage and learning dynamics
"""

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def linear_features_cartpole(state, order=2):
    """
    Extract polynomial features from CartPole state.
    
    Features: [1, x, x_dot, theta, theta_dot, x*theta, ...]
    
    Parameters:
    -----------
    state : ndarray
        CartPole state [x, x_dot, theta, theta_dot]
    order : int
        Polynomial order (1 or 2)
        
    Returns:
    --------
    features : ndarray
        Feature vector
    """
    if order == 1:
        return np.concatenate([[1], state])
    elif order == 2:
        x, xd, th, thd = state
        f = [1, x, xd, th, thd, x*th, x*thd, xd*th, xd*thd, 
             x**2, xd**2, th**2, thd**2]
        return np.array(f)
    else:
        raise ValueError("order must be 1 or 2")


def tabular_td_cartpole(episodes=500, alpha=0.01, gamma=0.99):
    """
    Tabular TD(0) on discretized CartPole.
    
    Parameters:
    -----------
    episodes : int
        Training episodes
    alpha : float
        Learning rate
    gamma : float
        Discount factor
        
    Returns:
    --------
    V_table : dict
        Value table (state -> value)
    rewards : ndarray
        Rewards per episode
    memory_usage : float
        Approximate memory in KB
    """
    env = gym.make('CartPole-v1')
    V_table = {}
    rewards = np.zeros(episodes)
    
    def discretize_state(state):
        x, xd, th, thd = state
        x_bin = int(np.clip((x + 2.4) / 4.8 * 10, 0, 9))
        xd_bin = int(np.clip((xd + 4) / 8 * 10, 0, 9))
        th_bin = int(np.clip((th + 0.42) / 0.84 * 10, 0, 9))
        thd_bin = int(np.clip((thd + 4) / 8 * 10, 0, 9))
        return (x_bin, xd_bin, th_bin, thd_bin)
    
    for episode in range(episodes):
        state, _ = env.reset()
        disc_state = discretize_state(state)
        done = False
        total_reward = 0
        
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            disc_next = discretize_state(next_state)
            
            v_curr = V_table.get(disc_state, 0)
            v_next = V_table.get(disc_next, 0)
            v_curr += alpha * (reward + gamma * v_next - v_curr)
            V_table[disc_state] = v_curr
            
            disc_state = disc_next
            total_reward += reward
        
        rewards[episode] = total_reward
    
    memory_usage = len(V_table) * 56 / 1024
    return V_table, rewards, memory_usage


def linear_fa_cartpole(episodes=500, alpha=0.001, gamma=0.99):
    """
    Linear function approximation TD on CartPole.
    
    Parameters:
    -----------
    episodes : int
        Training episodes
    alpha : float
        Learning rate
    gamma : float
        Discount factor
        
    Returns:
    --------
    w : ndarray
        Weight vector
    rewards : ndarray
        Rewards per episode
    """
    env = gym.make('CartPole-v1')
    w = np.zeros(13)
    rewards = np.zeros(episodes)
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        total_reward = 0
        
        while not done:
            f = linear_features_cartpole(state, order=2)
            v = np.dot(w, f)
            
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            f_next = linear_features_cartpole(next_state, order=2)
            v_next = np.dot(w, f_next)
            
            td_error = reward + gamma * v_next - v
            w += alpha * td_error * f
            
            total_reward += reward
        
        rewards[episode] = total_reward
    
    memory_usage = w.nbytes / 1024
    return w, rewards, memory_usage


def neural_network_fa_cartpole(episodes=500, learning_rate=0.01, gamma=0.99):
    """
    Neural network function approximation TD on CartPole.
    
    3-layer network: 4 -> 64 -> 32 -> 1
    
    Parameters:
    -----------
    episodes : int
        Training episodes
    learning_rate : float
        Neural network learning rate
    gamma : float
        Discount factor
        
    Returns:
    --------
    model : nn.Module or None
        Trained neural network
    rewards : ndarray
        Rewards per episode
    """
    if not TORCH_AVAILABLE:
        return None, np.zeros(episodes), 0
    
    class ValueNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(4, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1)
            )
        
        def forward(self, x):
            return self.net(x)
    
    model = ValueNet()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()
    
    env = gym.make('CartPole-v1')
    rewards = np.zeros(episodes)
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        total_reward = 0
        
        while not done:
            state_tensor = torch.tensor([state], dtype=torch.float32)
            v = model(state_tensor)
            
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            with torch.no_grad():
                next_state_tensor = torch.tensor([next_state], dtype=torch.float32)
                v_next = model(next_state_tensor)
                target = torch.tensor([[reward + gamma * v_next.item()]])
            
            loss = loss_fn(v, target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_reward += reward
        
        rewards[episode] = total_reward
    
    memory_params = sum(p.numel() * 4 for p in model.parameters()) / 1024
    return model, rewards, memory_params


def learning_rate_effect(env_name='CartPole-v1', alphas=[0.0001, 0.001, 0.01, 0.1]):
    """
    Analyze effect of learning rate on linear FA.
    
    Parameters:
    -----------
    env_name : str
        Gymnasium environment
    alphas : list
        Learning rates to test
        
    Returns:
    --------
    results : dict
        Rewards for each learning rate
    """
    results = {}
    
    for alpha in alphas:
        print(f"  Testing alpha={alpha}...", end=' ')
        w, rewards, _ = linear_fa_cartpole(episodes=200, alpha=alpha)
        results[alpha] = rewards
        print(f"mean reward: {np.mean(rewards[-50:]):.2f}")
    
    return results


def compare_methods(episodes=300):
    """
    Compare all three approximation methods.
    
    Parameters:
    -----------
    episodes : int
        Training episodes for each method
        
    Returns:
    --------
    results : dict
        Performance metrics for all methods
    """
    print("Comparing function approximation methods...")
    print("-" * 50)
    
    print("1. Tabular TD (discretized)...")
    V_tab, rewards_tab, mem_tab = tabular_td_cartpole(episodes=episodes)
    
    print("2. Linear FA...")
    w, rewards_lin, mem_lin = linear_fa_cartpole(episodes=episodes)
    
    print("3. Neural Network FA...")
    model, rewards_nn, mem_nn = neural_network_fa_cartpole(episodes=episodes)
    
    return {
        'tabular_rewards': rewards_tab,
        'tabular_memory': mem_tab,
        'linear_rewards': rewards_lin,
        'linear_memory': mem_lin,
        'nn_rewards': rewards_nn,
        'nn_memory': mem_nn,
        'torch_available': TORCH_AVAILABLE
    }


def plot_comparison(results):
    """
    Plot comparison of all methods.
    
    Parameters:
    -----------
    results : dict
        Results from compare_methods()
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    window = 10
    tab_smooth = np.convolve(results['tabular_rewards'], 
                             np.ones(window)/window, mode='valid')
    lin_smooth = np.convolve(results['linear_rewards'], 
                             np.ones(window)/window, mode='valid')
    
    axes[0].plot(tab_smooth, label=f'Tabular ({results["tabular_memory"]:.1f} KB)', linewidth=2)
    axes[0].plot(lin_smooth, label=f'Linear FA ({results["linear_memory"]:.3f} KB)', linewidth=2)
    
    if results['torch_available']:
        nn_smooth = np.convolve(results['nn_rewards'], 
                               np.ones(window)/window, mode='valid')
        axes[0].plot(nn_smooth, label=f'Neural Net ({results["nn_memory"]:.1f} KB)', linewidth=2)
    
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Reward (smoothed)')
    axes[0].set_title('Learning Curves: Function Approximation Methods')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    methods = ['Tabular', 'Linear FA', 'Neural Net'] if results['torch_available'] else ['Tabular', 'Linear FA']
    memory = [results['tabular_memory'], results['linear_memory']]
    if results['torch_available']:
        memory.append(results['nn_memory'])
    
    axes[1].bar(methods, memory, color=['blue', 'orange', 'green'][:len(methods)])
    axes[1].set_ylabel('Memory (KB)')
    axes[1].set_title('Memory Usage Comparison')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def analyze_lab10():
    """
    Run complete Lab 10 analysis.
    
    Returns:
    --------
    results : dict
        Complete analysis results
    """
    print("Lab 10: Function Approximation Scaling")
    print("-" * 50)
    
    results = compare_methods(episodes=200)
    
    print("\nLearning rate analysis...")
    lr_results = learning_rate_effect(alphas=[0.0001, 0.001, 0.01])
    
    print("\nResults:")
    print(f"  Tabular: {np.mean(results['tabular_rewards'][-30:]):.2f} reward, "
          f"{results['tabular_memory']:.1f} KB")
    print(f"  Linear: {np.mean(results['linear_rewards'][-30:]):.2f} reward, "
          f"{results['linear_memory']:.3f} KB")
    if results['torch_available']:
        print(f"  Neural: {np.mean(results['nn_rewards'][-30:]):.2f} reward, "
              f"{results['nn_memory']:.1f} KB")
    
    return {
        'comparison': results,
        'learning_rates': lr_results
    }
