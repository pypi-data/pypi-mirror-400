"""
RL Lab 12: Deep Q-Networks (DQN)
================================

Implements Deep Q-Networks with experience replay, target networks,
and epsilon-greedy exploration on CartPole environment.

Lab Objectives:
- Implement neural network-based Q-learning
- Understand experience replay mechanism
- Use target networks for stability
- Train on continuous control tasks
"""

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt
from collections import deque

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Dummy torch module
    torch = None
    nn = None
    optim = None


if TORCH_AVAILABLE:
    class QNetwork(nn.Module):
        """
        Deep Q-Network: 3-layer neural network for CartPole.
        
        Architecture: state_dim -> 64 -> 64 -> action_dim
        """
        def __init__(self, state_dim=4, action_dim=2):
            super().__init__()
            self.fc = nn.Sequential(
                nn.Linear(state_dim, 64),
                nn.ReLU(),
                nn.Linear(64, 64),
                nn.ReLU(),
                nn.Linear(64, action_dim)
            )
        
        def forward(self, x):
            return self.fc(x)
else:
    class QNetwork:
        """Placeholder QNetwork when PyTorch is unavailable."""
        def __init__(self, state_dim=4, action_dim=2):
            self.state_dim = state_dim
            self.action_dim = action_dim


class ExperienceReplay:
    """
    Experience replay buffer for DQN.
    
    Stores transitions and samples batches for training.
    """
    def __init__(self, max_size=2000):
        self.buffer = deque(maxlen=max_size)
    
    def add(self, state, action, reward, next_state, done):
        """Add transition to buffer."""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """Sample batch of transitions."""
        indices = np.random.choice(len(self.buffer), size=batch_size, replace=False)
        batch = [self.buffer[i] for i in indices]
        
        states = np.array([b[0] for b in batch])
        actions = np.array([b[1] for b in batch])
        rewards = np.array([b[2] for b in batch])
        next_states = np.array([b[3] for b in batch])
        dones = np.array([b[4] for b in batch])
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        return len(self.buffer)


def dqn_training(env_name='CartPole-v1', episodes=200, 
                 learning_rate=0.001, batch_size=64, gamma=0.99,
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995):
    """
    Train Deep Q-Network on CartPole.
    
    Parameters:
    -----------
    env_name : str
        Gymnasium environment
    episodes : int
        Training episodes
    learning_rate : float
        Adam learning rate
    batch_size : int
        Experience replay batch size
    gamma : float
        Discount factor
    epsilon_start : float
        Initial exploration rate
    epsilon_end : float
        Final exploration rate
    epsilon_decay : float
        Epsilon decay per episode
        
    Returns:
    --------
    model : nn.Module or None
        Trained Q-network
    target_model : nn.Module or None
        Target network (for computing targets)
    rewards : ndarray
        Rewards per episode
    losses : ndarray
        Mean loss per episode
    """
    if not TORCH_AVAILABLE:
        print("PyTorch not available. DQN training disabled.")
        return None, None, np.zeros(episodes), np.zeros(episodes)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = QNetwork(state_dim=4, action_dim=2).to(device)
    target_model = QNetwork(state_dim=4, action_dim=2).to(device)
    target_model.load_state_dict(model.state_dict())
    
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()
    
    replay_buffer = ExperienceReplay(max_size=2000)
    env = gym.make(env_name)
    
    rewards_per_episode = np.zeros(episodes)
    losses_per_episode = np.zeros(episodes)
    epsilon = epsilon_start
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0
        episode_losses = []
        
        while not done:
            if np.random.random() < epsilon:
                action = env.action_space.sample()
            else:
                state_tensor = torch.tensor([state], dtype=torch.float32).to(device)
                with torch.no_grad():
                    q_values = model(state_tensor)
                action = q_values.argmax(dim=1).item()
            
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            replay_buffer.add(state, action, reward, next_state, done)
            episode_reward += reward
            state = next_state
            
            if len(replay_buffer) >= batch_size:
                states, actions, rewards, next_states, dones = replay_buffer.sample(batch_size)
                
                states_tensor = torch.tensor(states, dtype=torch.float32).to(device)
                actions_tensor = torch.tensor(actions, dtype=torch.long).to(device)
                rewards_tensor = torch.tensor(rewards, dtype=torch.float32).to(device)
                next_states_tensor = torch.tensor(next_states, dtype=torch.float32).to(device)
                dones_tensor = torch.tensor(dones, dtype=torch.float32).to(device)
                
                q_values = model(states_tensor)
                q_values = q_values.gather(1, actions_tensor.unsqueeze(1)).squeeze(1)
                
                with torch.no_grad():
                    next_q_values = target_model(next_states_tensor).max(dim=1)[0]
                    target_q_values = rewards_tensor + gamma * next_q_values * (1 - dones_tensor)
                
                loss = loss_fn(q_values, target_q_values)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                episode_losses.append(loss.item())
        
        rewards_per_episode[episode] = episode_reward
        losses_per_episode[episode] = np.mean(episode_losses) if episode_losses else 0
        
        if (episode + 1) % 20 == 0:
            target_model.load_state_dict(model.state_dict())
        
        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        
        if (episode + 1) % 50 == 0:
            mean_reward = np.mean(rewards_per_episode[max(0, episode-49):episode+1])
            print(f"Episode {episode+1}: Mean reward = {mean_reward:.2f}, "
                  f"Epsilon = {epsilon:.4f}")
    
    return model, target_model, rewards_per_episode, losses_per_episode


