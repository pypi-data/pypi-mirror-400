"""
Lab 9: Recurrent Neural Networks (RNN)

This module provides functions for implementing RNNs for:
- Question-Answer tasks with custom dataset
- Sentiment analysis on IMDB movie reviews

Author: Matplotlab Team
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset, random_split
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix


# ============================================================================
# Text Processing Utilities
# ============================================================================

def tokenize_text(text):
    """
    Tokenize text by converting to lowercase and removing punctuation.
    
    Parameters:
    -----------
    text : str
        Input text to tokenize
    
    Returns:
    --------
    list
        List of tokens
    
    Example:
    --------
    >>> tokens = tokenize_text("What's the capital of Brazil?")
    >>> print(tokens)
    ['whats', 'the', 'capital', 'of', 'brazil']
    """
    text = text.lower().replace('?', '').replace("'", "").replace('.', '').replace(',', '')
    return text.split()


def build_vocab_from_dataframe(df):
    """
    Build vocabulary from question-answer dataframe.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with 'question' and 'answer' columns
    
    Returns:
    --------
    dict
        Vocabulary mapping words to indices
    
    Example:
    --------
    >>> vocab = build_vocab_from_dataframe(df)
    >>> print(f"Vocab size: {len(vocab)}")
    """
    vocab = {'<UNK>': 0}
    
    def add_to_vocab(row):
        tokenized_question = tokenize_text(row['question'])
        tokenized_answer = tokenize_text(row['answer'])
        merged_tokens = tokenized_question + tokenized_answer
        for token in merged_tokens:
            if token not in vocab:
                vocab[token] = len(vocab)
    
    df.apply(add_to_vocab, axis=1)
    return vocab


def text_to_indices(text, vocab):
    """
    Convert text to list of vocabulary indices.
    
    Parameters:
    -----------
    text : str
        Input text
    vocab : dict
        Vocabulary mapping
    
    Returns:
    --------
    list
        List of indices
    
    Example:
    --------
    >>> indices = text_to_indices("what is AI?", vocab)
    """
    indexed_text = []
    for token in tokenize_text(text):
        if token in vocab:
            indexed_text.append(vocab[token])
        else:
            indexed_text.append(vocab['<UNK>'])
    return indexed_text


# ============================================================================
# Dataset Classes
# ============================================================================

class QADataset(Dataset):
    """
    Question-Answer Dataset for RNN training.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with 'question' and 'answer' columns
    vocab : dict
        Vocabulary mapping
    """
    def __init__(self, df, vocab):
        self.df = df
        self.vocab = vocab
    
    def __len__(self):
        return self.df.shape[0]
    
    def __getitem__(self, index):
        question = self.df.iloc[index]['question']
        answer = self.df.iloc[index]['answer']
        
        numerical_question = text_to_indices(question, self.vocab)
        numerical_answer = text_to_indices(answer, self.vocab)
        
        return torch.tensor(numerical_question), torch.tensor(numerical_answer)


# ============================================================================
# RNN Model Architectures
# ============================================================================

class SimpleRNN(nn.Module):
    """
    Simple RNN for Question-Answer task.
    
    Parameters:
    -----------
    vocab_size : int
        Size of vocabulary
    embedding_dim : int
        Dimension of word embeddings
    hidden_dim : int
        Dimension of RNN hidden state
    """
    def __init__(self, vocab_size, embedding_dim=50, hidden_dim=64):
        super(SimpleRNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.rnn = nn.RNN(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, question):
        embedded_question = self.embedding(question)
        output, hidden = self.rnn(embedded_question)
        final_encoding = output[:, -1, :]  # Take last time step
        final_output = self.fc(final_encoding)
        return final_output


class SentimentRNN(nn.Module):
    """
    RNN for sentiment analysis (binary classification).
    
    Parameters:
    -----------
    vocab_size : int
        Size of vocabulary
    embedding_dim : int
        Dimension of word embeddings
    hidden_dim : int
        Dimension of RNN hidden state
    """
    def __init__(self, vocab_size, embedding_dim=32, hidden_dim=64):
        super(SentimentRNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.rnn = nn.RNN(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        embeds = self.embedding(x)
        rnn_out, hidden = self.rnn(embeds)
        last_step_output = rnn_out[:, -1, :]
        out = self.fc(last_step_output)
        return self.sigmoid(out)


# ============================================================================
# Training Functions
# ============================================================================

def train_qa_rnn(dataloader, vocab, epochs=50, lr=0.01, embedding_dim=50, hidden_dim=64):
    """
    Train RNN on Question-Answer dataset.
    
    Parameters:
    -----------
    dataloader : DataLoader
        Training data loader
    vocab : dict
        Vocabulary mapping
    epochs : int
        Number of training epochs
    lr : float
        Learning rate
    embedding_dim : int
        Embedding dimension
    hidden_dim : int
        Hidden dimension
    
    Returns:
    --------
    tuple
        (model, losses) trained model and loss history
    
    Example:
    --------
    >>> model, losses = train_qa_rnn(dataloader, vocab, epochs=50)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleRNN(len(vocab), embedding_dim, hidden_dim).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    losses = []
    model.train()
    
    print(f"Training QA RNN on {device}...")
    print(f"Vocabulary size: {len(vocab)}")
    print(f"Epochs: {epochs}\n")
    
    for epoch in range(epochs):
        total_loss = 0
        for question, answer in dataloader:
            question = question.to(device)
            answer = answer.to(device)
            
            optimizer.zero_grad()
            output = model(question)
            
            # Answer is first word only for simplicity
            loss = criterion(output, answer[:, 0] if len(answer.shape) > 1 else answer)
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        losses.append(total_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")
    
    return model, losses


def train_sentiment_rnn(train_loader, val_loader, vocab_size, epochs=10, lr=0.001, 
                        embedding_dim=32, hidden_dim=64):
    """
    Train RNN for sentiment analysis on IMDB dataset.
    
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
    embedding_dim : int
        Embedding dimension
    hidden_dim : int
        Hidden dimension
    
    Returns:
    --------
    tuple
        (model, train_losses, val_losses, train_accuracies, val_accuracies)
    
    Example:
    --------
    >>> model, train_loss, val_loss, train_acc, val_acc = train_sentiment_rnn(
    ...     train_loader, val_loader, vocab_size=10000
    ... )
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SentimentRNN(vocab_size, embedding_dim, hidden_dim).to(device)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []
    
    print(f"Training Sentiment RNN on {device}...")
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
            predicted = (outputs > 0.5).float()
            train_correct += (predicted == y_batch).sum().item()
            train_total += y_batch.size(0)
        
        avg_train_loss = train_loss / len(train_loader)
        train_accuracy = 100 * train_correct / train_total
        train_losses.append(avg_train_loss)
        train_accuracies.append(train_accuracy)
        
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
                predicted = (outputs > 0.5).float()
                val_correct += (predicted == y_batch).sum().item()
                val_total += y_batch.size(0)
        
        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = 100 * val_correct / val_total
        val_losses.append(avg_val_loss)
        val_accuracies.append(val_accuracy)
        
        print(f"Epoch [{epoch+1}/{epochs}]")
        print(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {train_accuracy:.2f}%")
        print(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {val_accuracy:.2f}%\n")
    
    return model, train_losses, val_losses, train_accuracies, val_accuracies


# ============================================================================
# Prediction and Evaluation Functions
# ============================================================================

def predict_qa_answer(model, question, vocab, threshold=0.5):
    """
    Predict answer for a question using trained QA RNN.
    
    Parameters:
    -----------
    model : nn.Module
        Trained QA RNN model
    question : str
        Input question
    vocab : dict
        Vocabulary mapping
    threshold : float
        Confidence threshold
    
    Returns:
    --------
    str
        Predicted answer word
    
    Example:
    --------
    >>> answer = predict_qa_answer(model, "what's the capital of Brazil?", vocab)
    >>> print(f"Predicted: {answer}")
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    numerical_question = text_to_indices(question, vocab)
    question_tensor = torch.tensor(numerical_question).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(question_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)
        value, index = torch.max(probs, dim=1)
    
    predicted_index = index.item()
    idx_to_word = {v: k for k, v in vocab.items()}
    predicted_word = idx_to_word.get(predicted_index, '<UNK>')
    
    return predicted_word


def evaluate_sentiment_model(model, test_loader):
    """
    Evaluate sentiment RNN model on test set.
    
    Parameters:
    -----------
    model : nn.Module
        Trained sentiment model
    test_loader : DataLoader
        Test data loader
    
    Returns:
    --------
    tuple
        (accuracy, predictions, true_labels)
    
    Example:
    --------
    >>> accuracy, preds, labels = evaluate_sentiment_model(model, test_loader)
    >>> print(f"Test Accuracy: {accuracy:.2f}%")
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    all_predictions = []
    all_labels = []
    correct = 0
    total = 0
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            outputs = model(X_batch)
            predicted = (outputs > 0.5).float()
            
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(y_batch.cpu().numpy())
            
            correct += (predicted == y_batch).sum().item()
            total += y_batch.size(0)
    
    accuracy = 100 * correct / total
    return accuracy, np.array(all_predictions), np.array(all_labels)


# ============================================================================
# Visualization Functions
# ============================================================================

def plot_rnn_training_loss(losses, title="RNN Training Loss"):
    """
    Plot RNN training loss curve.
    
    Parameters:
    -----------
    losses : list
        List of loss values
    title : str
        Plot title
    
    Example:
    --------
    >>> plot_rnn_training_loss(losses)
    """
    plt.figure(figsize=(10, 5))
    plt.plot(losses, label='Training Loss', color='blue', alpha=0.7)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_sentiment_training_curves(train_losses, val_losses, train_accs, val_accs):
    """
    Plot training and validation loss/accuracy curves.
    
    Parameters:
    -----------
    train_losses : list
        Training losses
    val_losses : list
        Validation losses
    train_accs : list
        Training accuracies
    val_accs : list
        Validation accuracies
    
    Example:
    --------
    >>> plot_sentiment_training_curves(train_loss, val_loss, train_acc, val_acc)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Loss plot
    ax1.plot(train_losses, label='Train Loss', marker='o', markersize=4)
    ax1.plot(val_losses, label='Val Loss', marker='s', markersize=4)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training and Validation Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy plot
    ax2.plot(train_accs, label='Train Accuracy', marker='o', markersize=4)
    ax2.plot(val_accs, label='Val Accuracy', marker='s', markersize=4)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training and Validation Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plot_confusion_matrix_sentiment(predictions, true_labels):
    """
    Plot confusion matrix for sentiment classification.
    
    Parameters:
    -----------
    predictions : array
        Predicted labels
    true_labels : array
        True labels
    
    Example:
    --------
    >>> plot_confusion_matrix_sentiment(preds, labels)
    """
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    
    cm = confusion_matrix(true_labels, predictions)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Negative', 'Positive'],
                yticklabels=['Negative', 'Positive'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix - Sentiment Analysis')
    plt.tight_layout()
    plt.show()
