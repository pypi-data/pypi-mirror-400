"""
Lab 5 - Convolutional Neural Networks (CNN) for FashionMNIST.
Contains CNN architectures and training/evaluation functions.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
import random


# ============================================================================
# CNN Model Architectures
# ============================================================================

def create_fashion_cnn():
    """
    Create a simple CNN for FashionMNIST classification.
    Returns nn.Sequential model - easy to understand and modify.
    
    Returns:
    --------
    nn.Sequential
        Simple CNN model for 28x28 images, 10 classes
    """
    model = nn.Sequential(
        nn.Conv2d(1, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        
        nn.Flatten(),
        nn.Linear(64 * 7 * 7, 128),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(128, 10)
    )
    return model


def create_deep_cnn():
    """
    Create a deeper CNN for FashionMNIST.
    Returns nn.Sequential model - simple and clear.
    
    Returns:
    --------
    nn.Sequential
        Deeper CNN model with 3 conv layers
    """
    model = nn.Sequential(
        nn.Conv2d(1, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        
        nn.Conv2d(32, 64, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        
        nn.Conv2d(64, 128, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        
        nn.Flatten(),
        nn.Linear(128 * 3 * 3, 256),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(256, 10)
    )
    return model


# ============================================================================
# Data Loading Functions
# ============================================================================

def load_fashion_mnist(batch_size=64, normalize=True):
    """
    Load FashionMNIST dataset with train/test splits.
    
    Parameters:
    -----------
    batch_size : int
        Batch size for data loaders (default: 64)
    normalize : bool
        Whether to normalize data to [-1, 1] (default: True)
    
    Returns:
    --------
    tuple
        (train_loader, test_loader, train_data, test_data)
    """
    if normalize:
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    else:
        transform = transforms.ToTensor()
    
    train_data = datasets.FashionMNIST(
        root='./data', train=True, download=True, transform=transform
    )
    test_data = datasets.FashionMNIST(
        root='./data', train=False, download=True, transform=transform
    )
    
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=1000, shuffle=False)
    
    return train_loader, test_loader, train_data, test_data


# ============================================================================
# Training Functions
# ============================================================================

def train_cnn(model, train_loader, test_loader, criterion, optimizer, epochs=10, device='cpu', lr_label="Training"):
    """
    Train CNN model on FashionMNIST.
    
    Parameters:
    -----------
    model : nn.Module
        CNN model to train
    train_loader : DataLoader
        Training data loader
    test_loader : DataLoader
        Test data loader
    criterion : nn.Module
        Loss criterion
    optimizer : torch.optim.Optimizer
        Optimizer for training
    epochs : int
        Number of training epochs (default: 10)
    device : str
        Device to train on ('cpu' or 'cuda', default: 'cpu')
    lr_label : str
        Label for printing progress (default: "Training")
    
    Returns:
    --------
    tuple
        (train_losses, test_accuracies) - lists of training metrics
    """
    train_losses = []
    test_accuracies = []
    train_accuracies = []
    
    model.to(device)
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()
        
        # Evaluate on test set
        model.eval()
        correct_test = 0
        total_test = 0
        
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total_test += labels.size(0)
                correct_test += (predicted == labels).sum().item()
        
        train_acc = 100 * correct_train / total_train
        test_acc = 100 * correct_test / total_test
        train_losses.append(running_loss / len(train_loader))
        train_accuracies.append(train_acc)
        test_accuracies.append(test_acc)
        
        print(f"[{lr_label}] Epoch {epoch+1}/{epochs} | Loss: {train_losses[-1]:.4f} | Test Acc: {test_acc:.2f}%")
    
    return train_losses, test_accuracies


# ============================================================================
# Evaluation Functions
# ============================================================================

def evaluate_cnn(model, test_loader, device='cpu'):
    """
    Evaluate CNN model on test set.
    
    Parameters:
    -----------
    model : nn.Module
        Trained CNN model
    test_loader : DataLoader
        Test data loader
    device : str
        Device to evaluate on (default: 'cpu')
    
    Returns:
    --------
    dict
        Dictionary with 'accuracy', 'predictions', 'targets' keys
    """
    model.eval()
    model.to(device)
    
    all_predictions = []
    all_targets = []
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            all_predictions.extend(predicted.cpu().numpy())
            all_targets.extend(labels.cpu().numpy())
    
    accuracy = 100 * correct / total
    
    return {
        'accuracy': accuracy,
        'predictions': all_predictions,
        'targets': all_targets
    }


def plot_confusion_matrix(y_true, y_pred, class_names):
    """
    Plot confusion matrix for CNN predictions.
    
    Parameters:
    -----------
    y_true : list or np.ndarray
        True labels
    y_pred : list or np.ndarray
        Predicted labels
    class_names : list
        List of class names
    """
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.show()
    
    # Print per-class accuracy
    class_acc = cm.diagonal() / cm.sum(axis=1)
    print("\nPer-Class Accuracy:")
    for i, acc in enumerate(class_acc):
        print(f"{class_names[i]:<15}: {acc*100:.2f}%")


# ============================================================================
# Visualization Functions
# ============================================================================

def plot_training_loss(losses_list, labels, title="Training Loss Comparison"):
    """
    Plot multiple training loss curves.
    
    Parameters:
    -----------
    losses_list : list of lists
        List of loss histories
    labels : list of str
        Labels for each loss curve
    title : str
        Plot title
    """
    plt.figure(figsize=(10, 6))
    
    for losses, label in zip(losses_list, labels):
        plt.plot(losses, label=label)
    
    plt.xlabel("Epochs")
    plt.ylabel("Training Loss")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()


def visualize_predictions(model, test_dataset, class_names, n_samples=5, device='cpu'):
    """
    Visualize model predictions on random test samples.
    
    Parameters:
    -----------
    model : nn.Module
        Trained model
    test_dataset : Dataset
        Test dataset
    class_names : list
        List of class names
    n_samples : int
        Number of samples to visualize (default: 5)
    device : str
        Device to run on (default: 'cpu')
    """
    model.eval()
    model.to(device)
    
    samples = random.sample(range(len(test_dataset)), n_samples)
    
    plt.figure(figsize=(12, 3))
    
    for idx, i in enumerate(samples):
        image, label = test_dataset[i]
        
        with torch.no_grad():
            output = model(image.unsqueeze(0).to(device))
            pred = output.argmax(1).item()
        
        plt.subplot(1, n_samples, idx + 1)
        plt.imshow(image.squeeze(), cmap='gray')
        plt.title(f"T: {class_names[label]}\nP: {class_names[pred]}")
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()


def save_model(model, filepath):
    """
    Save model state dict to file.
    
    Parameters:
    -----------
    model : nn.Module
        Model to save
    filepath : str
        Path to save model
    """
    torch.save(model.state_dict(), filepath)
    print(f"Model saved to {filepath}")


def load_model(model_creation_fn, filepath, device='cpu'):
    """
    Load model from file.
    
    Parameters:
    -----------
    model_creation_fn : function
        Function that creates model (e.g., create_fashion_cnn or create_deep_cnn)
    filepath : str
        Path to model file
    device : str
        Device to load model on (default: 'cpu')
    
    Returns:
    --------
    nn.Module
        Loaded model
    """
    model = model_creation_fn().to(device)
    model.load_state_dict(torch.load(filepath))
    model.eval()
    print(f"Model loaded from {filepath}")
    return model
