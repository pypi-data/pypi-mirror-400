"""
Lab 3 - ADALINE (Adaptive Linear Neuron) implementations using PyTorch.
Includes manual, semi-manual, and automatic implementations.
"""

import torch
import torch.nn as nn
from torch.autograd import grad
from matplotlib import pyplot as plt


# ============================================================================
# Manual ADALINE Implementation (Full Manual Backprop)
# ============================================================================

class manual_ADALINE:
    """ADALINE with manually computed gradients."""
    
    def __init__(self, num_features=None, input_size=None):
        # Support both parameter names
        if num_features is None and input_size is None:
            raise ValueError("Must provide either num_features or input_size")
        features = num_features if num_features is not None else input_size
        self.num_features = features
        self.weights = torch.zeros(features, 1, dtype=torch.float32)
        self.biases = torch.zeros(1, dtype=torch.float32)
    
    def forward(self, x):
        """Forward pass: y = Wx + b"""
        return torch.mm(x, self.weights) + self.biases
    
    def backward(self, x, yhat, y):
        """
        Backward pass: compute gradients manually.
        
        Returns:
        --------
        tuple
            (grad_weights, grad_biases)
        """
        grad_loss = (yhat.view(-1, 1) - y.view(-1, 1))
        grad_loss_weights = torch.mm(x.t(), grad_loss) / len(y)
        grad_loss_biases = torch.sum(grad_loss) / len(y)
        return grad_loss_weights, grad_loss_biases


# ============================================================================
# Semi-Manual ADALINE Implementation (Using autograd)
# ============================================================================

class semi_ADALINE:
    """ADALINE using PyTorch autograd for gradient computation."""
    
    def __init__(self, num_features=None, input_size=None):
        # Support both parameter names
        if num_features is None and input_size is None:
            raise ValueError("Must provide either num_features or input_size")
        features = num_features if num_features is not None else input_size
        self.num_features = features
        self.weights = torch.zeros(features, 1, dtype=torch.float32, requires_grad=True)
        self.bias = torch.zeros(1, dtype=torch.float32, requires_grad=True)
    
    def forward(self, x):
        """Forward pass: y = Wx + b"""
        return torch.mm(x, self.weights) + self.bias


# ============================================================================
# Automatic ADALINE Implementation (nn.Module)
# ============================================================================

class automatic_ADALINE(nn.Module):
    """ADALINE as a PyTorch nn.Module with automatic differentiation."""
    
    def __init__(self, num_features=None, input_size=None):
        super(automatic_ADALINE, self).__init__()
        # Support both parameter names
        if num_features is None and input_size is None:
            raise ValueError("Must provide either num_features or input_size")
        features = num_features if num_features is not None else input_size
        self.linear = nn.Linear(features, 1)
        with torch.no_grad():
            self.linear.weight.zero_()
            self.linear.bias.zero_()
    
    def forward(self, x):
        return self.linear(x).view(-1)


# ============================================================================
# Training Functions
# ============================================================================

def loss_function(yhat, y):
    """Mean Squared Error loss."""
    return torch.mean((yhat - y) ** 2)


def train_manual_adaline(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    """
    Train manual ADALINE with manually computed gradients.
    
    Parameters:
    -----------
    model : manual_ADALINE
        ADALINE model instance
    x : torch.Tensor
        Training features
    y : torch.Tensor
        Training labels
    total_epochs : int
        Number of training epochs
    lr : float
        Learning rate (default: 0.01)
    seed : int
        Random seed (default: 53)
    batch_size : int
        Mini-batch size (default: 16)
    
    Returns:
    --------
    list
        List of loss values per epoch
    """
    cost = []
    torch.manual_seed(seed)
    
    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)
        
        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch].view(-1, 1)
            yhat = model.forward(xb)
            loss = loss_function(yhat, yb)
            gradient_W, gradient_B = model.backward(xb, yhat, yb)
            
            with torch.no_grad():
                model.weights -= lr * gradient_W
                model.biases -= lr * gradient_B
        
        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = loss_function(yhat_full, y.view(-1, 1))
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())
    
    return cost


