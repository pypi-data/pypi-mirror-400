"""
Lab 8: Autoencoders (Undercomplete, Denoising, Convolutional)

This module provides functions for implementing different types of autoencoders:
- Undercomplete Autoencoder
- Denoising Autoencoder
- Convolutional Autoencoder

Author: Matplotlab Team
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np


# ============================================================================
# Autoencoder Architectures
# ============================================================================

class UndercompleteAutoencoder(nn.Module):
    """
    Simple Undercomplete Autoencoder for MNIST.
    
    Compresses 784-dimensional input to 64-dimensional latent space.
    """
    def __init__(self, input_dim=784, hidden_dim=128, latent_dim=64):
        super(UndercompleteAutoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """Forward pass through encoder and decoder."""
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


class DenoisingAutoencoder(nn.Module):
    """
    Denoising Autoencoder for MNIST.
    
    Learns to reconstruct clean images from noisy inputs.
    """
    def __init__(self, input_dim=784, hidden_dim=128, latent_dim=64):
        super(DenoisingAutoencoder, self).__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU()
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


class ConvolutionalAutoencoder(nn.Module):
    """
    Convolutional Autoencoder for FashionMNIST.
    
    Uses convolutional layers for better spatial feature learning.
    """
    def __init__(self):
        super(ConvolutionalAutoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1),  # 28x28 -> 14x14
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),  # 14x14 -> 7x7
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),  # 7x7 -> 4x4
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),  # 4x4 -> 7x7
            nn.ReLU(),
            nn.ConvTranspose2d(32, 16, kernel_size=3, stride=2, padding=1, output_padding=1),  # 7x7 -> 14x14
            nn.ReLU(),
            nn.ConvTranspose2d(16, 1, kernel_size=3, stride=2, padding=1, output_padding=1),  # 14x14 -> 28x28
            nn.Sigmoid()
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


# ============================================================================
# Dataset Loading Functions
# ============================================================================

def load_mnist_for_autoencoder(batch_size=64):
    """
    Load MNIST dataset for autoencoder training.
    
    Parameters:
    -----------
    batch_size : int
        Batch size for data loaders
    
    Returns:
    --------
    tuple
        (train_loader, test_loader)
    
    Example:
    --------
    >>> train_loader, test_loader = load_mnist_for_autoencoder()
    """
    transform = transforms.Compose([
        transforms.ToTensor()
    ])
    
    train_dataset = datasets.MNIST(
        root='./data',
        train=True,
        download=True,
        transform=transform
    )
    
    test_dataset = datasets.MNIST(
        root='./data',
        train=False,
        download=True,
        transform=transform
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, test_loader


def load_fashion_mnist_for_autoencoder(batch_size=64):
    """
    Load FashionMNIST dataset for convolutional autoencoder.
    
    Parameters:
    -----------
    batch_size : int
        Batch size for data loaders
    
    Returns:
    --------
    tuple
        (train_loader, test_loader)
    
    Example:
    --------
    >>> train_loader, test_loader = load_fashion_mnist_for_autoencoder()
    """
    transform = transforms.Compose([
        transforms.ToTensor()
    ])
    
    train_dataset = datasets.FashionMNIST(
        root='./data',
        train=True,
        download=True,
        transform=transform
    )
    
    test_dataset = datasets.FashionMNIST(
        root='./data',
        train=False,
        download=True,
        transform=transform
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, test_loader


# ============================================================================
# Training Functions
# ============================================================================

def train_undercomplete_autoencoder(train_loader, epochs=20, lr=1e-3):
    """
    Train an undercomplete autoencoder on MNIST.
    
    Parameters:
    -----------
    train_loader : DataLoader
        Training data loader
    epochs : int
        Number of training epochs
    lr : float
        Learning rate
    
    Returns:
    --------
    tuple
        (model, losses) where losses is a list of loss values per iteration
    
    Example:
    --------
    >>> train_loader, _ = load_mnist_for_autoencoder()
    >>> model, losses = train_undercomplete_autoencoder(train_loader)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UndercompleteAutoencoder().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-8)
    
    losses = []
    model.train()
    
    print(f"Training Undercomplete Autoencoder on {device}...")
    for epoch in range(epochs):
        epoch_loss = 0
        for images, _ in train_loader:
            images = images.view(-1, 28 * 28).to(device)
            
            optimizer.zero_grad()
            reconstructed = model(images)
            loss = criterion(reconstructed, images)
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
            epoch_loss += loss.item()
        
        if (epoch + 1) % 5 == 0:
            avg_loss = epoch_loss / len(train_loader)
            print(f"Epoch [{epoch+1}/{epochs}], Average Loss: {avg_loss:.6f}")
    
    return model, losses


