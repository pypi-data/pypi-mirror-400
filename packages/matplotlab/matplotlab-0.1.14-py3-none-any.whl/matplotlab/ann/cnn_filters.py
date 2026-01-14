"""Lab 6: CNN Filters - Apply custom filters to images using Conv2D"""

import numpy as np
from ._code_inspector import ShowableFunction

# Lazy imports to avoid slow module loading
def _lazy_import_tensorflow():
    """Import TensorFlow only when needed"""
    import tensorflow as tf
    from tensorflow.keras import layers, models
    return tf, layers, models

def _lazy_import_pil():
    """Import PIL only when needed"""
    from PIL import Image
    return Image

# Predefined filters (internal - not exposed as separate functions)
FILTERS = {
    'edge': np.array([[-1, -1, -1],
                      [-1,  8, -1],
                      [-1, -1, -1]]),
    
    'vertical': np.array([[ 1,  0, -1],
                          [ 1,  0, -1],
                          [ 1,  0, -1]]),
    
    'horizontal': np.array([[ 1,  1,  1],
                            [ 0,  0,  0],
                            [-1, -1, -1]]),
    
    'smoothing': np.array([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]]) / 9.0,
    
    'sharpening': np.array([[ 0, -1,  0],
                            [-1,  5, -1],
                            [ 0, -1,  0]])
}


@ShowableFunction
def apply_cnn_filter(image_path, filter_type='edge', channel=0):
    """
    Apply a custom CNN filter to an image using Conv2D.
    
    This function loads an image, applies one of the predefined filters
    (edge detection, vertical/horizontal edge detection, smoothing, or sharpening)
    using a Conv2D layer, and returns both the original and filtered images.
    
    Parameters:
    -----------
    image_path : str
        Path to the input image file
    filter_type : str, optional (default='edge')
        Type of filter to apply. Options: 'edge', 'vertical', 'horizontal', 
        'smoothing', 'sharpening'
    channel : int, optional (default=0)
        Which color channel to use (0=Red, 1=Green, 2=Blue)
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'original': Original image as numpy array (shape: H x W x C)
        - 'filtered': Filtered image as numpy array (shape: H x W)
        - 'filter': The filter kernel used (shape: 3 x 3)
        - 'model': The Keras model used for filtering
    
    Example:
    --------
    >>> result = apply_cnn_filter('path/to/image.jpg', filter_type='edge')
    >>> plt.imshow(result['filtered'], cmap='gray')
    >>> plt.show()
    
    Lab Context:
    ------------
    This implements the core functionality from Lab 6, where we use Conv2D
    layers with predefined filter weights to perform image processing tasks
    like edge detection and smoothing. The filters are set as non-trainable
    weights in a simple Sequential model.
    """
    # Lazy import TensorFlow (only when function is called)
    tf, layers, models = _lazy_import_tensorflow()
    Image = _lazy_import_pil()
    
    # Validate filter type
    if filter_type not in FILTERS:
        raise ValueError(f"Invalid filter_type. Choose from: {list(FILTERS.keys())}")
    
    # Get the filter and reshape for Conv2D (3x3x1x1)
    filter_kernel = FILTERS[filter_type].reshape((3, 3, 1, 1))
    
    # Load and prepare image
    img = Image.open(image_path)
    img_array = np.array(img).astype('float32')
    
    # Handle both grayscale and RGB images
    if len(img_array.shape) == 2:
        # Grayscale image
        channel_image = img_array
    else:
        # RGB image - extract specified channel
        channel_image = img_array[:, :, channel]
    
    # Reshape for Conv2D (batch_size, height, width, channels)
    input_image = channel_image.reshape(1, channel_image.shape[0], channel_image.shape[1], 1)
    
    # Create Conv2D model with custom filter weights
    model = models.Sequential([
        layers.Conv2D(
            filters=1,
            kernel_size=(3, 3),
            input_shape=(input_image.shape[1], input_image.shape[2], 1),
            use_bias=False
        )
    ])
    
    # Set the filter weights (non-trainable)
    model.layers[0].set_weights([filter_kernel])
    
    # Apply filter
    output_image = model.predict(input_image, verbose=0)
    
    return {
        'original': img_array,
        'filtered': output_image[0, :, :, 0],
        'filter': FILTERS[filter_type],
        'model': model
    }


@ShowableFunction
def get_available_filters():
    """
    Get list of available filter types and their kernel values.
    
    Returns:
    --------
    dict : Dictionary mapping filter names to their kernel arrays
    
    Example:
    --------
    >>> filters = get_available_filters()
    >>> print(filters.keys())
    dict_keys(['edge', 'vertical', 'horizontal', 'smoothing', 'sharpening'])
    """
    return FILTERS.copy()


