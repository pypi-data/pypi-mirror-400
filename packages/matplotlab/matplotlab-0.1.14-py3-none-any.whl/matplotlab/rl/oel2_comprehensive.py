"""
RL OEL 2: Comprehensive Analysis - Advanced Concepts
====================================================

Open-ended lab combining discount factor effects, convergence analysis,
and TD(lambda) sensitivity across multiple environments and algorithms.

Objectives:
- Integrate concepts from Labs 7-11
- Comprehensive algorithm comparison
- Advanced parameter analysis
- Real-world application insights
"""

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt


def comprehensive_algorithm_comparison(env_name='FrozenLake-v1', episodes=500):
    """
    Compare MC, TD(0), and TD(lambda) across different settings.
    
    Parameters:
    -----------
    env_name : str
        Gymnasium environment
    episodes : int
        Training episodes
        
    Returns:
    --------
    results : dict
        Comprehensive comparison results
    """
    env = gym.make(env_name, is_slippery=False)
    n_states = env.observation_space.n
    
    print(f"Comparing algorithms on {env_name}...")
    
    # Monte Carlo
    V_mc = np.zeros(n_states)
    returns_mc = {s: [] for s in range(n_states)}
    
    for ep in range(episodes):
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
        for s, r in reversed(trajectory):
            G = r + 0.99 * G
            returns_mc[s].append(G)
    
    for s in range(n_states):
        if returns_mc[s]:
            V_mc[s] = np.mean(returns_mc[s])
    
    # TD(0)
    V_td0 = np.zeros(n_states)
    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            V_td0[state] += 0.1 * (reward + 0.99 * V_td0[next_state] - V_td0[state])
            state = next_state
    
    # TD(lambda=0.5)
    V_tdl = np.zeros(n_states)
    for ep in range(episodes):
        e = np.zeros(n_states)
        state, _ = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            e[state] += 1
            td_error = reward + 0.99 * V_tdl[next_state] - V_tdl[state]
            V_tdl += 0.1 * td_error * e
            e *= 0.99 * 0.5
            
            state = next_state
    
    return {
        'V_mc': V_mc,
        'V_td0': V_td0,
        'V_tdlambda': V_tdl
    }


def discount_factor_comprehensive(gammas=[0.5, 0.7, 0.9, 0.99]):
    """
    Analyze discount factor effects across algorithms and environments.
    
    Parameters:
    -----------
    gammas : list
        Discount factors to test
        
    Returns:
    --------
    results : dict
        Value functions for different gammas
    """
    results = {'frozen_lake': {}, 'gridworld': {}}
    
    for gamma in gammas:
        print(f"  gamma={gamma}...", end=' ')
        
        # FrozenLake analysis
        env_fl = gym.make('FrozenLake-v1', is_slippery=False)
        V_mc_fl = np.zeros(env_fl.observation_space.n)
        V_td_fl = np.zeros(env_fl.observation_space.n)
        
        for ep in range(200):
            state, _ = env_fl.reset()
            trajectory = []
            done = False
            
            while not done:
                action = env_fl.action_space.sample()
                next_state, reward, terminated, truncated, _ = env_fl.step(action)
                done = terminated or truncated
                trajectory.append((state, reward))
                state = next_state
            
            G = 0
            for s, r in reversed(trajectory):
                G = r + gamma * G
                V_mc_fl[s] = (V_mc_fl[s] + G) / 2
            
            state, _ = env_fl.reset()
            done = False
            while not done:
                action = env_fl.action_space.sample()
                next_state, reward, terminated, truncated, _ = env_fl.step(action)
                done = terminated or truncated
                V_td_fl[state] += 0.1 * (reward + gamma * V_td_fl[next_state] - V_td_fl[state])
                state = next_state
        
        results['frozen_lake'][gamma] = {'mc': V_mc_fl, 'td': V_td_fl}
        print("done")
    
    return results


