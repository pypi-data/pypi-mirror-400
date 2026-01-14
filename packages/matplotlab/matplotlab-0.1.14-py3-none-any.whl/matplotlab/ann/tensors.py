"""
Lab 1 - PyTorch Tensor Operations.
Basic tensor manipulations, operations, and autograd functionality.
"""

import torch
import numpy as np


# ============================================================================
# Tensor Creation Functions
# ============================================================================

def create_scalar(value=1.5):
    """Create a scalar (0-D tensor)."""
    return torch.tensor(value)


def create_vector(values=None):
    """Create a vector (1-D tensor)."""
    if values is None:
        values = [1, 2, 3, 4, 5]
    return torch.tensor(values)


def create_matrix(values=None, rows=3, cols=3):
    """Create a matrix (2-D tensor)."""
    if values is not None:
        return torch.tensor(values)
    return torch.rand(rows, cols)


def create_tensor_3d(values=None, dim1=2, dim2=3, dim3=4):
    """Create a 3-D tensor."""
    if values is not None:
        return torch.tensor(values)
    return torch.rand(dim1, dim2, dim3)


# ============================================================================
# Tensor Operations
# ============================================================================

def tensor_element_wise_add(tensor1, tensor2):
    """Perform element-wise addition of two tensors."""
    return tensor1 + tensor2


def tensor_matrix_mul(t1, t2):
    """Perform matrix multiplication of two tensors."""
    return torch.matmul(t1, t2)


def tensor_mean(tensor, dim=None):
    """Compute mean of tensor along specified dimension."""
    # Convert to float if needed
    if tensor.dtype in [torch.int, torch.long, torch.int32, torch.int64]:
        tensor = tensor.float()
    if dim is not None:
        return torch.mean(tensor, dim=dim)
    return torch.mean(tensor)


def tensor_sum(tensor, dim=None):
    """Compute sum of tensor along specified dimension."""
    if dim is not None:
        return torch.sum(tensor, dim=dim)
    return torch.sum(tensor)


# ============================================================================
# Reshaping Functions
# ============================================================================

def tensor_reshape(tensor, *shape):
    """Reshape a tensor to the specified shape."""
    return tensor.reshape(*shape)


def tensor_arange(start, end=None):
    """Create a 1-D tensor with sequential values."""
    if end is None:
        return torch.arange(start)
    return torch.arange(start, end)


# ============================================================================
# Autograd Functions
# ============================================================================

def compute_gradient_simple(x_value):
    """
    Compute gradient of y = x^2 using autograd.
    
    Parameters:
    -----------
    x_value : float
        Input value for x
    
    Returns:
    --------
    dict
        Dictionary containing x, y, and gradient values
    """
    x = torch.tensor(x_value, requires_grad=True)
    y = x ** 2
    y.backward()
    
    return {
        'x': x.item(),
        'y': y.item(),
        'grad': x.grad.item()
    }


# ============================================================================
# Image Processing Functions
# ============================================================================

def create_image_tensor(height=5, width=5, max_val=255):
    """Create a tensor representing a grayscale image."""
    return torch.randint(0, max_val + 1, (height, width), dtype=torch.float32)


def normalize_image(image):
    """Normalize pixel values to [0, 1] range."""
    return image / 255.0


def apply_kernel_filter(image, kernel):
    """
    Apply a kernel filter to a region of the image.
    
    Parameters:
    -----------
    image : torch.Tensor
        Normalized image tensor
    kernel : torch.Tensor
        3x3 kernel for filtering
    
    Returns:
    --------
    torch.Tensor
        Filtered region of the image
    """
    if image.shape[0] < 3 or image.shape[1] < 3:
        raise ValueError("Image must be at least 3x3 for kernel application")
    
    region_of_interest = image[1:4, 1:4]
    filtered_region = region_of_interest * kernel
    return filtered_region


def calculate_average_brightness(image):
    """Calculate the mean pixel value (brightness) of an image."""
    return torch.mean(image).item()


# ============================================================================
# Data Analysis Functions
# ============================================================================

def create_sensor_data(n_samples=30):
    """Create a 1D tensor containing sequential sensor readings."""
    return torch.arange(float(n_samples))


def reshape_to_batches(data, batch_size):
    """
    Reshape 1D sensor data into batches.
    
    Parameters:
    -----------
    data : torch.Tensor
        1D tensor of sensor data
    batch_size : int
        Number of readings per batch
    
    Returns:
    --------
    torch.Tensor
        2D tensor where each row is a batch
    """
    n_batches = len(data) // batch_size
    return data.reshape(n_batches, batch_size)


def calculate_batch_averages(batched_data):
    """Calculate the average reading for each batch (row)."""
    return torch.mean(batched_data, dim=1)


def calculate_sensor_type_averages(sensor_data):
    """Calculate the average reading for each sensor type (column)."""
    return torch.mean(sensor_data, dim=0)


# ============================================================================
# Utility Functions
# ============================================================================

def check_cuda_availability():
    """
    Check if CUDA is available and return GPU info.
    
    Returns:
    --------
    dict
        Dictionary with 'available' (bool) and 'device_name' (str) keys
    """
    if torch.cuda.is_available():
        return {
            'available': True,
            'device_name': torch.cuda.get_device_name(0)
        }
    else:
        return {
            'available': False,
            'device_name': 'CPU'
        }


def get_pytorch_version():
    """Get the current PyTorch version."""
    return torch.__version__
