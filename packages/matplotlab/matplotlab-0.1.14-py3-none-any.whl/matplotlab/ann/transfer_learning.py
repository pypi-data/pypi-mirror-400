"""Lab 7: Transfer Learning - Fine-tune pretrained models on Fashion-MNIST"""

import numpy as np
from ._code_inspector import ShowableFunction

# Lazy imports to avoid slow module loading
def _lazy_import_torch():
    """Import PyTorch only when needed"""
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms, models
    return torch, nn, optim, DataLoader, datasets, transforms, models


@ShowableFunction
def load_pretrained_model(model_name='resnet18', num_classes=10, freeze_backbone=True):
    """
    Load a pretrained model and adapt it for Fashion-MNIST.
    
    Loads a pretrained CNN model (ResNet18, VGG16, or AlexNet) with ImageNet weights,
    replaces the final classification layer to match the target number of classes,
    and optionally freezes the backbone layers for transfer learning.
    
    Parameters:
    -----------
    model_name : str, optional (default='resnet18')
        Name of the pretrained model. Options: 'resnet18', 'vgg16', 'alexnet'
    num_classes : int, optional (default=10)
        Number of output classes (10 for Fashion-MNIST)
    freeze_backbone : bool, optional (default=True)
        If True, freeze all layers except the final classification layer.
        This is recommended for transfer learning with small datasets.
    
    Returns:
    --------
    model : torch.nn.Module
        Pretrained model adapted for the target task
    
    Example:
    --------
    >>> model = load_pretrained_model('resnet18', num_classes=10, freeze_backbone=True)
    >>> print(f"Model loaded: {model.__class__.__name__}")
    
    Lab Context:
    ------------
    This implements the core transfer learning setup from Lab 7, where we use
    pretrained models (ResNet18, VGG16, AlexNet) trained on ImageNet and adapt
    them for Fashion-MNIST classification. Freezing the backbone layers allows
    us to train only the final layer, which is much faster and works well when
    the target dataset is small.
    """
    # Lazy import PyTorch (only when function is called)
    torch, nn, optim, DataLoader, datasets, transforms, models = _lazy_import_torch()
    
    # Load pretrained model
    if model_name.lower() == 'resnet18':
        model = models.resnet18(pretrained=True)
        # Replace final layer
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, num_classes)
        
        # Freeze backbone if requested
        if freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
            # Unfreeze final layer
            for param in model.fc.parameters():
                param.requires_grad = True
                
    elif model_name.lower() == 'vgg16':
        model = models.vgg16(pretrained=True)
        # Replace final layer
        num_features = model.classifier[6].in_features
        model.classifier[6] = nn.Linear(num_features, num_classes)
        
        # Freeze backbone if requested
        if freeze_backbone:
            for param in model.features.parameters():
                param.requires_grad = False
            # Classifier layers remain trainable
                
    elif model_name.lower() == 'alexnet':
        model = models.alexnet(pretrained=True)
        # Replace final layer
        num_features = model.classifier[6].in_features
        model.classifier[6] = nn.Linear(num_features, num_classes)
        
        # Freeze backbone if requested
        if freeze_backbone:
            for param in model.features.parameters():
                param.requires_grad = False
            # Classifier layers remain trainable
                
    else:
        raise ValueError(f"Invalid model_name. Choose from: 'resnet18', 'vgg16', 'alexnet'")
    
    return model


@ShowableFunction
def train_transfer_model(model, train_loader, val_loader, epochs=10, lr=0.001, device='cuda'):
    """
    Train/fine-tune a transfer learning model.
    
    Trains the model using the provided data loaders, tracks training and validation
    loss and accuracy for each epoch, and returns the trained model along with
    the training history.
    
    Parameters:
    -----------
    model : torch.nn.Module
        The model to train (typically from load_pretrained_model)
    train_loader : torch.utils.data.DataLoader
        DataLoader for training data
    val_loader : torch.utils.data.DataLoader
        DataLoader for validation data
    epochs : int, optional (default=10)
        Number of training epochs
    lr : float, optional (default=0.001)
        Learning rate for Adam optimizer
    device : str, optional (default='cuda')
        Device to use for training ('cuda' or 'cpu')
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'model': Trained model
        - 'history': Dictionary with 'train_loss', 'train_acc', 'val_loss', 'val_acc' lists
    
    Example:
    --------
    >>> model = load_pretrained_model('resnet18')
    >>> result = train_transfer_model(model, train_loader, val_loader, epochs=5)
    >>> print(f"Final validation accuracy: {result['history']['val_acc'][-1]:.2f}%")
    
    Lab Context:
    ------------
    This implements the training loop from Lab 7. When using transfer learning
    with frozen backbone, only the final classification layer is trained, which
    significantly reduces training time while still achieving good performance
    on the target dataset (Fashion-MNIST).
    """
    # Lazy import PyTorch (only when function is called)
    torch, nn, optim, DataLoader, datasets, transforms, models = _lazy_import_torch()
    
    # Set device
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    
    # Get only trainable parameters (no lambda - beginner friendly)
    trainable_params = []
    for param in model.parameters():
        if param.requires_grad:
            trainable_params.append(param)
    
    optimizer = optim.Adam(trainable_params, lr=lr)
    
    # Training history
    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        # Calculate metrics
        train_loss = train_loss / len(train_loader)
        train_acc = 100. * train_correct / train_total
        val_loss = val_loss / len(val_loader)
        val_acc = 100. * val_correct / val_total
        
        # Store history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f'Epoch [{epoch+1}/{epochs}] '
              f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%, '
              f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
    
    return {
        'model': model,
        'history': history
    }


