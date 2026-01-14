"""
Visualization utilities for Reinforcement Learning.

This module provides plotting functions for visualizing policies,
value functions, and convergence behavior.
Based on implementations from all labs.
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_episode_rewards(rewards, title="Episode Rewards", xlabel="Episode", ylabel="Total Reward"):
    """
    Plot total reward per episode.
    
    Parameters:
    -----------
    rewards : list or numpy.ndarray
        List of rewards per episode
    title : str, optional
        Plot title
    xlabel : str, optional
        X-axis label
    ylabel : str, optional
        Y-axis label
    
    Example:
    --------
    >>> import numpy as np
    >>> rewards = [10, 15, 12, 20, 25]
    >>> plot_episode_rewards(rewards, title="Training Progress")
    """
    plt.figure(figsize=(10, 5))
    plt.plot(rewards)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_grid_policy(V, policy, grid_shape=(3, 4), title="Grid World Policy"):
    """
    Visualize policy as arrows on grid with values.
    
    Parameters:
    -----------
    V : numpy.ndarray
        Value function (flat array)
    policy : numpy.ndarray or dict
        Policy array (nS, nA) or dict mapping states to actions
    grid_shape : tuple, optional (default=(3, 4))
        Shape of the grid (rows, cols)
    title : str, optional
        Plot title
    
    Example:
    --------
    >>> V = np.random.rand(11)  # 3x4 grid minus wall
    >>> policy = np.array([1, 2, 1, 0, 3, 2, 1, 0, 2, 1, 0])
    >>> plot_grid_policy(V, policy, grid_shape=(3, 4))
    """
    arrow_dict = {0: '←', 1: '↓', 2: '→', 3: '↑'}
    
    # Handle dict policy (convert to array of action indices)
    if isinstance(policy, dict):
        # policy is {state: action_name} - not directly usable
        # Skip this for now, requires action mapping
        best_actions = [0] * len(V)  # Default
    # If policy is 2D array, extract best actions
    elif hasattr(policy, 'shape') and len(policy.shape) > 1:
        best_actions = np.argmax(policy, axis=1)
    else:
        best_actions = policy
    
    rows, cols = grid_shape
    V_grid = V.reshape(grid_shape)
    
    plt.figure(figsize=(8, 6))
    plt.imshow(V_grid, cmap='cool', alpha=0.7)
    plt.colorbar(label='State Value')
    
    for state in range(len(V)):
        row = state // cols
        col = state % cols
        
        # Draw value
        plt.text(col, row, f'{V[state]:.2f}', 
                ha='center', va='center', color='black', fontsize=8)
        
        # Draw arrow
        plt.text(col, row + 0.3, arrow_dict[best_actions[state]], 
                ha='center', va='center', color='purple', fontsize=16)
    
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def plot_value_heatmap(V, grid_shape=(4, 4), title="State Values"):
    """
    Display value function as heatmap.
    
    Parameters:
    -----------
    V : numpy.ndarray
        Value function
    grid_shape : tuple, optional (default=(4, 4))
        Shape of the grid
    title : str, optional
        Plot title
    
    Example:
    --------
    >>> V = np.random.rand(16)
    >>> plot_value_heatmap(V, grid_shape=(4, 4))
    """
    rows, cols = grid_shape
    V_grid = V.reshape((rows, cols))
    
    plt.figure(figsize=(6, 5))
    im = plt.imshow(V_grid, cmap='viridis')
    plt.colorbar(im, label='Value')
    plt.title(title)
    
    # Add value text
    for i in range(rows):
        for j in range(cols):
            plt.text(j, i, f'{V_grid[i, j]:.2f}', 
                    ha='center', va='center', color='white', fontsize=10)
    
    plt.tight_layout()
    plt.show()


def plot(V, policy, env, col_ramp=1, dpi=175, draw_vals=False):
    """
    Comprehensive FrozenLake visualization.
    
    Shows:
    - State values as colors
    - Policy as arrows
    - Tile types (S, F, H, G)
    
    Parameters:
    -----------
    V : numpy.ndarray
        Value function
    policy : numpy.ndarray
        Policy array (nS, nA)
    env : gymnasium.Env
        FrozenLake environment
    col_ramp : int, optional (default=1)
        1 for 'cool' colormap, 0 for 'gray'
    dpi : int, optional (default=175)
        Figure DPI
    draw_vals : bool, optional (default=False)
        Whether to draw numerical values
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1')
    >>> V = np.random.rand(16)
    >>> policy = np.eye(4)[np.random.randint(0, 4, 16)]
    >>> plot(V, policy, env, draw_vals=True)
    """
    plt.rcParams['figure.dpi'] = dpi
    plt.rcParams.update({'axes.edgecolor': (0.32, 0.36, 0.38)})
    plt.figure(figsize=(3, 3))
    
    # Get environment layout
    desc = env.unwrapped.desc
    nrow, ncol = desc.shape
    V_sq = V.reshape((nrow, ncol))
    
    # Plot heatmap
    plt.imshow(V_sq, cmap='cool' if col_ramp else 'gray', alpha=0.7)
    ax = plt.gca()
    
    # Arrow symbols for actions
    arrow_dict = {0: '←', 1: '↓', 2: '→', 3: '↑'}
    
    # Draw grid lines
    for x in range(ncol + 1):
        ax.axvline(x - 0.5, lw=0.5, color='black')
    for y in range(nrow + 1):
        ax.axhline(y - 0.5, lw=0.5, color='black')
    
    # Fill each grid cell
    for r in range(nrow):
        for c in range(ncol):
            s = r * ncol + c
            val = V[s]
            
            # Tile text (S, F, H, G)
            tile = desc[r, c].decode('utf-8')
            if tile == 'H':
                color = 'red'
            elif tile == 'G':
                color = 'green'
            elif tile == 'S':
                color = 'blue'
            else:
                color = 'black'
            
            # Draw tile letter
            plt.text(c, r, tile, ha='center', va='center', 
                    color=color, fontsize=10, fontweight='bold')
            
            # Draw state value
            if draw_vals and tile != 'H':
                plt.text(c, r + 0.3, f"{val:.2f}", ha='center', va='center', 
                        color='black', fontsize=6)
            
            # Draw arrow for best action
            if policy is not None:
                best_action = np.argmax(policy[s])
                plt.text(c, r - 0.25, arrow_dict[best_action], 
                        ha='center', va='center', color='purple', fontsize=12)
    
    plt.title("FrozenLake: Policy and State Values")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def plot_convergence_delta(deltas, title="Convergence", log_scale=True):
    """
    Plot maximum delta vs iteration (convergence curve).
    
    Parameters:
    -----------
    deltas : list
        List of maximum deltas per iteration
    title : str, optional
        Plot title
    log_scale : bool, optional (default=True)
        Whether to use log scale for y-axis
    
    Example:
    --------
    >>> deltas = [1.0, 0.5, 0.1, 0.01, 0.001]
    >>> plot_convergence_delta(deltas, title="Value Iteration Convergence")
    """
    plt.figure(figsize=(8, 4))
    plt.plot(deltas, marker='.')
    if log_scale:
        plt.yscale('log')
    plt.title(title)
    plt.xlabel('Iteration')
    plt.ylabel('Max ΔV' + (' (log scale)' if log_scale else ''))
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.show()


def plot_values(env, V, title="Value Function"):
    """
    Line plot of values for all states.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Environment (for state count)
    V : numpy.ndarray
        Value function
    title : str, optional
        Plot title
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('Taxi-v3')
    >>> V = np.random.rand(env.observation_space.n)
    >>> plot_values(env, V, title="Taxi-v3 Values")
    """
    plt.figure(figsize=(10, 4))
    plt.plot(V)
    plt.title(title)
    plt.xlabel("State")
    plt.ylabel("Value")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_policy(env, policy, title="Policy"):
    """
    Bar plot showing best action per state.
    
    Parameters:
    -----------
    env : gymnasium.Env
        Environment
    policy : numpy.ndarray
        Policy array (nS, nA)
    title : str, optional
        Plot title
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1')
    >>> policy = np.eye(4)[np.random.randint(0, 4, 16)]
    >>> plot_policy(env, policy, title="Random Policy")
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    actions = np.argmax(policy, axis=1)
    
    # Create action labels
    action_names = {0: 'Left', 1: 'Down', 2: 'Right', 3: 'Up'}
    
    plt.figure(figsize=(12, 5))
    
    # Create bar plot with colors
    colors = ['red', 'blue', 'green', 'orange']
    bar_colors = [colors[a % len(colors)] for a in actions]
    
    bars = plt.bar(np.arange(nS), actions, color=bar_colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for i, (bar, action) in enumerate(zip(bars, actions)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{action_names.get(action, str(action))}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("State", fontsize=12)
    plt.ylabel("Best Action", fontsize=12)
    plt.yticks(range(nA), [action_names.get(i, str(i)) for i in range(nA)])
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()


def simple_plot(V, policy=None, env=None):
    """
    Compact FrozenLake plot with values and arrows.
    
    Parameters:
    -----------
    V : numpy.ndarray
        Value function
    policy : numpy.ndarray, optional
        Policy array (nS, nA)
    env : gymnasium.Env, optional
        FrozenLake environment
    
    Example:
    --------
    >>> import gymnasium as gym
    >>> import numpy as np
    >>> env = gym.make('FrozenLake-v1')
    >>> V = np.random.rand(16)
    >>> policy = np.eye(4)[np.random.randint(0, 4, 16)]
    >>> simple_plot(V, policy, env)
    """
    rows = cols = int(np.sqrt(len(V)))
    V_grid = V.reshape((rows, cols))
    
    fig, ax = plt.subplots()
    im = ax.matshow(V_grid, cmap='cool')
    fig.colorbar(im)
    
    if env is not None:
        desc = env.unwrapped.desc
        arrows = {0: '←', 1: '↓', 2: '→', 3: '↑'}
        
        for i in range(rows):
            for j in range(cols):
                s = i * cols + j
                tile = desc[i, j].decode('utf-8')
                text = tile
                
                if policy is not None:
                    best_action = np.argmax(policy[s])
                    text += '\n' + arrows[best_action]
                    ax.text(j, i, text, ha='center', va='center', color='black')
                    ax.text(j, i + 0.3, f"{V[s]:.2f}", ha='center', va='center', 
                           color='black', fontsize=8)
    
    plt.title("FrozenLake Values")
    plt.tight_layout()
    plt.show()


def plot_convergence(V_track, title="Value Function Convergence", states_to_plot=None):
    """
    Plot V(s) evolution over episodes for selected states.
    
    Parameters:
    -----------
    V_track : list of numpy.ndarray
        List of value functions over time
    title : str, optional
        Plot title
    states_to_plot : list, optional
        List of state indices to plot (default: plot first 5 states)
    
    Example:
    --------
    >>> V_track = [np.random.rand(16) for _ in range(100)]
    >>> plot_convergence(V_track, title="MC Convergence", states_to_plot=[0, 5, 10, 15])
    """
    if states_to_plot is None:
        states_to_plot = range(min(5, len(V_track[0])))
    
    plt.figure(figsize=(10, 5))
    for state in states_to_plot:
        values = [V[state] for V in V_track]
        plt.plot(values, label=f'State {state}')
    
    plt.title(title)
    plt.xlabel('Episode')
    plt.ylabel('V(s)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def compare_mc_td_convergence(V_mc_track, V_td_track, states_to_plot=None):
    """
    Side-by-side comparison of MC vs TD convergence.
    
    Parameters:
    -----------
    V_mc_track : list of numpy.ndarray
        Monte Carlo value function tracking
    V_td_track : list of numpy.ndarray
        TD learning value function tracking
    states_to_plot : list, optional
        List of state indices to plot
    
    Example:
    --------
    >>> V_mc = [np.random.rand(16) for _ in range(100)]
    >>> V_td = [np.random.rand(16) for _ in range(100)]
    >>> compare_mc_td_convergence(V_mc, V_td, states_to_plot=[0, 5, 15])
    """
    if states_to_plot is None:
        states_to_plot = range(min(5, len(V_mc_track[0])))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # MC convergence
    for state in states_to_plot:
        values = [V[state] for V in V_mc_track]
        ax1.plot(values, label=f'State {state}')
    ax1.set_title('Monte Carlo Convergence')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('V(s)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # TD convergence
    for state in states_to_plot:
        values = [V[state] for V in V_td_track]
        ax2.plot(values, label=f'State {state}')
    ax2.set_title('TD Learning Convergence')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('V(s)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
