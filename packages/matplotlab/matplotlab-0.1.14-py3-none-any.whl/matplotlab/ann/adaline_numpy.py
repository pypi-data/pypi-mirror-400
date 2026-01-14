"""
Lab 3 - ADALINE implementation using NumPy (Delta Rule).
Pure NumPy implementation without PyTorch.
"""

import numpy as np
from matplotlib import pyplot as plt


class AdalineNumPy:
    """ADALINE (Adaptive Linear Neuron) implementation using NumPy."""
    
    def __init__(self, n_features=None, learning_rate=0.01, epochs=100):
        """
        Initialize ADALINE.
        
        Parameters:
        -----------
        n_features : int or None
            Number of features (optional, for compatibility)
        learning_rate : float
            Learning rate for weight updates (default: 0.01)
        epochs : int
            Number of training epochs (default: 100)
        """
        self.n_features = n_features
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights = None
        self.bias = None
        self.cost_history = []
    
    def fit(self, X, y):
        """
        Train ADALINE on given data using Delta Rule.
        
        Parameters:
        -----------
        X : np.ndarray
            Training features of shape (n_samples, n_features)
        y : np.ndarray
            Training labels of shape (n_samples,)
        
        Returns:
        --------
        self
            Returns self for method chaining
        """
        n_samples, n_features = X.shape
        
        # Initialize weights and bias
        self.weights = np.zeros(n_features)
        self.bias = 0.0
        
        # Training loop
        for epoch in range(self.epochs):
            # Forward pass
            y_pred = self.predict_continuous(X)
            
            # Compute error
            errors = y - y_pred
            
            # Compute cost (MSE)
            cost = np.mean(errors ** 2)
            self.cost_history.append(cost)
            
            # Update weights using Delta Rule
            self.weights += self.learning_rate * X.T.dot(errors) / n_samples
            self.bias += self.learning_rate * np.sum(errors) / n_samples
        
        return self
    
    def predict_continuous(self, X):
        """
        Compute continuous predictions (linear activation).
        
        Parameters:
        -----------
        X : np.ndarray
            Feature matrix
        
        Returns:
        --------
        np.ndarray
            Continuous predictions
        """
        return X.dot(self.weights) + self.bias
    
    def predict(self, X, threshold=0.5):
        """
        Predict class labels using threshold.
        
        Parameters:
        -----------
        X : np.ndarray
            Feature matrix
        threshold : float
            Classification threshold (default: 0.5)
        
        Returns:
        --------
        np.ndarray
            Binary predictions (0 or 1)
        """
        continuous_output = self.predict_continuous(X)
        return np.where(continuous_output >= threshold, 1, 0)


def train_adaline_numpy(X, y, learning_rate=0.01, epochs=100):
    """
    Train ADALINE model using NumPy.
    
    Parameters:
    -----------
    X : np.ndarray
        Training features
    y : np.ndarray
        Training labels
    learning_rate : float
        Learning rate (default: 0.01)
    epochs : int
        Number of epochs (default: 100)
    
    Returns:
    --------
    AdalineNumPy
        Trained ADALINE model
    """
    model = AdalineNumPy(learning_rate=learning_rate, epochs=epochs)
    model.fit(X, y)
    return model


def evaluate_adaline_numpy(model, X_train, y_train, X_test, y_test):
    """
    Evaluate ADALINE model on train and test sets.
    
    Parameters:
    -----------
    model : AdalineNumPy
        Trained ADALINE model
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training labels
    X_test : np.ndarray
        Test features
    y_test : np.ndarray
        Test labels
    
    Returns:
    --------
    dict
        Dictionary containing train and test accuracy
    """
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_accuracy = np.mean(train_pred == y_train) * 100
    test_accuracy = np.mean(test_pred == y_test) * 100
    
    return {
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy
    }


def plot_adaline_cost(model, title="ADALINE Cost Function (Delta Rule)"):
    """
    Plot ADALINE cost history.
    
    Parameters:
    -----------
    model : AdalineNumPy
        Trained ADALINE model with cost_history
    title : str
        Plot title
    """
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(model.cost_history) + 1), model.cost_history)
    plt.xlabel('Epoch')
    plt.ylabel('Mean Squared Error')
    plt.title(title)
    plt.grid(True)
    plt.show()


def compare_learning_rates(X, y, learning_rates=[0.001, 0.01, 0.1], epochs=100):
    """
    Compare ADALINE performance with different learning rates.
    
    Parameters:
    -----------
    X : np.ndarray
        Training features
    y : np.ndarray
        Training labels
    learning_rates : list
        List of learning rates to compare
    epochs : int
        Number of epochs for each model
    
    Returns:
    --------
    dict
        Dictionary mapping learning rates to trained models
    """
    models = {}
    
    plt.figure(figsize=(12, 6))
    
    for lr in learning_rates:
        model = AdalineNumPy(learning_rate=lr, epochs=epochs)
        model.fit(X, y)
        models[lr] = model
        
        plt.plot(range(1, epochs + 1), model.cost_history, label=f'LR = {lr}')
    
    plt.xlabel('Epoch')
    plt.ylabel('Mean Squared Error')
    plt.title('Learning Rate Comparison')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return models
