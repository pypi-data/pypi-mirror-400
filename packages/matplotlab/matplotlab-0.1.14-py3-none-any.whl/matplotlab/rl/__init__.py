"""
Reinforcement Learning Module
==============================

Implementations from RL Labs 1-12 and OEL1/OEL2 covering:
- Monte Carlo Methods (Lab 3, 7)
- Temporal Difference Learning (Lab 7, 11)
- Policy Evaluation (Lab 4)
- Policy Iteration (Lab 5, OEL)
- Value Iteration (Lab 6)
- Q-Learning & Function Approximation (Lab 8, 10)
- Off-Policy Learning (Lab 9)
- Batch RL Analysis (Lab 11)
- Deep Q-Networks (Lab 12)
- Custom Environments (Lab 1, 2)
- MDP Utilities (Lab 2)
- Visualization Tools (All labs)
- Lab Workflow References (flowlab1-12, flowoel, flowoel2)

Author: Sohail
Source: University RL Coursework 2025
"""

__version__ = "0.1.3"

# Environment utilities
from .environments import (
    create_frozenlake_env,
    random_agent_episode,
    visualize_path,
    GridWorld,
)

# MDP utilities
from .mdp import (
    next_state,
    transition_probabilities,
    reward,
    define_states_actions,
)

# Monte Carlo methods
from .monte_carlo import (
    sample_episode,
    mc_value_estimation_mdp,
    compute_return,
    analytical_solution,
    mc_prediction,
)

# Policy evaluation
from .policy_eval import (
    policy_evaluation,
    bellman_expectation_backup,
)

# Policy iteration
from .policy_iter import (
    q_from_v,
    policy_improvement,
    policy_iteration,
)

# Value iteration
from .value_iter import (
    value_iteration,
    extract_policy_from_v,
    evaluate_policy,
    value_iteration_with_delta,
)

# Temporal difference learning
from .td_learning import (
    td_prediction,
)

# NEW LAB 7: Monte Carlo vs TD comparison
from .lab7_mc_vs_td import (
    monte_carlo_prediction,
    td0_prediction,
    plot_convergence_comparison,
    analyze_lab7,
)

# NEW LAB 8: Q-Learning and Function Approximation
from .lab8_qlearning_fa import (
    q_learning_tabular,
    linear_function_approximation,
    neural_network_approximation,
    compare_approximation_methods,
    plot_approximation_comparison,
)

# NEW LAB 9: Off-Policy Learning with Importance Sampling
from .lab9_offpolicy_mc import (
    ordinary_importance_sampling,
    weighted_importance_sampling,
    q_learning_blackjack,
    variance_analysis_is,
    plot_offpolicy_comparison,
    variance_analysis_comparison,
    analyze_lab9,
)

# NEW LAB 10: Function Approximation Methods
from .lab10_function_approximation import (
    linear_features_cartpole,
    tabular_td_cartpole,
    linear_fa_cartpole,
    neural_network_fa_cartpole,
    learning_rate_effect,
    compare_methods,
    plot_comparison,
    analyze_lab10,
)

# NEW LAB 11: Batch RL and Parameter Analysis
from .lab11_batch_rl import (
    batch_monte_carlo,
    batch_td_zero,
    batch_td_lambda,
    discount_factor_analysis,
    lambda_sensitivity_analysis,
    convergence_analysis,
    plot_discount_factor_effect,
    plot_lambda_analysis,
    plot_convergence_comparison,
    analyze_lab11,
)

# NEW LAB 12: Deep Q-Networks
from .lab12_dqn import (
    QNetwork,
    ExperienceReplay,
    dqn_training,
    dqn_testing,
    compare_with_random,
    plot_dqn_training,
    analyze_lab12,
)

# NEW OEL2: Comprehensive Analysis
from .oel2_comprehensive import (
    comprehensive_algorithm_comparison,
    discount_factor_comprehensive,
    lambda_comprehensive_analysis,
    environment_scaling_analysis,
    convergence_speed_comparison,
    plot_comprehensive_analysis,
    analyze_oel2,
)

# Visualization
from .visualization import (
    plot_episode_rewards,
    plot_grid_policy,
    plot_value_heatmap,
    plot,
    plot_convergence_delta,
    plot_values,
    plot_policy,
    simple_plot,
    plot_convergence,
    compare_mc_td_convergence,
)

# Utility functions
from ._utils import query

# Lab workflow functions
from .lab_flows import (
    flowlab1,
    flowlab2,
    flowlab3,
    flowlab4,
    flowlab5,
    flowlab6,
    flowlab7,
    flowlab8,
    flowlab9,
    flowlab10,
    flowlab11,
    flowlab12,
    flowoel,
    flowoel2,
)

# Import code inspector and wrap all functions with .show() capability
from ._code_inspector import ShowableFunction, ShowableClass


def list_functions():
    """
    Display all available RL functions organized by category.
    
    After seeing the list, use help(rl.function_name) to see parameters.
    
    Example:
    --------
    >>> import sohail_mlsuite.rl as rl
    >>> rl.list_functions()  # See all functions
    >>> help(rl.policy_iteration)  # See parameters for specific function
    """
    categories = {
        "ENVIRONMENTS (3 functions)": [
            "create_frozenlake_env",
            "random_agent_episode", 
            "visualize_path",
        ],
        "MDP UTILITIES (4 functions)": [
            "define_states_actions",
            "next_state",
            "transition_probabilities",
            "reward",
        ],
        "MONTE CARLO (5 functions)": [
            "sample_episode",
            "mc_value_estimation_mdp",
            "compute_return",
            "analytical_solution",
            "mc_prediction",
        ],
        "POLICY EVALUATION (2 functions)": [
            "policy_evaluation",
            "bellman_expectation_backup",
        ],
        "POLICY ITERATION (3 functions)": [
            "q_from_v",
            "policy_improvement",
            "policy_iteration",
        ],
        "VALUE ITERATION (4 functions)": [
            "value_iteration",
            "extract_policy_from_v",
            "evaluate_policy",
            "value_iteration_with_delta",
        ],
        "TD LEARNING (1 function)": [
            "td_prediction",
        ],
        "LAB 7: MC vs TD (4 functions)": [
            "monte_carlo_prediction",
            "td0_prediction",
            "plot_convergence_comparison",
            "analyze_lab7",
        ],
        "LAB 8: Q-Learning & FA (5 functions)": [
            "q_learning_tabular",
            "linear_function_approximation",
            "neural_network_approximation",
            "compare_approximation_methods",
            "plot_approximation_comparison",
        ],
        "LAB 9: Off-Policy MC (7 functions)": [
            "ordinary_importance_sampling",
            "weighted_importance_sampling",
            "q_learning_blackjack",
            "variance_analysis_is",
            "plot_offpolicy_comparison",
            "variance_analysis_comparison",
            "analyze_lab9",
        ],
        "LAB 10: Function Approx (8 functions)": [
            "linear_features_cartpole",
            "tabular_td_cartpole",
            "linear_fa_cartpole",
            "neural_network_fa_cartpole",
            "learning_rate_effect",
            "compare_methods",
            "plot_comparison",
            "analyze_lab10",
        ],
        "LAB 11: Batch RL (10 functions)": [
            "batch_monte_carlo",
            "batch_td_zero",
            "batch_td_lambda",
            "discount_factor_analysis",
            "lambda_sensitivity_analysis",
            "convergence_analysis",
            "plot_discount_factor_effect",
            "plot_lambda_analysis",
            "plot_convergence_comparison",
            "analyze_lab11",
        ],
        "LAB 12: Deep Q-Networks (7 functions + 2 classes)": [
            "QNetwork",
            "ExperienceReplay",
            "dqn_training",
            "dqn_testing",
            "compare_with_random",
            "plot_dqn_training",
            "analyze_lab12",
        ],
        "OEL2: Comprehensive (7 functions)": [
            "comprehensive_algorithm_comparison",
            "discount_factor_comprehensive",
            "lambda_comprehensive_analysis",
            "environment_scaling_analysis",
            "convergence_speed_comparison",
            "plot_comprehensive_analysis",
            "analyze_oel2",
        ],
        "VISUALIZATION (10 functions)": [
            "plot_episode_rewards",
            "plot_grid_policy",
            "plot_value_heatmap",
            "plot",
            "plot_convergence_delta",
            "plot_values",
            "plot_policy",
            "simple_plot",
            "plot_convergence",
            "compare_mc_td_convergence",
        ],
        "UTILITY (1 function)": [
            "query",
        ],
        "LAB WORKFLOWS (14 functions)": [
            "flowlab1",
            "flowlab2",
            "flowlab3",
            "flowlab4",
            "flowlab5",
            "flowlab6",
            "flowlab7",
            "flowlab8",
            "flowlab9",
            "flowlab10",
            "flowlab11",
            "flowlab12",
            "flowoel",
            "flowoel2",
        ],
    }
    
    print("=" * 70)
    print("MATPLOTLAB RL MODULE - ALL FUNCTIONS")
    print("=" * 70)
    print()
    
    total = 0
    for category, funcs in categories.items():
        print(f"{category}")
        print("-" * 70)
        for func in funcs:
            print(f"  - {func}")
            total += 1
        print()
    
    print("=" * 70)
    print(f"TOTAL: {total} functions available")
    print()
    print("HOW TO USE:")
    print("  1. Choose a function from above")
    print("  2. See parameters: help(rl.function_name)")
    print("  3. See code: rl.function_name.show()")
    print()
    print("LAB WORKFLOWS:")
    print("  - Use flowlab1() through flowlab6() and flowoel() to see complete")
    print("    lab code workflows from import to visualization")
    print("  - Example: rl.flowlab3() shows all code for Lab 3")
    print("=" * 70)