def dqn_testing(model, env_name='CartPole-v1', episodes=10):
    """
    Test trained DQN model.
    
    Parameters:
    -----------
    model : nn.Module
        Trained Q-network
    env_name : str
        Gymnasium environment
    episodes : int
        Testing episodes
        
    Returns:
    --------
    test_rewards : ndarray
        Rewards for each episode
    """
    if not TORCH_AVAILABLE or model is None:
        return np.zeros(episodes)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.eval()
    env = gym.make(env_name)
    
    test_rewards = np.zeros(episodes)
    
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            state_tensor = torch.tensor([state], dtype=torch.float32).to(device)
            with torch.no_grad():
                q_values = model(state_tensor)
            action = q_values.argmax(dim=1).item()
            
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            state = next_state
        
        test_rewards[episode] = episode_reward
    
    return test_rewards


def compare_with_random(episodes=50):
    """
    Compare DQN performance with random policy.
    
    Parameters:
    -----------
    episodes : int
        Testing episodes
        
    Returns:
    --------
    results : dict
        DQN and random performance
    """
    if not TORCH_AVAILABLE:
        print("PyTorch not available. Cannot compare.")
        return {}
    
    print("Training DQN...")
    model, _, train_rewards, train_losses = dqn_training(
        episodes=200, batch_size=64, learning_rate=0.001
    )
    
    print("\nTesting trained DQN...")
    dqn_test_rewards = dqn_testing(model, episodes=episodes)
    
    print("Testing random policy...")
    env = gym.make('CartPole-v1')
    random_rewards = []
    for _ in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0
        while not done:
            action = env.action_space.sample()
            _, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            episode_reward += reward
        random_rewards.append(episode_reward)
    random_rewards = np.array(random_rewards)
    
    return {
        'dqn_train_rewards': train_rewards,
        'dqn_train_losses': train_losses,
        'dqn_test_rewards': dqn_test_rewards,
        'random_rewards': random_rewards,
        'dqn_mean': np.mean(dqn_test_rewards),
        'random_mean': np.mean(random_rewards)
    }


def plot_dqn_training(rewards, losses):
    """
    Plot DQN training curves.
    
    Parameters:
    -----------
    rewards : ndarray
        Rewards per episode
    losses : ndarray
        Losses per episode
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    window = 10
    rewards_smooth = np.convolve(rewards, np.ones(window)/window, mode='valid')
    
    axes[0].plot(rewards_smooth, linewidth=2, color='steelblue')
    axes[0].axhline(y=195, color='red', linestyle='--', label='Success Threshold (195)')
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Reward')
    axes[0].set_title('DQN Training: Episode Rewards (smoothed)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    if len(losses) > window:
        losses_smooth = np.convolve(losses, np.ones(window)/window, mode='valid')
        axes[1].plot(losses_smooth, linewidth=2, color='orange')
        axes[1].set_xlabel('Episode')
        axes[1].set_ylabel('MSE Loss')
        axes[1].set_title('DQN Training: Loss')
    
    axes[1].grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def analyze_lab12():
    """
    Run complete Lab 12 analysis.
    
    Returns:
    --------
    results : dict
        Training and testing results
    """
    if not TORCH_AVAILABLE:
        print("PyTorch not available. Cannot run Lab 12.")
        return {}
    
    print("Lab 12: Deep Q-Networks (DQN)")
    print("-" * 50)
    
    results = compare_with_random(episodes=20)
    
    if results:
        print("\nResults Summary:")
        print(f"  DQN Test Mean Reward: {results['dqn_mean']:.2f}")
        print(f"  Random Policy Mean Reward: {results['random_mean']:.2f}")
        print(f"  Improvement: {results['dqn_mean'] - results['random_mean']:.2f}")
    
    return results
