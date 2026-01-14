"""
RL Lab 8: Q-Learning and Function Approximation
================================================

Implements Q-Learning (TD-based control) and compares tabular vs
function approximation (linear and neural network) approaches.

Lab Objectives:
- Implement Q-Learning algorithm
- Compare tabular Q-Learning vs function approximation
- Analyze effect of learning rate
"""

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def q_learning_tabular(env, episodes=2000, alpha=0.8, gamma=0.95, epsilon=0.1):
    """
    Tabular Q-Learning algorithm.
    
    Off-policy temporal difference control using epsilon-greedy exploration.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Environment (must have discrete state and action spaces)
    episodes : int
        Number of training episodes
    alpha : float
        Learning rate
    gamma : float
        Discount factor
    epsilon : float
        Exploration rate
        
    Returns:
    --------
    Q : ndarray, shape (n_states, n_actions)
        Learned Q-table
    rewards_per_episode : ndarray, shape (episodes,)
        Total reward per episode
    """
    Q = np.zeros((env.observation_space.n, env.action_space.n))
    rewards_per_episode = np.zeros(episodes)
    
    def epsilon_greedy(state):
        if np.random.random() < epsilon:
            return env.action_space.sample()
        return np.argmax(Q[state])
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        total_reward = 0
        
        while not done:
            action = epsilon_greedy(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            if not terminated and not truncated:
                reward = -0.01
            elif terminated and reward == 0:
                reward = -1.0
            
            best_next = np.max(Q[next_state])
            Q[state, action] += alpha * (reward + gamma * best_next - Q[state, action])
            
            state = next_state
            total_reward += reward
        
        rewards_per_episode[episode] = total_reward
    
    return Q, rewards_per_episode


def linear_function_approximation(env, episodes=500, alpha=0.01, gamma=0.99):
    """
    Q-Learning with linear function approximation.
    
    Uses feature vector [1, state, state^2] and weight vector w.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Environment
    episodes : int
        Training episodes
    alpha : float
        Learning rate
    gamma : float
        Discount factor
        
    Returns:
    --------
    w : ndarray
        Learned weight vector
    rewards : ndarray
        Rewards per episode
    td_errors : ndarray
        Mean TD error per episode
    """
    def features(state):
        s = float(state[0] if hasattr(state, '__getitem__') else state)
        return np.array([1, s, s**2])
    
    w = np.zeros(3)
    rewards = []
    td_errors = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0
        episode_td_errors = []
        
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            s = features(state)
            s_next = features(next_state)
            
            q_curr = np.dot(w, s)
            q_next = np.dot(w, s_next)
            td_error = reward + gamma * q_next - q_curr
            
            w += alpha * td_error * s
            
            episode_reward += reward
            episode_td_errors.append(abs(td_error))
            state = next_state
        
        rewards.append(episode_reward)
        td_errors.append(np.mean(episode_td_errors) if episode_td_errors else 0)
    
    return w, np.array(rewards), np.array(td_errors)


def neural_network_approximation(env, episodes=500, learning_rate=0.001, gamma=0.99):
    """
    Q-Learning with neural network function approximation.
    
    Uses a 2-layer neural network to approximate Q-values.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Environment
    episodes : int
        Training episodes
    learning_rate : float
        Neural network learning rate
    gamma : float
        Discount factor
        
    Returns:
    --------
    model : nn.Module or None
        Trained model (or None if torch not available)
    rewards : ndarray
        Rewards per episode
    losses : ndarray
        Mean MSE loss per episode
    """
    if not TORCH_AVAILABLE:
        return None, np.zeros(episodes), np.zeros(episodes)
    
    class ValueNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Sequential(
                nn.Linear(1, 64),
                nn.ReLU(),
                nn.Linear(64, 1)
            )
        
        def forward(self, x):
            return self.fc(x)
    
    model = ValueNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()
    
    rewards = []
    losses = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0
        episode_losses = []
        
        while not done:
            state_tensor = torch.tensor([state[0]], dtype=torch.float32).unsqueeze(0)
            value = model(state_tensor)
            
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            with torch.no_grad():
                next_state_tensor = torch.tensor([next_state[0]], dtype=torch.float32).unsqueeze(0)
                next_value = model(next_state_tensor)
                target = torch.tensor([[reward + gamma * next_value.item()]])
            
            loss = loss_fn(value, target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            episode_reward += reward
            episode_losses.append(loss.item())
            state = next_state
        
        rewards.append(episode_reward)
        losses.append(np.mean(episode_losses) if episode_losses else 0)
    
    return model, np.array(rewards), np.array(losses)


def compare_approximation_methods(env_name='CartPole-v1', episodes=500):
    """
    Compare tabular, linear, and neural network approximation.
    
    Parameters:
    -----------
    env_name : str
        Gymnasium environment name
    episodes : int
        Training episodes
        
    Returns:
    --------
    results : dict
        Results from all methods
    """
    env = gym.make(env_name)
    
    w, lin_rewards, lin_td_errors = linear_function_approximation(
        env, episodes=episodes
    )
    nn_model, nn_rewards, nn_losses = neural_network_approximation(
        env, episodes=episodes
    )
    
    return {
        'linear_weights': w,
        'linear_rewards': lin_rewards,
        'linear_td_errors': lin_td_errors,
        'nn_model': nn_model,
        'nn_rewards': nn_rewards,
        'nn_losses': nn_losses
    }


def plot_approximation_comparison(results):
    """
    Plot comparison of approximation methods.
    
    Parameters:
    -----------
    results : dict
        Results from compare_approximation_methods()
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].plot(results['linear_rewards'], label='Linear FA', linewidth=2)
    axes[0].plot(results['nn_rewards'], label='Neural Network FA', linewidth=2)
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Total Reward')
    axes[0].set_title('Rewards: Linear vs Neural Network Function Approximation')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(results['linear_td_errors'], label='Linear FA (TD Error)', linewidth=2)
    axes[1].plot(results['nn_losses'], label='Neural Network FA (MSE Loss)', linewidth=2)
    axes[1].set_xlabel('Episode')
    axes[1].set_ylabel('Error/Loss')
    axes[1].set_title('Learning Error Comparison')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig
