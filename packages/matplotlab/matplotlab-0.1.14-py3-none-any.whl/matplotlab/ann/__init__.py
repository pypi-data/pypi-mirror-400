"""
Matplotlab - Artificial Neural Networks (ANN) Module

Extended plotting and machine learning utilities for neural networks.
Provides essential functions for tensor operations, perceptrons, ADALINE,
MLPs, CNNs, CNN filters, and transfer learning.

Usage:
    from matplotlab import ann
    
    # See all available functions
    ann.list_functions()
    
    # View function documentation and source code
    ann.train_perceptron.show()
    
    # Search for specific functionality
    ann.query("How to train a CNN?")

Author: ML Community
Module: ANN (Artificial Neural Networks)
Complete Implementation
"""

from ._code_inspector import ShowableFunction
from ._utils import query

# ============================================================================
# Lab 1: Tensor Operations (20 functions)
# ============================================================================
from .tensors import (
    # Basic tensor creation
    create_scalar,
    create_vector,
    create_matrix,
    create_tensor_3d,
    tensor_element_wise_add,
    tensor_matrix_mul,
    tensor_mean,
    tensor_sum,
    tensor_reshape,
    tensor_arange,
    compute_gradient_simple,
    
    # Image operations
    create_image_tensor,
    normalize_image,
    apply_kernel_filter,
    calculate_average_brightness,
    
    # Sensor data operations
    create_sensor_data,
    reshape_to_batches,
    calculate_batch_averages,
    calculate_sensor_type_averages,
    
    # System utilities
    check_cuda_availability,
    get_pytorch_version
)

# ============================================================================
# Lab 2: Perceptron (6 functions)
# ============================================================================
from .perceptron import (
    generate_linearly_separable_data,
    train_perceptron,
    plot_perceptron_decision_boundary,
    plot_decision_regions_mlxtend,
    plot_data_scatter,
    compare_perceptron_iterations
)

# ============================================================================
# Lab 3: ADALINE - PyTorch & NumPy (10 functions + 4 classes)
# ============================================================================
from .adaline_pytorch import (
    # Classes
    manual_ADALINE,
    semi_ADALINE,
    automatic_ADALINE,
    
    # Functions
    loss_function,
    train_manual_adaline,
    train_semi_adaline,
    train_automatic_adaline,
    evaluate_adaline_accuracy,
    plot_adaline_loss
)

from .adaline_numpy import (
    # Class
    AdalineNumPy,
    
    # Functions
    train_adaline_numpy,
    evaluate_adaline_numpy,
    plot_adaline_cost,
    compare_learning_rates
)

# ============================================================================
# Lab 4: Multi-Layer Perceptron (11 functions)
# ============================================================================
from .mlp import (
    sigmoid,
    sigmoid_derivative,
    train_mlp_xor_numpy,
    predict_mlp_numpy,
    create_mlp_model,
    train_mlp_xor_pytorch,
    train_classification_mlp,
    train_regression_mlp,
    evaluate_classification,
    evaluate_regression,
    plot_loss_curve
)

# ============================================================================
# Lab 5: Convolutional Neural Networks (10 functions)
# ============================================================================
from .cnn import (
    # Simple CNN creation functions
    create_fashion_cnn,
    create_deep_cnn,
    
    # Functions
    load_fashion_mnist,
    train_cnn,
    evaluate_cnn,
    plot_confusion_matrix,
    plot_training_loss,
    visualize_predictions,
    save_model,
    load_model
)

# ============================================================================
# Lab 6: CNN Filters (7 functions)
# ============================================================================
from .cnn_filters import (
    apply_cnn_filter,
    get_available_filters,
    load_and_prepare_image,
    visualize_original_image,
    visualize_filtered_image,
    compare_all_filters,
    create_filter_model
)

# ============================================================================
# Lab 7: Transfer Learning (4 functions)
# ============================================================================
from .transfer_learning import (
    load_pretrained_model,
    train_transfer_model,
    evaluate_transfer_model,
    load_fashion_mnist as load_fashion_mnist_transfer
)
# ============================================================================
# Lab 8: Autoencoders (13 functions + 3 classes)
# ============================================================================
from .autoencoder import (
    # Model Classes
    UndercompleteAutoencoder,
    DenoisingAutoencoder,
    ConvolutionalAutoencoder,
    
    # Dataset Loading
    load_mnist_for_autoencoder,
    load_fashion_mnist_for_autoencoder,
    
    # Training Functions
    train_undercomplete_autoencoder,
    train_denoising_autoencoder,
    train_convolutional_autoencoder,
    
    # Visualization Functions
    plot_autoencoder_loss,
    visualize_reconstructions,
    visualize_denoising,
    compare_all_autoencoders
)

# ============================================================================
# Lab 9: Recurrent Neural Networks (11 functions + 3 classes)
# ============================================================================
from .rnn import (
    # Model Classes
    SimpleRNN,
    SentimentRNN,
    QADataset,
    
    # Text Processing
    tokenize_text,
    build_vocab_from_dataframe,
    text_to_indices,
    
    # Training Functions
    train_qa_rnn,
    train_sentiment_rnn,
    
    # Evaluation & Prediction
    predict_qa_answer,
    evaluate_sentiment_model,
    
    # Visualization
    plot_rnn_training_loss,
    plot_sentiment_training_curves,
    plot_confusion_matrix_sentiment
)

# ============================================================================
# Lab 10: LSTM (11 functions + 2 classes)
# ============================================================================
from .lstm import (
    # Model Classes
    NextWordLSTM,
    TextGenerationLSTM,
    NextWordDataset,
    
    # Text Processing
    tokenize_lstm_text,
    make_vocab,
    create_sequences,
    
    # Training Functions
    train_next_word_lstm,
    train_text_generation_lstm,
    
    # Generation & Prediction
    predict_next_word,
    generate_text,
    
    # Visualization
    plot_lstm_training_curves,
    plot_text_generation_loss,
    compare_predictions
)
# ============================================================================
# Lab Workflow Functions (11 lab flows + 2 OEL tasks + list function = 14 functions)
# ============================================================================
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
    flowoel1,
    flowoel2,
    list_ann_labs
)

# ============================================================================
# Module-level functions
# ============================================================================

def list_functions():
    """
    List all available functions in the ANN module organized by lab.
    
    Returns:
        None (prints formatted output)
    
    Example:
        >>> from matplotlab import ann
        >>> ann.list_functions()
    """
    import sys
    module = sys.modules[__name__]
    
    print("\n" + "="*70)
    print("MATPLOTLAB - ANN MODULE")
    print("Artificial Neural Networks Library")
    print("="*70)
    
    labs = {
        "Lab 1: Tensor Operations": [
            "create_scalar", "create_vector", "create_matrix", "create_tensor_3d",
            "tensor_element_wise_add", "tensor_matrix_mul", "tensor_mean", "tensor_sum",
            "tensor_reshape", "tensor_arange", "compute_gradient_simple",
            "create_image_tensor", "normalize_image", "apply_kernel_filter",
            "calculate_average_brightness", "create_sensor_data", "reshape_to_batches",
            "calculate_batch_averages", "calculate_sensor_type_averages",
            "check_cuda_availability", "get_pytorch_version"
        ],
        "Lab 2: Perceptron": [
            "generate_linearly_separable_data", "train_perceptron",
            "plot_perceptron_decision_boundary", "plot_decision_regions_mlxtend",
            "plot_data_scatter", "compare_perceptron_iterations"
        ],
        "Lab 3: ADALINE (PyTorch)": [
            "manual_ADALINE", "semi_ADALINE", "automatic_ADALINE",
            "loss_function", "train_manual_adaline", "train_semi_adaline",
            "train_automatic_adaline", "evaluate_adaline_accuracy", "plot_adaline_loss"
        ],
        "Lab 3: ADALINE (NumPy)": [
            "AdalineNumPy", "train_adaline_numpy", "evaluate_adaline_numpy",
            "plot_adaline_cost", "compare_learning_rates"
        ],
        "Lab 4: Multi-Layer Perceptron": [
            "sigmoid", "sigmoid_derivative", "train_mlp_xor_numpy",
            "predict_mlp_numpy", "create_mlp_model", "train_mlp_xor_pytorch",
            "train_classification_mlp", "train_regression_mlp",
            "evaluate_classification", "evaluate_regression", "plot_loss_curve"
        ],
        "Lab 5: CNNs (Convolutional Neural Networks)": [
            "create_fashion_cnn", "create_deep_cnn", "load_fashion_mnist", "train_cnn",
            "evaluate_cnn", "plot_confusion_matrix", "plot_training_loss",
            "visualize_predictions", "save_model", "load_model"
        ],
        "Lab 6: CNN Filters": [
            "apply_cnn_filter", "get_available_filters", "load_and_prepare_image",
            "visualize_original_image", "visualize_filtered_image", 
            "compare_all_filters", "create_filter_model"
        ],
        "Lab 7: Transfer Learning": [
            "load_pretrained_model", "train_transfer_model",
            "evaluate_transfer_model", "load_fashion_mnist_transfer"
        ],
        "Lab 8: Autoencoders": [
            "UndercompleteAutoencoder", "DenoisingAutoencoder", "ConvolutionalAutoencoder",
            "load_mnist_for_autoencoder", "load_fashion_mnist_for_autoencoder",
            "train_undercomplete_autoencoder", "train_denoising_autoencoder",
            "train_convolutional_autoencoder", "plot_autoencoder_loss",
            "visualize_reconstructions", "visualize_denoising",
            "compare_all_autoencoders"
        ],
        "Lab 9: RNN (Recurrent Neural Networks)": [
            "SimpleRNN", "SentimentRNN", "QADataset",
            "tokenize_text", "build_vocab_from_dataframe", "text_to_indices",
            "train_qa_rnn", "train_sentiment_rnn",
            "predict_qa_answer", "evaluate_sentiment_model",
            "plot_rnn_training_loss", "plot_sentiment_training_curves",
            "plot_confusion_matrix_sentiment"
        ],
        "Lab 10: LSTM (Long Short-Term Memory)": [
            "NextWordLSTM", "TextGenerationLSTM", "NextWordDataset",
            "tokenize_lstm_text", "make_vocab", "create_sequences",
            "train_next_word_lstm", "train_text_generation_lstm",
            "predict_next_word", "generate_text",
            "plot_lstm_training_curves", "plot_text_generation_loss",
            "compare_predictions"
        ],
        "LAB WORKFLOWS (12 functions)": [
            "flowlab1", "flowlab2", "flowlab3", "flowlab4",
            "flowlab5", "flowlab6", "flowlab7", "flowlab8",
            "flowlab9", "flowlab10", "flowoel1", "flowoel2"
        ]
    }
    
    total_functions = 0
    for lab_name, functions in labs.items():
        print(f"\n{lab_name}")
        print("-" * 70)
        for func_name in functions:
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                # Get first line of docstring if available
                doc = func.__doc__.strip().split('\n')[0] if func.__doc__ else "No description"
                print(f"  • {func_name}() - {doc}")
                total_functions += 1
            else:
                print(f"  • {func_name}() - [NOT FOUND]")
    
    print("\n" + "="*70)
    print(f"Total: {total_functions} functions/classes + 12 lab workflows (10 labs + 2 OEL)")
    print("="*70)
    print("\nUsage:")
    print("  • View function details: ann.function_name.show()")
    print("  • Search functionality: ann.query('your search term')")
    print("  • Example: ann.train_perceptron.show()")
    print("="*70 + "\n")


