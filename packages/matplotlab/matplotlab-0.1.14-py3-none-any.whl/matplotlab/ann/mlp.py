"""
Lab 4 - Multilayer Perceptron (MLP) implementations.
Contains manual backpropagation and PyTorch-based MLP training functions.
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader, random_split
from matplotlib import pyplot as plt


# ============================================================================
# Manual Backpropagation Functions (NumPy)
# ============================================================================

def sigmoid(x):
    """Sigmoid activation function."""
    return 1 / (1 + np.exp(-x))


def sigmoid_derivative(x):
    """Derivative of sigmoid function."""
    return x * (1 - x)


def train_mlp_xor_numpy(X, y, lr=0.5, epochs=10000, hidden_size=2):
    """
    Train a 2-layer MLP on XOR problem using manual backpropagation with NumPy.
    
    Parameters:
    -----------
    X : np.ndarray
        Input data of shape (n_samples, 2)
    y : np.ndarray
        Target labels of shape (n_samples, 1)
    lr : float
        Learning rate (default: 0.5)
    epochs : int
        Number of training epochs (default: 10000)
    hidden_size : int
        Number of hidden units (default: 2)
    
    Returns:
    --------
    dict
        Dictionary containing trained weights, biases, and final predictions
    """
    # Initialize weights and biases
    W1 = np.random.randn(2, hidden_size) * 0.01
    b1 = np.zeros((1, hidden_size))
    W2 = np.random.randn(hidden_size, 1) * 0.01
    b2 = np.zeros((1, 1))
    
    losses = []
    
    for epoch in range(epochs):
        # Forward pass
        z1 = np.dot(X, W1) + b1
        a1 = sigmoid(z1)
        z2 = np.dot(a1, W2) + b2
        y_pred = sigmoid(z2)
        
        # Compute loss
        loss = 0.5 * np.mean((y - y_pred) ** 2)
        losses.append(loss)
        
        # Backward pass
        delta2 = (y_pred - y) * sigmoid_derivative(y_pred)
        dW2 = np.dot(a1.T, delta2)
        db2 = np.sum(delta2, axis=0, keepdims=True)
        
        delta1 = np.dot(delta2, W2.T) * sigmoid_derivative(a1)
        dW1 = np.dot(X.T, delta1)
        db1 = np.sum(delta1, axis=0, keepdims=True)
        
        # Update weights
        W2 -= lr * dW2
        b2 -= lr * db2
        W1 -= lr * dW1
        b1 -= lr * db1
    
    return {
        'W1': W1,
        'b1': b1,
        'W2': W2,
        'b2': b2,
        'predictions': y_pred,
        'losses': losses
    }


def predict_mlp_numpy(X, W1, b1, W2, b2):
    """
    Make predictions using trained MLP weights.
    
    Parameters:
    -----------
    X : np.ndarray
        Input data
    W1, b1 : np.ndarray
        First layer weights and biases
    W2, b2 : np.ndarray
        Second layer weights and biases
    
    Returns:
    --------
    np.ndarray
        Predictions
    """
    z1 = np.dot(X, W1) + b1
    a1 = sigmoid(z1)
    z2 = np.dot(a1, W2) + b2
    y_pred = sigmoid(z2)
    return y_pred


# ============================================================================
# PyTorch MLP Functions
# ============================================================================

def create_mlp_model(input_size, hidden_sizes, output_size, activation='relu'):
    """
    Create a PyTorch MLP model with specified architecture.
    
    Parameters:
    -----------
    input_size : int
        Number of input features
    hidden_sizes : list of int
        Sizes of hidden layers
    output_size : int
        Number of output units
    activation : str
        Activation function ('relu', 'sigmoid', 'tanh')
    
    Returns:
    --------
    nn.Sequential
        PyTorch MLP model
    """
    layers = []
    prev_size = input_size
    
    activation_map = {
        'relu': nn.ReLU,
        'sigmoid': nn.Sigmoid,
        'tanh': nn.Tanh
    }
    
    act_fn = activation_map.get(activation.lower(), nn.ReLU)
    
    for hidden_size in hidden_sizes:
        layers.append(nn.Linear(prev_size, hidden_size))
        layers.append(act_fn())
        prev_size = hidden_size
    
    layers.append(nn.Linear(prev_size, output_size))
    
    return nn.Sequential(*layers)


def train_mlp_xor_pytorch(X, y, lr=0.5, epochs=1000, hidden_size=2):
    """
    Train MLP on XOR problem using PyTorch.
    
    Parameters:
    -----------
    X : torch.Tensor
        Input data of shape (n_samples, 2)
    y : torch.Tensor
        Target labels of shape (n_samples, 1)
    lr : float
        Learning rate (default: 0.5)
    epochs : int
        Number of training epochs (default: 1000)
    hidden_size : int
        Number of hidden units (default: 2)
    
    Returns:
    --------
    dict
        Dictionary containing trained model and loss history
    """
    model = nn.Sequential(
        nn.Linear(2, hidden_size),
        nn.Sigmoid(),
        nn.Linear(hidden_size, 1),
        nn.Sigmoid()
    )
    
    criterion = nn.BCELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    
    losses = []
    
    for epoch in range(epochs):
        outputs = model(X)
        loss = criterion(outputs, y)
        losses.append(loss.item())
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    return {
        'model': model,
        'losses': losses
    }


def train_classification_mlp(X, y, model_config, train_config):
    """
    Train a classification MLP with custom configuration.
    
    Parameters:
    -----------
    X : torch.Tensor
        Input features
    y : torch.Tensor
        Target labels
    model_config : dict
        Model configuration with keys: 'input_size', 'hidden_sizes', 'output_size'
    train_config : dict
        Training configuration with keys: 'lr', 'epochs', 'batch_size', 
        'train_split', 'optimizer'
    
    Returns:
    --------
    dict
        Dictionary containing trained model, train/test loaders, and metrics
    """
    # Create dataset
    tensor_dataset = TensorDataset(X, y)
    
    # Split dataset
    total_size = len(tensor_dataset)
    train_size = int(train_config.get('train_split', 0.8) * total_size)
    test_size = total_size - train_size
    
    train_dataset, test_dataset = random_split(
        tensor_dataset,
        [train_size, test_size],
        generator=torch.Generator().manual_seed(53)
    )
    
    # Create data loaders
    batch_size = train_config.get('batch_size', 32)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Create model
    model = nn.Sequential(
        nn.Linear(model_config['input_size'], model_config['hidden_sizes'][0]),
        nn.ReLU(),
        nn.Linear(model_config['hidden_sizes'][0], model_config['hidden_sizes'][1]),
        nn.ReLU(),
        nn.Linear(model_config['hidden_sizes'][1], model_config['output_size']),
        nn.Sigmoid()
    )
    
    criterion = nn.BCELoss()
    
    # Setup optimizer
    opt_name = train_config.get('optimizer', 'SGD')
    lr = train_config.get('lr', 0.01)
    
    if opt_name.lower() == 'adam':
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    elif opt_name.lower() == 'rmsprop':
        optimizer = torch.optim.RMSprop(model.parameters(), lr=lr)
    else:
        optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    
    # Training loop
    model.train()
    epochs = train_config.get('epochs', 1000)
    
    for epoch in range(epochs):
        for data, target in train_loader:
            optimizer.zero_grad()
            output = model(data).squeeze()
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
    
    return {
        'model': model,
        'train_loader': train_loader,
        'test_loader': test_loader,
        'criterion': criterion
    }


def train_regression_mlp(X, y, model_config, train_config):
    """
    Train a regression MLP with custom configuration.
    
    Parameters:
    -----------
    X : torch.Tensor
        Input features
    y : torch.Tensor
        Target values
    model_config : dict
        Model configuration with keys: 'input_size', 'hidden_sizes'
    train_config : dict
        Training configuration with keys: 'lr', 'epochs', 'batch_size', 
        'train_split', 'optimizer'
    
    Returns:
    --------
    dict
        Dictionary containing trained model, train/test loaders, and metrics
    """
    # Create dataset
    tensor_dataset = TensorDataset(X, y)
    
    # Split dataset
    total_size = len(tensor_dataset)
    train_size = int(train_config.get('train_split', 0.8) * total_size)
    test_size = total_size - train_size
    
    train_dataset, test_dataset = random_split(
        tensor_dataset,
        [train_size, test_size],
        generator=torch.Generator().manual_seed(53)
    )
    
    # Create data loaders
    batch_size = train_config.get('batch_size', 32)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Create model
    layers = []
    prev_size = model_config['input_size']
    
    for hidden_size in model_config['hidden_sizes']:
        layers.append(nn.Linear(prev_size, hidden_size))
        layers.append(nn.ReLU())
        prev_size = hidden_size
    
    layers.append(nn.Linear(prev_size, 1))
    model = nn.Sequential(*layers)
    
    criterion = nn.MSELoss()
    
    # Setup optimizer
    opt_name = train_config.get('optimizer', 'RMSprop')
    lr = train_config.get('lr', 0.01)
    
    if opt_name.lower() == 'adam':
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    elif opt_name.lower() == 'sgd':
        optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    else:
        optimizer = torch.optim.RMSprop(model.parameters(), lr=lr)
    
    # Training loop
    model.train()
    epochs = train_config.get('epochs', 1000)
    
    for epoch in range(epochs):
        for data, target in train_loader:
            optimizer.zero_grad()
            batch_outputs = model(data).squeeze()
            batch_loss = criterion(batch_outputs, target)
            batch_loss.backward()
            optimizer.step()
    
    return {
        'model': model,
        'train_loader': train_loader,
        'test_loader': test_loader,
        'criterion': criterion
    }


def evaluate_classification(model, test_loader, criterion):
    """
    Evaluate classification model on test set.
    
    Parameters:
    -----------
    model : nn.Module
        Trained model
    test_loader : DataLoader
        Test data loader
    criterion : nn.Module
        Loss criterion
    
    Returns:
    --------
    dict
        Dictionary containing accuracy, loss, predictions, and targets
    """
    model.eval()
    all_predictions = []
    all_targets = []
    total_correct = 0
    total_loss = 0
    total_samples = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            batch_output = model(data).squeeze()
            batch_loss = criterion(batch_output, target)
            total_loss += batch_loss.item()
            
            probabilities = torch.sigmoid(batch_output)
            pred = (probabilities > 0.5).float()
            all_predictions.extend(probabilities.cpu().numpy())
            all_targets.extend(target.cpu().numpy())
            
            total_correct += pred.eq(target).sum().item()
            total_samples += len(data)
    
    avg_loss = total_loss / len(test_loader)
    accuracy = 100. * total_correct / total_samples
    
    return {
        'accuracy': accuracy,
        'loss': avg_loss,
        'predictions': all_predictions,
        'targets': all_targets
    }


def evaluate_regression(model, test_loader, criterion):
    """
    Evaluate regression model on test set.
    
    Parameters:
    -----------
    model : nn.Module
        Trained model
    test_loader : DataLoader
        Test data loader
    criterion : nn.Module
        Loss criterion (MSELoss)
    
    Returns:
    --------
    dict
        Dictionary containing loss, predictions, and targets
    """
    model.eval()
    all_predictions = []
    all_targets = []
    total_loss = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            batch_outputs = model(data).squeeze()
            batch_loss = criterion(batch_outputs, target)
            total_loss += batch_loss.item()
            all_predictions.extend(batch_outputs.cpu().numpy())
            all_targets.extend(target.cpu().numpy())
    
    avg_loss = total_loss / len(test_loader)
    
    return {
        'loss': avg_loss,
        'predictions': all_predictions,
        'targets': all_targets
    }


def plot_loss_curve(losses, title="Training Loss", last_n=None):
    """
    Plot training loss curve.
    
    Parameters:
    -----------
    losses : list
        List of loss values
    title : str
        Plot title
    last_n : int or None
        Plot only last n epochs (if specified)
    """
    if last_n is not None:
        losses = losses[-last_n:]
    
    plt.figure(figsize=(10, 6))
    plt.plot(losses)
    plt.title(title)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.show()