@ShowableFunction
def load_and_prepare_image(image_path):
    """
    Load an image from file and prepare it for CNN filter application.
    
    Loads the image using PIL, converts to numpy array, casts to float32,
    and reshapes for Conv2D input format.
    
    Parameters:
    -----------
    image_path : str
        Path to the input image file
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'original_array': Original image as numpy array
        - 'input_tensor': Reshaped image ready for Conv2D (batch format)
        - 'shape': Original image shape
    
    Example:
    --------
    >>> img_data = load_and_prepare_image('path/to/image.jpg')
    >>> print(img_data['shape'])
    (512, 512, 3)
    
    Lab Context:
    ------------
    From Lab 6 cells #VSC-62c06e9a and #VSC-84b6128e.
    Prepares images in the format expected by TensorFlow Conv2D layers.
    """
    Image = _lazy_import_pil()
    
    # Load image
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # Prepare for Conv2D
    img_array = img_array.astype('float32')
    input_image = img_array.reshape(1, img_array.shape[0], img_array.shape[1], 3)
    
    return {
        'original_array': img_array,
        'input_tensor': input_image,
        'shape': img_array.shape
    }


@ShowableFunction
def visualize_original_image(image_path, channel=0, title="Original Image"):
    """
    Display the original image before filtering.
    
    Parameters:
    -----------
    image_path : str
        Path to the input image file
    channel : int, optional (default=0)
        Which color channel to display (0=Red, 1=Green, 2=Blue)
    title : str, optional
        Title for the plot
    
    Returns:
    --------
    None (displays plot)
    
    Example:
    --------
    >>> visualize_original_image('path/to/image.jpg')
    
    Lab Context:
    ------------
    From Lab 6 cell #VSC-84b6128e.
    Shows the input image before applying filters.
    """
    import matplotlib.pyplot as plt
    
    img_data = load_and_prepare_image(image_path)
    input_image = img_data['input_tensor']
    
    plt.imshow(input_image[0, :, :, channel])
    plt.title(title)
    plt.axis('off')
    plt.show()


@ShowableFunction
def visualize_filtered_image(result, title=None, cmap='gray'):
    """
    Display the result of applying a filter to an image.
    
    Parameters:
    -----------
    result : dict
        Result dictionary from apply_cnn_filter()
    title : str, optional
        Title for the plot. If None, uses filter type.
    cmap : str, optional (default='gray')
        Colormap for visualization
    
    Returns:
    --------
    None (displays plot)
    
    Example:
    --------
    >>> result = apply_cnn_filter('path/to/image.jpg', filter_type='edge')
    >>> visualize_filtered_image(result)
    
    Lab Context:
    ------------
    From Lab 6 cells #VSC-d2f1dbd7, #VSC-9550d749, etc.
    Shows the filtered image output.
    """
    import matplotlib.pyplot as plt
    
    if title is None:
        title = "Filtered Image"
    
    plt.imshow(result['filtered'], cmap=cmap)
    plt.title(title)
    plt.axis('off')
    plt.show()


@ShowableFunction
def compare_all_filters(image_path, channel=0):
    """
    Apply all 5 filters to an image and display results side-by-side.
    
    Creates a subplot showing the original image and all filtered versions
    for easy comparison of different filter effects.
    
    Parameters:
    -----------
    image_path : str
        Path to the input image file
    channel : int, optional (default=0)
        Which color channel to use
    
    Returns:
    --------
    dict : Dictionary with filter names as keys and filtered images as values
    
    Example:
    --------
    >>> results = compare_all_filters('path/to/image.jpg')
    
    Lab Context:
    ------------
    Combines functionality from all filter cells in Lab 6.
    Shows visual comparison of edge, vertical, horizontal, smoothing, and sharpening filters.
    """
    import matplotlib.pyplot as plt
    
    # Load image
    img_data = load_and_prepare_image(image_path)
    
    # Apply all filters
    results = {}
    filter_names = list(FILTERS.keys())
    
    for filter_name in filter_names:
        result = apply_cnn_filter(image_path, filter_type=filter_name, channel=channel)
        results[filter_name] = result['filtered']
    
    # Create subplot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    # Show original
    axes[0].imshow(img_data['input_tensor'][0, :, :, channel])
    axes[0].set_title("Original Image")
    axes[0].axis('off')
    
    # Show filtered images
    for idx, (filter_name, filtered_img) in enumerate(results.items(), start=1):
        axes[idx].imshow(filtered_img, cmap='gray')
        axes[idx].set_title(f"{filter_name.capitalize()} Filter")
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return results


@ShowableFunction
def create_filter_model(filter_weights, input_shape):
    """
    Create a Conv2D model with custom filter weights.
    
    This is a low-level function that creates the actual Keras model
    with specified filter weights, matching the pattern from Lab 6.
    
    Parameters:
    -----------
    filter_weights : numpy.ndarray
        Filter kernel as 4D array (height, width, in_channels, out_channels)
    input_shape : tuple
        Shape of input image (height, width, channels)
    
    Returns:
    --------
    model : tensorflow.keras.Model
        Compiled Sequential model with Conv2D layer
    
    Example:
    --------
    >>> filters = get_available_filters()
    >>> edge_filter = filters['edge'].reshape((3, 3, 1, 1))
    >>> model = create_filter_model(edge_filter, (512, 512, 1))
    
    Lab Context:
    ------------
    From Lab 6 cells #VSC-d2f1dbd7, etc.
    Creates the Sequential model structure used in the lab.
    """
    tf, layers, models = _lazy_import_tensorflow()
    
    model = models.Sequential()
    model.add(layers.Conv2D(
        filters=1,
        kernel_size=(3, 3),
        input_shape=input_shape,
        use_bias=False
    ))
    model.layers[0].set_weights([filter_weights])
    
    return model