def train_semi_adaline(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    """
    Train semi-manual ADALINE using autograd for gradients.
    
    Parameters:
    -----------
    model : semi_ADALINE
        ADALINE model instance
    x : torch.Tensor
        Training features
    y : torch.Tensor
        Training labels
    total_epochs : int
        Number of training epochs
    lr : float
        Learning rate (default: 0.01)
    seed : int
        Random seed (default: 53)
    batch_size : int
        Mini-batch size (default: 16)
    
    Returns:
    --------
    list
        List of loss values per epoch
    """
    cost = []
    torch.manual_seed(seed)
    
    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)
        
        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch]
            yhat = model.forward(xb)
            loss = loss_function(yhat, yb)
            
            gradient_W = grad(loss, model.weights, retain_graph=True)[0]
            gradient_B = grad(loss, model.bias)[0]
            
            with torch.no_grad():
                model.weights -= lr * gradient_W
                model.bias -= lr * gradient_B
        
        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = loss_function(yhat_full, y)
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())
    
    return cost


def train_automatic_adaline(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    """
    Train automatic ADALINE using nn.Module and optimizer.
    
    Parameters:
    -----------
    model : automatic_ADALINE
        ADALINE model instance
    x : torch.Tensor
        Training features
    y : torch.Tensor
        Training labels
    total_epochs : int
        Number of training epochs
    lr : float
        Learning rate (default: 0.01)
    seed : int
        Random seed (default: 53)
    batch_size : int
        Mini-batch size (default: 16)
    
    Returns:
    --------
    list
        List of loss values per epoch
    """
    cost = []
    torch.manual_seed(seed)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    
    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)
        
        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch]
            yhat = model.forward(xb)
            loss = torch.nn.functional.mse_loss(yhat, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = torch.nn.functional.mse_loss(yhat_full, y)
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())
    
    return cost


# ============================================================================
# Evaluation Functions
# ============================================================================

def evaluate_adaline_accuracy(model, X_train, y_train, X_test, y_test, threshold=0.5):
    """
    Evaluate ADALINE model accuracy on train and test sets.
    
    Parameters:
    -----------
    model : manual_ADALINE, semi_ADALINE, or automatic_ADALINE
        Trained ADALINE model
    X_train : torch.Tensor
        Training features
    y_train : torch.Tensor
        Training labels
    X_test : torch.Tensor
        Test features
    y_test : torch.Tensor
        Test labels
    threshold : float
        Classification threshold (default: 0.5)
    
    Returns:
    --------
    dict
        Dictionary with 'train_accuracy' and 'test_accuracy' keys
    """
    train_ones = torch.ones(y_train.size())
    train_zeroes = torch.zeros(y_train.size())
    
    if isinstance(model, automatic_ADALINE):
        train_predictions = model.forward(X_train)
    else:
        train_predictions = model.forward(X_train).squeeze()
    
    train_accuracy = torch.mean(
        (torch.where(train_predictions > threshold, train_ones, train_zeroes).int() == y_train).float()
    )
    
    test_ones = torch.ones(y_test.size())
    test_zeroes = torch.zeros(y_test.size())
    
    if isinstance(model, automatic_ADALINE):
        test_predictions = model.forward(X_test)
    else:
        test_predictions = model.forward(X_test).squeeze()
    
    test_accuracy = torch.mean(
        (torch.where(test_predictions > threshold, test_ones, test_zeroes).int() == y_test).float()
    )
    
    return {
        'train_accuracy': train_accuracy.item() * 100,
        'test_accuracy': test_accuracy.item() * 100
    }


def plot_adaline_loss(cost, title="ADALINE Training Loss"):
    """
    Plot ADALINE training loss curve.
    
    Parameters:
    -----------
    cost : list
        List of loss values per epoch
    title : str
        Plot title (default: "ADALINE Training Loss")
    """
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(cost)), cost)
    plt.ylabel('Mean Squared Error')
    plt.xlabel('Epoch')
    plt.title(title)
    plt.grid(True)
    plt.show()