def show_lib():
    """
    Display all required library imports for ANN labs.
    
    Shows the complete list of imports needed across all 7 ANN labs
    with correct syntax. Use this when you forget import statements.
    
    Example:
    --------
    >>> from matplotlab import ann
    >>> ann.show_lib()  # See all required imports
    """
    print("=" * 70)
    print("REQUIRED LIBRARIES FOR ANN MODULE (All 7 Labs)")
    print("=" * 70)
    print()
    
    print("# Core Scientific Computing")
    print("-" * 70)
    print("import numpy as np")
    print("import pandas as pd")
    print("import matplotlib.pyplot as plt")
    print("import seaborn as sns")
    print()
    
    print("# PyTorch (Deep Learning Framework)")
    print("-" * 70)
    print("import torch")
    print("import torch.nn as nn")
    print("import torch.optim as optim")
    print("import torch.nn.functional as F")
    print("from torch.autograd import grad")
    print("from torch.utils.data import TensorDataset, DataLoader, random_split")
    print()
    
    print("# TorchVision (Computer Vision)")
    print("-" * 70)
    print("from torchvision import datasets, transforms")
    print()
    
    print("# TensorFlow/Keras (For CNN Filters Lab)")
    print("-" * 70)
    print("import tensorflow as tf")
    print("from tensorflow.keras import layers, models")
    print()
    
    print("# Scikit-Learn (Machine Learning)")
    print("-" * 70)
    print("from sklearn.datasets import make_blobs, load_iris")
    print("from sklearn.preprocessing import StandardScaler")
    print("from sklearn.linear_model import Perceptron")
    print("from sklearn.model_selection import train_test_split")
    print("from sklearn.inspection import DecisionBoundaryDisplay")
    print("from sklearn.metrics import (")
    print("    accuracy_score, confusion_matrix, precision_score,")
    print("    recall_score, f1_score, RocCurveDisplay,")
    print("    mean_squared_error, mean_absolute_error, r2_score")
    print(")")
    print()
    
    print("# Additional Visualization")
    print("-" * 70)
    print("from mlxtend.plotting import plot_decision_regions")
    print("from PIL import Image")
    print()
    
    print("=" * 70)
    print("INSTALLATION COMMANDS")
    print("=" * 70)
    print()
    print("# Core packages")
    print("pip install numpy pandas matplotlib seaborn")
    print()
    print("# PyTorch (CPU version)")
    print("pip install torch torchvision")
    print()
    print("# TensorFlow")
    print("pip install tensorflow")
    print()
    print("# Scikit-learn and utilities")
    print("pip install scikit-learn mlxtend pillow")
    print()
    print("=" * 70)
    print()
    print("NOTES:")
    print("  - numpy: Array operations and numerical computing")
    print("  - pandas: Data manipulation and analysis")
    print("  - matplotlib/seaborn: Plotting and visualization")
    print("  - torch: PyTorch deep learning framework")
    print("  - tensorflow: TensorFlow/Keras for CNN filters")
    print("  - scikit-learn: Classical ML algorithms and utilities")
    print("  - mlxtend: Machine learning extensions (decision regions)")
    print("  - PIL: Image processing library")
    print("=" * 70)


# ============================================================================
# Wrap all functions with ShowableFunction to add .show() method
# ============================================================================