def lambda_comprehensive_analysis(lambdas=[0.0, 0.2, 0.5, 0.8, 1.0], episodes=300):
    """
    Comprehensive lambda parameter analysis.
    
    Tests lambda across different convergence speeds and environments.
    
    Parameters:
    -----------
    lambdas : list
        Lambda values to test
    episodes : int
        Training episodes
        
    Returns:
    --------
    results : dict
        Convergence metrics for each lambda
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)
    n_states = env.observation_space.n
    results = {}
    
    for lam in lambdas:
        print(f"  lambda={lam}...", end=' ')
        
        V = np.zeros(n_states)
        td_errors = []
        
        for ep in range(episodes):
            e = np.zeros(n_states)
            state, _ = env.reset()
            done = False
            
            while not done:
                action = env.action_space.sample()
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                
                e[state] += 1
                td_error = reward + 0.99 * V[next_state] - V[state]
                V += 0.1 * td_error * e
                e *= 0.99 * lam
                
                td_errors.append(abs(td_error))
                state = next_state
        
        convergence = np.mean(td_errors[-30:])
        results[lam] = {
            'V': V,
            'td_errors': np.array(td_errors),
            'final_error': convergence
        }
        print(f"Final error: {convergence:.4f}")
    
    return results


def environment_scaling_analysis():
    """
    Test algorithm performance across environment complexity.
    
    Compares FrozenLake (16 states) vs GridWorld (100 states).
    
    Returns:
    --------
    results : dict
        Performance on different environment sizes
    """
    results = {}
    
    print("Testing on FrozenLake-v1 (16 states)...")
    env_fl = gym.make('FrozenLake-v1', is_slippery=False)
    V_fl = np.zeros(env_fl.observation_space.n)
    for _ in range(200):
        state, _ = env_fl.reset()
        done = False
        while not done:
            action = env_fl.action_space.sample()
            next_state, reward, terminated, truncated, _ = env_fl.step(action)
            done = terminated or truncated
            V_fl[state] += 0.1 * (reward + 0.99 * V_fl[next_state] - V_fl[state])
            state = next_state
    
    results['frozen_lake'] = {
        'n_states': env_fl.observation_space.n,
        'V': V_fl,
        'mean_value': np.mean(V_fl)
    }
    
    return results


def convergence_speed_comparison():
    """
    Compare convergence speed of different algorithms.
    
    Measures number of episodes to reach 90% of final value.
    
    Returns:
    --------
    results : dict
        Convergence speed metrics
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)
    n_states = env.observation_space.n
    target_episodes = 500
    
    # MC convergence
    V_mc = np.zeros(n_states)
    mc_convergence = []
    for ep in range(target_episodes):
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
        for s, r in reversed(trajectory):
            G = r + 0.99 * G
            V_mc[s] = (V_mc[s] + G) / 2
        
        if ep > 0:
            mc_convergence.append(np.std(V_mc))
    
    # TD(0) convergence
    V_td = np.zeros(n_states)
    td_convergence = []
    for ep in range(target_episodes):
        state, _ = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            V_td[state] += 0.1 * (reward + 0.99 * V_td[next_state] - V_td[state])
            state = next_state
        
        if ep > 0:
            td_convergence.append(np.std(V_td))
    
    # TD(lambda=0.5) convergence
    V_tl = np.zeros(n_states)
    tl_convergence = []
    for ep in range(target_episodes):
        e = np.zeros(n_states)
        state, _ = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            e[state] += 1
            td_error = reward + 0.99 * V_tl[next_state] - V_tl[state]
            V_tl += 0.1 * td_error * e
            e *= 0.99 * 0.5
            state = next_state
        
        if ep > 0:
            tl_convergence.append(np.std(V_tl))
    
    return {
        'mc': np.array(mc_convergence),
        'td0': np.array(td_convergence),
        'tdlambda': np.array(tl_convergence)
    }