def show_lib():
    """
    Display all required library imports for RL labs.
    
    Shows the complete list of imports needed across all 7 RL labs
    with correct syntax. Use this when you forget import statements.
    
    Example:
    --------
    >>> import sohail_mlsuite.rl as rl
    >>> rl.show_lib()  # See all required imports
    """
    print("=" * 70)
    print("REQUIRED LIBRARIES FOR RL MODULE (All 7 Labs)")
    print("=" * 70)
    print()
    
    print("# Core Libraries")
    print("-" * 70)
    print("import numpy as np")
    print("import matplotlib.pyplot as plt")
    print()
    
    print("# Gymnasium (OpenAI Gym)")
    print("-" * 70)
    print("import gymnasium as gym")
    print()
    
    print("# Python Standard Library")
    print("-" * 70)
    print("from pprint import pprint")
    print()
    
    print("=" * 70)
    print("INSTALLATION COMMANDS")
    print("=" * 70)
    print()
    print("pip install numpy matplotlib gymnasium pygame")
    print()
    print("=" * 70)
    print()
    print("NOTES:")
    print("  - numpy: Array operations and mathematical computations")
    print("  - matplotlib: Plotting and visualization")
    print("  - gymnasium: RL environments (FrozenLake, Taxi, etc.)")
    print("  - pygame: Required for gymnasium rendering")
    print("  - pprint: Pretty printing for debugging")
    print("=" * 70)


# Wrap all imported functions to add .show() method
_functions_to_wrap = [
    # Environments
    create_frozenlake_env,
    random_agent_episode,
    visualize_path,
    # MDP
    next_state,
    transition_probabilities,
    reward,
    define_states_actions,
    # Monte Carlo
    sample_episode,
    mc_value_estimation_mdp,
    compute_return,
    analytical_solution,
    mc_prediction,
    # Policy Evaluation
    policy_evaluation,
    bellman_expectation_backup,
    # Policy Iteration
    q_from_v,
    policy_improvement,
    policy_iteration,
    # Value Iteration
    value_iteration,
    extract_policy_from_v,
    evaluate_policy,
    value_iteration_with_delta,
    # TD Learning
    td_prediction,
    # Lab 7: MC vs TD
    monte_carlo_prediction,
    td0_prediction,
    plot_convergence_comparison,
    analyze_lab7,
    # Lab 8: Q-Learning & FA
    q_learning_tabular,
    linear_function_approximation,
    neural_network_approximation,
    compare_approximation_methods,
    plot_approximation_comparison,
    # Lab 9: Off-Policy MC
    ordinary_importance_sampling,
    weighted_importance_sampling,
    q_learning_blackjack,
    variance_analysis_is,
    plot_offpolicy_comparison,
    variance_analysis_comparison,
    analyze_lab9,
    # Lab 10: Function Approx
    linear_features_cartpole,
    tabular_td_cartpole,
    linear_fa_cartpole,
    neural_network_fa_cartpole,
    learning_rate_effect,
    compare_methods,
    plot_comparison,
    analyze_lab10,
    # Lab 11: Batch RL
    batch_monte_carlo,
    batch_td_zero,
    batch_td_lambda,
    discount_factor_analysis,
    lambda_sensitivity_analysis,
    convergence_analysis,
    plot_discount_factor_effect,
    plot_lambda_analysis,
    plot_convergence_comparison,
    analyze_lab11,
    # Lab 12: DQN
    dqn_training,
    dqn_testing,
    compare_with_random,
    plot_dqn_training,
    analyze_lab12,
    # OEL2: Comprehensive
    comprehensive_algorithm_comparison,
    discount_factor_comprehensive,
    lambda_comprehensive_analysis,
    environment_scaling_analysis,
    convergence_speed_comparison,
    plot_comprehensive_analysis,
    analyze_oel2,
    # Visualization
    plot_episode_rewards,
    plot_grid_policy,
    plot_value_heatmap,
    plot,
    plot_convergence_delta,
    plot_values,
    plot_policy,
    simple_plot,
    plot_convergence,
    compare_mc_td_convergence,
]