_functions_to_wrap = [
    # Lab 1
    create_scalar, create_vector, create_matrix, create_tensor_3d,
    tensor_element_wise_add, tensor_matrix_mul, tensor_mean, tensor_sum,
    tensor_reshape, tensor_arange, compute_gradient_simple,
    create_image_tensor, normalize_image, apply_kernel_filter,
    calculate_average_brightness, create_sensor_data, reshape_to_batches,
    calculate_batch_averages, calculate_sensor_type_averages,
    check_cuda_availability, get_pytorch_version,
    # Lab 2
    generate_linearly_separable_data, train_perceptron,
    plot_perceptron_decision_boundary, plot_decision_regions_mlxtend,
    plot_data_scatter, compare_perceptron_iterations,
    # Lab 3 PyTorch
    loss_function, train_manual_adaline, train_semi_adaline,
    train_automatic_adaline, evaluate_adaline_accuracy, plot_adaline_loss,
    # Lab 3 NumPy
    train_adaline_numpy, evaluate_adaline_numpy,
    plot_adaline_cost, compare_learning_rates,
    # Lab 4
    sigmoid, sigmoid_derivative, train_mlp_xor_numpy,
    predict_mlp_numpy, create_mlp_model, train_mlp_xor_pytorch,
    train_classification_mlp, train_regression_mlp,
    evaluate_classification, evaluate_regression, plot_loss_curve,
    # Lab 5
    create_fashion_cnn, create_deep_cnn, load_fashion_mnist, train_cnn,
    evaluate_cnn, plot_confusion_matrix, plot_training_loss,
    visualize_predictions, save_model, load_model,
    # Lab 6
    apply_cnn_filter, get_available_filters, load_and_prepare_image,
    visualize_original_image, visualize_filtered_image,
    compare_all_filters, create_filter_model,
    # Lab 7
    load_pretrained_model, train_transfer_model,
    evaluate_transfer_model, load_fashion_mnist_transfer,
    # Lab 8 - Functions
    load_mnist_for_autoencoder, load_fashion_mnist_for_autoencoder,
    train_undercomplete_autoencoder, train_denoising_autoencoder,
    train_convolutional_autoencoder, plot_autoencoder_loss,
    visualize_reconstructions, visualize_denoising,
    compare_all_autoencoders,
    # Lab 9 - Functions
    tokenize_text, build_vocab_from_dataframe, text_to_indices,
    train_qa_rnn, train_sentiment_rnn, predict_qa_answer,
    evaluate_sentiment_model, plot_rnn_training_loss,
    plot_sentiment_training_curves, plot_confusion_matrix_sentiment,
    # Lab 10 - Functions
    tokenize_lstm_text, make_vocab, create_sequences,
    train_next_word_lstm, train_text_generation_lstm,
    predict_next_word, generate_text, plot_lstm_training_curves,
    plot_text_generation_loss, compare_predictions
]

# Note: Model classes (UndercompleteAutoencoder, DenoisingAutoencoder, ConvolutionalAutoencoder,
# SimpleRNN, SentimentRNN, QADataset, NextWordLSTM, TextGenerationLSTM, NextWordDataset,
# manual_ADALINE, semi_ADALINE, automatic_ADALINE, AdalineNumPy) are not wrapped
# because they are classes, not functions, and don't need the .show() method

for func in _functions_to_wrap:
    # Only wrap if not already wrapped (to avoid double-wrapping)
    if not isinstance(func, ShowableFunction):
        wrapped = ShowableFunction(func)
        globals()[func.__name__] = wrapped

# Clean up internal variables to avoid polluting module namespace
del ShowableFunction  # Remove the class from module namespace
del wrapped  # Remove the temporary variable

# ============================================================================
# Export all public symbols
# ============================================================================