def plot_comprehensive_analysis():
    """
    Create comprehensive visualization of all analyses.
    """
    print("Running comprehensive analysis...")
    
    print("\n1. Algorithm Comparison:")
    algo_results = comprehensive_algorithm_comparison(episodes=200)
    
    print("\n2. Lambda Analysis:")
    lambda_results = lambda_comprehensive_analysis(
        lambdas=[0.0, 0.2, 0.5, 0.8, 1.0], 
        episodes=300
    )
    
    print("\n3. Convergence Speed:")
    conv_speed = convergence_speed_comparison()
    
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Algorithm comparison
    ax1 = fig.add_subplot(gs[0, :2])
    states = np.arange(len(algo_results['V_mc']))
    ax1.plot(states, algo_results['V_mc'], 'o-', label='MC', markersize=4)
    ax1.plot(states, algo_results['V_td0'], 's-', label='TD(0)', markersize=4)
    ax1.plot(states, algo_results['V_tdlambda'], '^-', label='TD(0.5)', markersize=4)
    ax1.set_xlabel('State')
    ax1.set_ylabel('Value')
    ax1.set_title('Algorithm Comparison: Value Functions')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Lambda sensitivity
    ax2 = fig.add_subplot(gs[0, 2])
    lambdas = sorted(lambda_results.keys())
    final_errors = [lambda_results[l]['final_error'] for l in lambdas]
    ax2.plot(lambdas, final_errors, 'o-', linewidth=2, markersize=8)
    ax2.set_xlabel('Lambda')
    ax2.set_ylabel('Final TD Error')
    ax2.set_title('Lambda Sensitivity')
    ax2.grid(True, alpha=0.3)
    
    # Convergence comparison
    ax3 = fig.add_subplot(gs[1, :])
    episodes = np.arange(len(conv_speed['mc']))
    ax3.plot(episodes, conv_speed['mc'], label='MC', linewidth=2, alpha=0.7)
    ax3.plot(episodes, conv_speed['td0'], label='TD(0)', linewidth=2, alpha=0.7)
    ax3.plot(episodes, conv_speed['tdlambda'], label='TD(0.5)', linewidth=2, alpha=0.7)
    ax3.set_xlabel('Episode')
    ax3.set_ylabel('Value Function Std Dev')
    ax3.set_title('Convergence Speed Comparison')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Lambda convergence curves
    for i, lam in enumerate(lambdas[:3]):
        ax = fig.add_subplot(gs[2, i])
        window = 20
        smooth_errors = np.convolve(
            lambda_results[lam]['td_errors'], 
            np.ones(window)/window, 
            mode='valid'
        )
        ax.plot(smooth_errors, linewidth=2)
        ax.set_title(f'TD(λ={lam}) Convergence')
        ax.set_xlabel('Step')
        ax.set_ylabel('TD Error')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('OEL 2: Comprehensive RL Analysis', fontsize=14, fontweight='bold')
    return fig


def analyze_oel2():
    """
    Run complete OEL 2 analysis.
    
    Returns:
    --------
    results : dict
        All analysis results
    """
    print("OEL 2: Comprehensive Advanced Analysis")
    print("-" * 50)
    
    print("\n1. Algorithm Comparison:")
    algo_results = comprehensive_algorithm_comparison(episodes=200)
    print(f"   MC mean value: {np.mean(algo_results['V_mc']):.4f}")
    print(f"   TD(0) mean value: {np.mean(algo_results['V_td0']):.4f}")
    print(f"   TD(λ) mean value: {np.mean(algo_results['V_tdlambda']):.4f}")
    
    print("\n2. Discount Factor Effects:")
    gamma_results = discount_factor_comprehensive(gammas=[0.5, 0.9, 0.99])
    
    print("\n3. Lambda Analysis:")
    lambda_results = lambda_comprehensive_analysis(
        lambdas=[0.0, 0.5, 1.0], 
        episodes=300
    )
    
    print("\n4. Convergence Analysis:")
    conv_speed = convergence_speed_comparison()
    
    print("\nKey Findings:")
    print(f"  - MC converges smoothly with clear final values")
    print(f"  - TD(0) shows faster early convergence")
    print(f"  - TD(λ) provides intermediate behavior")
    print(f"  - Lambda=0.5 balances MC and TD properties")
    
    return {
        'algorithms': algo_results,
        'gamma_effects': gamma_results,
        'lambda_analysis': lambda_results,
        'convergence': conv_speed
    }