def train_denoising_autoencoder(train_loader, epochs=20, lr=1e-3, noise_factor=0.5):
    """
    Train a denoising autoencoder on MNIST with added noise.
    
    Parameters:
    -----------
    train_loader : DataLoader
        Training data loader
    epochs : int
        Number of training epochs
    lr : float
        Learning rate
    noise_factor : float
        Amount of noise to add (0.0 to 1.0)
    
    Returns:
    --------
    tuple
        (model, losses) where losses is a list of loss values per iteration
    
    Example:
    --------
    >>> train_loader, _ = load_mnist_for_autoencoder()
    >>> model, losses = train_denoising_autoencoder(train_loader, noise_factor=0.5)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DenoisingAutoencoder().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-8)
    
    losses = []
    model.train()
    
    print(f"Training Denoising Autoencoder on {device}...")
    print(f"Noise factor: {noise_factor}")
    
    for epoch in range(epochs):
        epoch_loss = 0
        for images, _ in train_loader:
            images = images.view(-1, 28 * 28).to(device)
            
            # Add noise
            noisy_images = images + noise_factor * torch.randn_like(images)
            noisy_images = torch.clamp(noisy_images, 0., 1.)
            
            optimizer.zero_grad()
            reconstructed = model(noisy_images)
            loss = criterion(reconstructed, images)  # Reconstruct original clean images
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
            epoch_loss += loss.item()
        
        if (epoch + 1) % 5 == 0:
            avg_loss = epoch_loss / len(train_loader)
            print(f"Epoch [{epoch+1}/{epochs}], Average Loss: {avg_loss:.6f}")
    
    return model, losses


def train_convolutional_autoencoder(train_loader, epochs=20, lr=1e-3):
    """
    Train a convolutional autoencoder on FashionMNIST.
    
    Parameters:
    -----------
    train_loader : DataLoader
        Training data loader
    epochs : int
        Number of training epochs
    lr : float
        Learning rate
    
    Returns:
    --------
    tuple
        (model, losses) where losses is a list of loss values per iteration
    
    Example:
    --------
    >>> train_loader, _ = load_fashion_mnist_for_autoencoder()
    >>> model, losses = train_convolutional_autoencoder(train_loader)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ConvolutionalAutoencoder().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-8)
    
    losses = []
    model.train()
    
    print(f"Training Convolutional Autoencoder on {device}...")
    for epoch in range(epochs):
        epoch_loss = 0
        for images, _ in train_loader:
            images = images.to(device)
            
            optimizer.zero_grad()
            reconstructed = model(images)
            loss = criterion(reconstructed, images)
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
            epoch_loss += loss.item()
        
        if (epoch + 1) % 5 == 0:
            avg_loss = epoch_loss / len(train_loader)
            print(f"Epoch [{epoch+1}/{epochs}], Average Loss: {avg_loss:.6f}")
    
    return model, losses


# ============================================================================
# Visualization Functions
# ============================================================================