__all__ = [
    # Module utilities
    'list_functions',
    'show_lib',
    'query',
    
    # Lab Workflows (14 functions: 11 labs + 2 OEL tasks + list function)
    'flowlab1', 'flowlab2', 'flowlab3', 'flowlab4',
    'flowlab5', 'flowlab6', 'flowlab7', 'flowlab8',
    'flowlab9', 'flowlab10', 'flowlab11', 'flowoel1', 'flowoel2',
    'list_ann_labs',
    
    # Lab 1 (21 functions)
    'create_scalar', 'create_vector', 'create_matrix', 'create_tensor_3d',
    'tensor_element_wise_add', 'tensor_matrix_mul', 'tensor_mean', 'tensor_sum',
    'tensor_reshape', 'tensor_arange', 'compute_gradient_simple',
    'create_image_tensor', 'normalize_image', 'apply_kernel_filter',
    'calculate_average_brightness', 'create_sensor_data', 'reshape_to_batches',
    'calculate_batch_averages', 'calculate_sensor_type_averages',
    'check_cuda_availability', 'get_pytorch_version',
    
    # Lab 2 (6 functions)
    'generate_linearly_separable_data', 'train_perceptron',
    'plot_perceptron_decision_boundary', 'plot_decision_regions_mlxtend',
    'plot_data_scatter', 'compare_perceptron_iterations',
    
    # Lab 3 PyTorch (9 items: 3 classes + 6 functions)
    'manual_ADALINE', 'semi_ADALINE', 'automatic_ADALINE',
    'loss_function', 'train_manual_adaline', 'train_semi_adaline',
    'train_automatic_adaline', 'evaluate_adaline_accuracy', 'plot_adaline_loss',
    
    # Lab 3 NumPy (5 items: 1 class + 4 functions)
    'AdalineNumPy', 'train_adaline_numpy', 'evaluate_adaline_numpy',
    'plot_adaline_cost', 'compare_learning_rates',
    
    # Lab 4 (11 functions)
    'sigmoid', 'sigmoid_derivative', 'train_mlp_xor_numpy',
    'predict_mlp_numpy', 'create_mlp_model', 'train_mlp_xor_pytorch',
    'train_classification_mlp', 'train_regression_mlp',
    'evaluate_classification', 'evaluate_regression', 'plot_loss_curve',
    
    # Lab 5 (10 functions)
    'create_fashion_cnn', 'create_deep_cnn', 'load_fashion_mnist', 'train_cnn',
    'evaluate_cnn', 'plot_confusion_matrix', 'plot_training_loss',
    'visualize_predictions', 'save_model', 'load_model',
    
    # Lab 6 (7 functions)
    'apply_cnn_filter', 'get_available_filters', 'load_and_prepare_image',
    'visualize_original_image', 'visualize_filtered_image',
    'compare_all_filters', 'create_filter_model',
    
    # Lab 7 (4 functions)
    'load_pretrained_model', 'train_transfer_model',
    'evaluate_transfer_model', 'load_fashion_mnist_transfer',
    
    # Lab 8 (12 items: 3 classes + 9 functions)
    'UndercompleteAutoencoder', 'DenoisingAutoencoder', 'ConvolutionalAutoencoder',
    'load_mnist_for_autoencoder', 'load_fashion_mnist_for_autoencoder',
    'train_undercomplete_autoencoder', 'train_denoising_autoencoder',
    'train_convolutional_autoencoder', 'plot_autoencoder_loss',
    'visualize_reconstructions', 'visualize_denoising',
    'compare_all_autoencoders',
    
    # Lab 9 (14 items: 3 classes + 11 functions)
    'SimpleRNN', 'SentimentRNN', 'QADataset',
    'tokenize_text', 'build_vocab_from_dataframe', 'text_to_indices',
    'train_qa_rnn', 'train_sentiment_rnn', 'predict_qa_answer',
    'evaluate_sentiment_model', 'plot_rnn_training_loss',
    'plot_sentiment_training_curves', 'plot_confusion_matrix_sentiment',
    
    # Lab 10 (14 items: 3 classes + 11 functions)
    'NextWordLSTM', 'TextGenerationLSTM', 'NextWordDataset',
    'tokenize_lstm_text', 'make_vocab', 'create_sequences',
    'train_next_word_lstm', 'train_text_generation_lstm',
    'predict_next_word', 'generate_text', 'plot_lstm_training_curves',
    'plot_text_generation_loss', 'compare_predictions'
]

# Total: 114 functions/classes + 12 lab workflows across 10 labs
