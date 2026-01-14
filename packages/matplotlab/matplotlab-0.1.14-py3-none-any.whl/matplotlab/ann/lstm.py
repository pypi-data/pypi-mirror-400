"""
Lab 10: Long Short-Term Memory (LSTM) Networks

This module provides functions for implementing LSTMs for:
- Next word prediction
- Text generation

Author: Matplotlab Team
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import string
import random
import matplotlib.pyplot as plt
import numpy as np


# ============================================================================
# Text Processing Utilities
# ============================================================================

def tokenize_lstm_text(text):
    """
    Tokenize text for LSTM processing.
    
    Parameters:
    -----------
    text : str
        Input text
    
    Returns:
    --------
    list
        List of lowercase tokens without punctuation
    
    Example:
    --------
    >>> tokens = tokenize_lstm_text("Hello, World!")
    >>> print(tokens)
    ['hello', 'world']
    """
    standardized_text = text.casefold()
    cleaned_text = ""
    
    for char in standardized_text:
        if char not in string.punctuation:
            cleaned_text += char
    
    token_array = cleaned_text.split()
    return token_array


def make_vocab(tokenized_text):
    """
    Create vocabulary from tokenized text.
    
    Parameters:
    -----------
    tokenized_text : list
        List of tokens
    
    Returns:
    --------
    dict
        Vocabulary mapping words to indices (includes <pad> and <unk>)
    
    Example:
    --------
    >>> tokens = tokenize_lstm_text(text)
    >>> vocab = make_vocab(tokens)
    >>> print(f"Vocab size: {len(vocab)}")
    """
    vocab = {"<pad>": 0, "<unk>": 1}
    unique_words = sorted(list(set(tokenized_text)))
    
    for word in unique_words:
        if word not in vocab:
            vocab[word] = len(vocab)
    
    return vocab


def create_sequences(tokens, vocab, sequence_length=5):
    """
    Create input sequences and targets for next-word prediction.
    
    Parameters:
    -----------
    tokens : list
        List of tokens
    vocab : dict
        Vocabulary mapping
    sequence_length : int
        Length of input sequences
    
    Returns:
    --------
    tuple
        (X_sequences, y_targets) as tensors
    
    Example:
    --------
    >>> X, y = create_sequences(tokens, vocab, sequence_length=5)
    >>> print(f"Input shape: {X.shape}, Target shape: {y.shape}")
    """
    input_sequences = []
    
    for i in range(len(tokens) - sequence_length):
        seq_words = tokens[i : i + sequence_length]
        seq_indices = [vocab[w] for w in seq_words]
        input_sequences.append(seq_indices)
    
    data_tensor = torch.tensor(input_sequences, dtype=torch.long)
    
    X = data_tensor[:, :-1]  # All but last
    y = data_tensor[:, -1]   # Last word is target
    
    return X, y


# ============================================================================
# Dataset Class
# ============================================================================

class NextWordDataset(Dataset):
    """
    Dataset for next-word prediction task.
    
    Parameters:
    -----------
    X : torch.Tensor
        Input sequences
    y : torch.Tensor
        Target words
    """
    def __init__(self, X, y):
        self.X = X
        self.y = y
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# ============================================================================
# LSTM Model Architectures
# ============================================================================

class NextWordLSTM(nn.Module):
    """
    LSTM for next-word prediction.
    
    Parameters:
    -----------
    vocab_size : int
        Size of vocabulary
    embed_dim : int
        Dimension of word embeddings
    hidden_dim : int
        Dimension of LSTM hidden state
    """
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=100):
        super(NextWordLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, x):
        embeds = self.embedding(x)
        lstm_out, _ = self.lstm(embeds)
        last_time_step = lstm_out[:, -1, :]
        out = self.fc(last_time_step)
        return out


class TextGenerationLSTM(nn.Module):
    """
    LSTM for text generation with multiple layers.
    
    Parameters:
    -----------
    vocab_size : int
        Size of vocabulary
    embed_dim : int
        Dimension of word embeddings
    hidden_dim : int
        Dimension of LSTM hidden state
    num_layers : int
        Number of LSTM layers
    dropout : float
        Dropout probability
    """
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256, num_layers=2, dropout=0.3):
        super(TextGenerationLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
    
    def forward(self, x, hidden=None):
        embeds = self.embedding(x)
        lstm_out, hidden = self.lstm(embeds, hidden)
        lstm_out = self.dropout(lstm_out)
        last_time_step = lstm_out[:, -1, :]
        out = self.fc(last_time_step)
        return out, hidden
    
    def init_hidden(self, batch_size, device):
        """Initialize hidden state."""
        return (torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device),
                torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device))


# ============================================================================
# Training Functions
# ============================================================================

def train_next_word_lstm(train_loader, val_loader, vocab_size, epochs=50, lr=0.001,
                         embed_dim=64, hidden_dim=100):
    """
    Train LSTM for next-word prediction.
    
    Parameters:
    -----------
    train_loader : DataLoader
        Training data loader
    val_loader : DataLoader
        Validation data loader
    vocab_size : int
        Size of vocabulary
    epochs : int
        Number of training epochs
    lr : float
        Learning rate
    embed_dim : int
        Embedding dimension
    hidden_dim : int
        Hidden dimension
    
    Returns:
    --------
    tuple
        (model, train_losses, val_losses, train_accs, val_accs)
    
    Example:
    --------
    >>> model, train_loss, val_loss, train_acc, val_acc = train_next_word_lstm(
    ...     train_loader, val_loader, vocab_size=500
    ... )
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = NextWordLSTM(vocab_size, embed_dim, hidden_dim).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    
    print(f"Training Next-Word LSTM on {device}...")
    print(f"Vocab size: {vocab_size}, Epochs: {epochs}\n")
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_correct += (predicted == y_batch).sum().item()
            train_total += y_batch.size(0)
        
        avg_train_loss = train_loss / len(train_loader)
        train_accuracy = 100 * train_correct / train_total
        train_losses.append(avg_train_loss)
        train_accs.append(train_accuracy)
        
        # Validation phase
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                val_correct += (predicted == y_batch).sum().item()
                val_total += y_batch.size(0)
        
        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = 100 * val_correct / val_total
        val_losses.append(avg_val_loss)
        val_accs.append(val_accuracy)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}]")
            print(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {train_accuracy:.2f}%")
            print(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {val_accuracy:.2f}%\n")
    
    return model, train_losses, val_losses, train_accs, val_accs


def train_text_generation_lstm(train_loader, val_loader, vocab_size, epochs=100, lr=0.001,
                                embed_dim=128, hidden_dim=256, num_layers=2):
    """
    Train LSTM for text generation.
    
    Parameters:
    -----------
    train_loader : DataLoader
        Training data loader
    val_loader : DataLoader
        Validation data loader
    vocab_size : int
        Size of vocabulary
    epochs : int
        Number of training epochs
    lr : float
        Learning rate
    embed_dim : int
        Embedding dimension
    hidden_dim : int
        Hidden dimension
    num_layers : int
        Number of LSTM layers
    
    Returns:
    --------
    tuple
        (model, train_losses, val_losses)
    
    Example:
    --------
    >>> model, train_loss, val_loss = train_text_generation_lstm(
    ...     train_loader, val_loader, vocab_size=500, num_layers=2
    ... )
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TextGenerationLSTM(vocab_size, embed_dim, hidden_dim, num_layers).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    train_losses = []
    val_losses = []
    
    print(f"Training Text Generation LSTM on {device}...")
    print(f"Vocab size: {vocab_size}, Layers: {num_layers}, Epochs: {epochs}\n")
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0
        
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            outputs, _ = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)
        train_losses.append(avg_train_loss)
        
        # Validation
        model.eval()
        val_loss = 0
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs, _ = model(X_batch)
                loss = criterion(outputs, y_batch)
                val_loss += loss.item()
        
        avg_val_loss = val_loss / len(val_loader)
        val_losses.append(avg_val_loss)
        
        if (epoch + 1) % 20 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
    
    return model, train_losses, val_losses


# ============================================================================
# Prediction and Generation Functions
# ============================================================================

def predict_next_word(model, seed_text, vocab, sequence_length=4):
    """
    Predict next word given seed text.
    
    Parameters:
    -----------
    model : nn.Module
        Trained LSTM model
    seed_text : str
        Input text (last N words will be used)
    vocab : dict
        Vocabulary mapping
    sequence_length : int
        Number of words to use from seed_text
    
    Returns:
    --------
    str
        Predicted next word
    
    Example:
    --------
    >>> next_word = predict_next_word(model, "the data science mentorship", vocab)
    >>> print(f"Next word: {next_word}")
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    tokens = tokenize_lstm_text(seed_text)
    tokens = tokens[-sequence_length:]  # Take last N words
    
    # Convert to indices
    indices = [vocab.get(w, vocab['<unk>']) for w in tokens]
    
    # Pad if needed
    while len(indices) < sequence_length:
        indices.insert(0, vocab['<pad>'])
    
    input_tensor = torch.tensor([indices], dtype=torch.long).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)
        _, predicted_idx = torch.max(output, 1)
    
    # Convert index back to word
    idx_to_word = {v: k for k, v in vocab.items()}
    predicted_word = idx_to_word.get(predicted_idx.item(), '<unk>')
    
    return predicted_word


def generate_text(model, seed_text, vocab, num_words=50, sequence_length=4, temperature=1.0):
    """
    Generate text using trained LSTM.
    
    Parameters:
    -----------
    model : nn.Module
        Trained LSTM model
    seed_text : str
        Starting text
    vocab : dict
        Vocabulary mapping
    num_words : int
        Number of words to generate
    sequence_length : int
        Sequence length for input
    temperature : float
        Sampling temperature (higher = more random)
    
    Returns:
    --------
    str
        Generated text
    
    Example:
    --------
    >>> text = generate_text(model, "the data science", vocab, num_words=30)
    >>> print(text)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    idx_to_word = {v: k for k, v in vocab.items()}
    generated_words = tokenize_lstm_text(seed_text)
    
    for _ in range(num_words):
        # Get last sequence_length words
        current_sequence = generated_words[-sequence_length:]
        
        # Convert to indices
        indices = [vocab.get(w, vocab['<unk>']) for w in current_sequence]
        
        # Pad if needed
        while len(indices) < sequence_length:
            indices.insert(0, vocab['<pad>'])
        
        input_tensor = torch.tensor([indices], dtype=torch.long).to(device)
        
        with torch.no_grad():
            if isinstance(model, TextGenerationLSTM):
                output, _ = model(input_tensor)
            else:
                output = model(input_tensor)
            
            # Apply temperature
            output = output / temperature
            probs = torch.softmax(output, dim=1)
            
            # Sample from distribution
            predicted_idx = torch.multinomial(probs, 1).item()
        
        predicted_word = idx_to_word.get(predicted_idx, '<unk>')
        
        # Skip special tokens
        if predicted_word not in ['<pad>', '<unk>']:
            generated_words.append(predicted_word)
    
    return ' '.join(generated_words)


# ============================================================================
# Visualization Functions
# ============================================================================

def plot_lstm_training_curves(train_losses, val_losses, train_accs=None, val_accs=None):
    """
    Plot LSTM training curves.
    
    Parameters:
    -----------
    train_losses : list
        Training losses
    val_losses : list
        Validation losses
    train_accs : list, optional
        Training accuracies
    val_accs : list, optional
        Validation accuracies
    
    Example:
    --------
    >>> plot_lstm_training_curves(train_loss, val_loss, train_acc, val_acc)
    """
    if train_accs is not None and val_accs is not None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Loss plot
        ax1.plot(train_losses, label='Train Loss', marker='o', markersize=3)
        ax1.plot(val_losses, label='Val Loss', marker='s', markersize=3)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Accuracy plot
        ax2.plot(train_accs, label='Train Accuracy', marker='o', markersize=3)
        ax2.plot(val_accs, label='Val Accuracy', marker='s', markersize=3)
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.set_title('Training and Validation Accuracy')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    else:
        # Only loss plot
        plt.figure(figsize=(10, 5))
        plt.plot(train_losses, label='Train Loss', marker='o', markersize=3)
        plt.plot(val_losses, label='Val Loss', marker='s', markersize=3)
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('LSTM Training and Validation Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plot_text_generation_loss(train_losses, val_losses):
    """
    Plot text generation LSTM loss curves.
    
    Parameters:
    -----------
    train_losses : list
        Training losses
    val_losses : list
        Validation losses
    
    Example:
    --------
    >>> plot_text_generation_loss(train_loss, val_loss)
    """
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss', linewidth=2, alpha=0.8)
    plt.plot(val_losses, label='Validation Loss', linewidth=2, alpha=0.8)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Cross-Entropy Loss', fontsize=12)
    plt.title('Text Generation LSTM - Training Progress', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def compare_predictions(model, test_samples, vocab, sequence_length=4):
    """
    Compare model predictions on multiple test samples.
    
    Parameters:
    -----------
    model : nn.Module
        Trained model
    test_samples : list
        List of test sentences
    vocab : dict
        Vocabulary mapping
    sequence_length : int
        Sequence length
    
    Example:
    --------
    >>> samples = ["the data science", "students are required", "all monthly payments"]
    >>> compare_predictions(model, samples, vocab)
    """
    print("=" * 70)
    print("NEXT WORD PREDICTIONS")
    print("=" * 70)
    
    for sample in test_samples:
        predicted = predict_next_word(model, sample, vocab, sequence_length)
        print(f"Input: '{sample}'")
        print(f"Predicted next word: '{predicted}'")
        print("-" * 70)