def plot_autoencoder_loss(losses, title="Autoencoder Training Loss"):
    """
    Plot training loss curve.
    
    Parameters:
    -----------
    losses : list
        List of loss values
    title : str
        Plot title
    
    Example:
    --------
    >>> plot_autoencoder_loss(losses, "Undercomplete Autoencoder Loss")
    """
    plt.figure(figsize=(10, 5))
    plt.plot(losses, label='Training Loss', alpha=0.7)
    plt.xlabel('Iterations')
    plt.ylabel('Loss (MSE)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def visualize_reconstructions(model, test_loader, num_images=10, is_conv=False):
    """
    Visualize original and reconstructed images.
    
    Parameters:
    -----------
    model : nn.Module
        Trained autoencoder model
    test_loader : DataLoader
        Test data loader
    num_images : int
        Number of images to display
    is_conv : bool
        Whether the model is convolutional (True) or fully connected (False)
    
    Example:
    --------
    >>> visualize_reconstructions(model, test_loader, num_images=10)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    dataiter = iter(test_loader)
    images, _ = next(dataiter)
    
    with torch.no_grad():
        if is_conv:
            images = images.to(device)
            reconstructed = model(images)
        else:
            images_flat = images.view(-1, 28 * 28).to(device)
            reconstructed = model(images_flat)
            images = images_flat
    
    fig, axes = plt.subplots(nrows=2, ncols=num_images, figsize=(num_images, 3))
    
    for i in range(num_images):
        # Original images
        if is_conv:
            img = images[i].cpu().squeeze().numpy()
        else:
            img = images[i].cpu().numpy().reshape(28, 28)
        axes[0, i].imshow(img, cmap='gray')
        axes[0, i].axis('off')
        if i == 0:
            axes[0, i].set_title('Original', fontsize=10)
        
        # Reconstructed images
        if is_conv:
            rec_img = reconstructed[i].cpu().squeeze().numpy()
        else:
            rec_img = reconstructed[i].cpu().numpy().reshape(28, 28)
        axes[1, i].imshow(rec_img, cmap='gray')
        axes[1, i].axis('off')
        if i == 0:
            axes[1, i].set_title('Reconstructed', fontsize=10)
    
    plt.tight_layout()
    plt.show()


def visualize_denoising(model, test_loader, noise_factor=0.5, num_images=10):
    """
    Visualize denoising process: original, noisy, reconstructed.
    
    Parameters:
    -----------
    model : nn.Module
        Trained denoising autoencoder
    test_loader : DataLoader
        Test data loader
    noise_factor : float
        Noise level for visualization
    num_images : int
        Number of images to display
    
    Example:
    --------
    >>> visualize_denoising(model, test_loader, noise_factor=0.5)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    dataiter = iter(test_loader)
    images, _ = next(dataiter)
    images = images.view(-1, 28 * 28).to(device)
    
    # Add noise
    noisy_images = images + noise_factor * torch.randn_like(images)
    noisy_images = torch.clamp(noisy_images, 0., 1.)
    
    with torch.no_grad():
        reconstructed = model(noisy_images)
    
    fig, axes = plt.subplots(nrows=3, ncols=num_images, figsize=(num_images, 4))
    
    for i in range(num_images):
        # Original
        axes[0, i].imshow(images[i].cpu().numpy().reshape(28, 28), cmap='gray')
        axes[0, i].axis('off')
        if i == 0:
            axes[0, i].set_title('Original', fontsize=10)
        
        # Noisy
        axes[1, i].imshow(noisy_images[i].cpu().numpy().reshape(28, 28), cmap='gray')
        axes[1, i].axis('off')
        if i == 0:
            axes[1, i].set_title('Noisy', fontsize=10)
        
        # Reconstructed
        axes[2, i].imshow(reconstructed[i].cpu().numpy().reshape(28, 28), cmap='gray')
        axes[2, i].axis('off')
        if i == 0:
            axes[2, i].set_title('Denoised', fontsize=10)
    
    plt.tight_layout()
    plt.show()


def compare_all_autoencoders(undercomplete_losses, denoising_losses, conv_losses):
    """
    Compare loss curves of all three autoencoder types.
    
    Parameters:
    -----------
    undercomplete_losses : list
        Losses from undercomplete autoencoder
    denoising_losses : list
        Losses from denoising autoencoder
    conv_losses : list
        Losses from convolutional autoencoder
    
    Example:
    --------
    >>> compare_all_autoencoders(losses1, losses2, losses3)
    """
    plt.figure(figsize=(12, 5))
    
    plt.plot(undercomplete_losses, label='Undercomplete AE', alpha=0.7)
    plt.plot(denoising_losses, label='Denoising AE', alpha=0.7)
    plt.plot(conv_losses, label='Convolutional AE', alpha=0.7)
    
    plt.xlabel('Iterations')
    plt.ylabel('Loss (MSE)')
    plt.title('Comparison of Autoencoder Training Losses')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
