"""
Lab 2 - Perceptron implementations using sklearn.
Linear classification with decision boundary visualization.
"""

import numpy as np
import pandas as pd
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Perceptron
from sklearn.inspection import DecisionBoundaryDisplay
from mlxtend.plotting import plot_decision_regions
from matplotlib import pyplot as plt
import seaborn as sns


def generate_linearly_separable_data(n_samples=300, centers=2, random_state=54):
    """
    Generate a 2D synthetic dataset with linearly separable clusters.
    
    Parameters:
    -----------
    n_samples : int
        Total number of samples (default: 300)
    centers : int
        Number of cluster centers (default: 2)
    random_state : int
        Random seed for reproducibility (default: 54)
    
    Returns:
    --------
    tuple
        (X_raw, y_raw, X_prep, y_raw) where X_prep is standardized
    """
    X_raw, y_raw = make_blobs(n_samples=n_samples, centers=centers, random_state=random_state)
    
    scaler = StandardScaler()
    X_prep = scaler.fit_transform(X_raw)
    
    return X_raw, y_raw, X_prep, y_raw


def train_perceptron(X, y, max_iter=1000, random_state=None):
    """
    Train a perceptron on given data.
    
    Parameters:
    -----------
    X : np.ndarray
        Feature matrix
    y : np.ndarray
        Target labels
    max_iter : int
        Maximum number of iterations (default: 1000)
    random_state : int or None
        Random seed (default: None)
    
    Returns:
    --------
    Perceptron
        Trained perceptron model
    """
    perceptron = Perceptron(max_iter=max_iter, random_state=random_state)
    perceptron.fit(X, y)
    return perceptron


def plot_perceptron_decision_boundary(model, X, y, title="Perceptron Decision Boundary"):
    """
    Plot decision boundary with data points.
    
    Parameters:
    -----------
    model : Perceptron
        Trained perceptron model
    X : np.ndarray
        Feature matrix
    y : np.ndarray
        Target labels
    title : str
        Plot title (default: "Perceptron Decision Boundary")
    """
    plot = DecisionBoundaryDisplay.from_estimator(
        model, X, response_method='predict'
    )
    plot.ax_.scatter(X[:, 0], X[:, 1], c=y, edgecolor='k')
    plt.title(title)
    plt.show()


def plot_decision_regions_mlxtend(X, y, model, title="Decision Regions"):
    """
    Plot decision regions using mlxtend library.
    
    Parameters:
    -----------
    X : np.ndarray
        Feature matrix
    y : np.ndarray
        Target labels
    model : sklearn estimator
        Trained model
    title : str
        Plot title (default: "Decision Regions")
    """
    plot_decision_regions(X, y, clf=model)
    plt.title(title)
    plt.show()


def plot_data_scatter(X, y, title="Data Distribution"):
    """
    Plot scatter plot of 2D data with class labels.
    
    Parameters:
    -----------
    X : np.ndarray
        Feature matrix with 2 features
    y : np.ndarray
        Target labels
    title : str
        Plot title (default: "Data Distribution")
    """
    data = pd.DataFrame(X, columns=['X1', 'X2'])
    data['y'] = y
    
    sns.scatterplot(data=data, x='X1', y='X2', hue='y')
    plt.title(title)
    plt.show()


def compare_perceptron_iterations(X, y, max_iters=[1, 10, 100, 1000], random_state=53):
    """
    Compare perceptron convergence with different max_iter values.
    
    Parameters:
    -----------
    X : np.ndarray
        Feature matrix
    y : np.ndarray
        Target labels
    max_iters : list of int
        List of max_iter values to test (default: [1, 10, 100, 1000])
    random_state : int
        Random seed (default: 53)
    
    Returns:
    --------
    dict
        Dictionary mapping max_iter to (model, n_iter_) tuples
    """
    results = {}
    
    for max_iter in max_iters:
        model = Perceptron(max_iter=max_iter, random_state=random_state)
        model.fit(X, y)
        results[max_iter] = {
            'model': model,
            'n_iter': model.n_iter_
        }
        print(f"max_iter={max_iter}: converged in {model.n_iter_} iterations")
    
    return results