# Apply ShowableFunction wrapper to all functions
for func in _functions_to_wrap:
    # Only wrap if not already wrapped (to avoid double-wrapping)
    if not isinstance(func, ShowableFunction):
        wrapped = ShowableFunction(func)
        globals()[func.__name__] = wrapped

# Wrap all classes to add .show() method
_classes_to_wrap = [
    GridWorld,  # Main RL class
]

for cls in _classes_to_wrap:
    if not isinstance(cls, ShowableClass):
        wrapped_cls = ShowableClass(cls)
        globals()[cls.__name__] = wrapped_cls

# Clean up internal variables to avoid polluting module namespace
del ShowableFunction  # Remove the class from module namespace
del ShowableClass    # Remove the class from module namespace
del wrapped  # Remove the temporary variable

__all__ = [
    # Environments
    "create_frozenlake_env",
    "random_agent_episode",
    "visualize_path",
    "GridWorld",
    "define_states_actions",
    # MDP
    "next_state",
    "transition_probabilities",
    "reward",
    # Monte Carlo
    "sample_episode",
    "mc_value_estimation_mdp",
    "compute_return",
    "analytical_solution",
    "mc_prediction",
    # Policy Evaluation
    "policy_evaluation",
    "bellman_expectation_backup",
    # Policy Iteration
    "q_from_v",
    "policy_improvement",
    "policy_iteration",
    # Value Iteration
    "value_iteration",
    "extract_policy_from_v",
    "evaluate_policy",
    "value_iteration_with_delta",
    # TD Learning
    "td_prediction",
    # Lab 7: MC vs TD
    "monte_carlo_prediction",
    "td0_prediction",
    "plot_convergence_comparison",
    "analyze_lab7",
    # Lab 8: Q-Learning & FA
    "q_learning_tabular",
    "linear_function_approximation",
    "neural_network_approximation",
    "compare_approximation_methods",
    "plot_approximation_comparison",
    # Lab 9: Off-Policy MC
    "ordinary_importance_sampling",
    "weighted_importance_sampling",
    "q_learning_blackjack",
    "variance_analysis_is",
    "plot_offpolicy_comparison",
    "variance_analysis_comparison",
    "analyze_lab9",
    # Lab 10: Function Approx
    "linear_features_cartpole",
    "tabular_td_cartpole",
    "linear_fa_cartpole",
    "neural_network_fa_cartpole",
    "learning_rate_effect",
    "compare_methods",
    "plot_comparison",
    "analyze_lab10",
    # Lab 11: Batch RL
    "batch_monte_carlo",
    "batch_td_zero",
    "batch_td_lambda",
    "discount_factor_analysis",
    "lambda_sensitivity_analysis",
    "convergence_analysis",
    "plot_discount_factor_effect",
    "plot_lambda_analysis",
    "plot_convergence_comparison",
    "analyze_lab11",
    # Lab 12: DQN
    "QNetwork",
    "ExperienceReplay",
    "dqn_training",
    "dqn_testing",
    "compare_with_random",
    "plot_dqn_training",
    "analyze_lab12",
    # OEL2: Comprehensive
    "comprehensive_algorithm_comparison",
    "discount_factor_comprehensive",
    "lambda_comprehensive_analysis",
    "environment_scaling_analysis",
    "convergence_speed_comparison",
    "plot_comprehensive_analysis",
    "analyze_oel2",
    # Visualization
    "plot_episode_rewards",
    "plot_grid_policy",
    "plot_value_heatmap",
    "plot",
    "plot_convergence_delta",
    "plot_values",
    "plot_policy",
    "simple_plot",
    "plot_convergence",
    "compare_mc_td_convergence",
    # Utility
    "query",
    "list_functions",
    "show_lib",
    # Lab Workflows
    "flowlab1",
    "flowlab2",
    "flowlab3",
    "flowlab4",
    "flowlab5",
    "flowlab6",
    "flowlab7",
    "flowlab8",
    "flowlab9",
    "flowlab10",
    "flowlab11",
    "flowlab12",
    "flowoel",
    "flowoel2",
]