@ShowableFunction
def evaluate_transfer_model(model, test_loader, device='cuda'):
    """
    Evaluate a trained transfer learning model on test data.
    
    Computes test accuracy and per-class accuracies. Also returns predictions
    and true labels for further analysis if needed.
    
    Parameters:
    -----------
    model : torch.nn.Module
        Trained model to evaluate
    test_loader : torch.utils.data.DataLoader
        DataLoader for test data
    device : str, optional (default='cuda')
        Device to use for evaluation ('cuda' or 'cpu')
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'test_acc': Overall test accuracy (%)
        - 'predictions': All predictions (numpy array)
        - 'true_labels': All true labels (numpy array)
        - 'per_class_acc': Accuracy for each class (dict)
    
    Example:
    --------
    >>> result = evaluate_transfer_model(model, test_loader)
    >>> print(f"Test Accuracy: {result['test_acc']:.2f}%")
    >>> print(f"Class 0 Accuracy: {result['per_class_acc'][0]:.2f}%")
    
    Lab Context:
    ------------
    This evaluates the transfer learning model on Fashion-MNIST test data,
    providing both overall accuracy and per-class metrics to understand
    which clothing categories the model recognizes well.
    """
    # Lazy import PyTorch (only when function is called)
    torch, nn, optim, DataLoader, datasets, transforms, models = _lazy_import_torch()
    
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()
    
    all_predictions = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Convert to numpy arrays
    predictions = np.array(all_predictions)
    true_labels = np.array(all_labels)
    
    # Calculate overall accuracy
    test_acc = 100. * np.sum(predictions == true_labels) / len(true_labels)
    
    # Calculate per-class accuracy
    per_class_acc = {}
    num_classes = len(np.unique(true_labels))
    
    for class_idx in range(num_classes):
        class_mask = true_labels == class_idx
        if np.sum(class_mask) > 0:
            class_correct = np.sum((predictions == true_labels) & class_mask)
            per_class_acc[class_idx] = 100. * class_correct / np.sum(class_mask)
    
    return {
        'test_acc': test_acc,
        'predictions': predictions,
        'true_labels': true_labels,
        'per_class_acc': per_class_acc
    }


@ShowableFunction
def load_fashion_mnist(batch_size=64, img_size=224):
    """
    Load Fashion-MNIST dataset with preprocessing for pretrained models.
    
    Creates train, validation, and test DataLoaders with appropriate transforms.
    Images are resized to 224x224 and converted to 3 channels (RGB) to match
    the input requirements of pretrained ImageNet models.
    
    Parameters:
    -----------
    batch_size : int, optional (default=64)
        Batch size for DataLoaders
    img_size : int, optional (default=224)
        Target image size (ImageNet models expect 224x224)
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'train_loader': Training DataLoader
        - 'val_loader': Validation DataLoader (split from training set)
        - 'test_loader': Test DataLoader
        - 'classes': List of class names
    
    Example:
    --------
    >>> data = load_fashion_mnist(batch_size=32)
    >>> print(f"Classes: {data['classes']}")
    >>> for images, labels in data['train_loader']:
    >>>     print(f"Batch shape: {images.shape}")
    >>>     break
    
    Lab Context:
    ------------
    Fashion-MNIST contains 28x28 grayscale images of clothing items.
    For transfer learning with ImageNet models, we resize to 224x224
    and convert to 3 channels (RGB) by repeating the grayscale channel.
    """
    # Lazy import PyTorch (only when function is called)
    torch, nn, optim, DataLoader, datasets, transforms, models = _lazy_import_torch()
    
    # Define transforms
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.Grayscale(num_output_channels=3),  # Convert to 3 channels
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load datasets
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
    
    # Split training into train and validation (80-20)
    train_size = int(0.8 * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        train_dataset, [train_size, val_size]
    )
    
    # Create DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Fashion-MNIST class names
    classes = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
    
    return {
        'train_loader': train_loader,
        'val_loader': val_loader,
        'test_loader': test_loader,
        'classes': classes
    }
