"""
RangeFlow Functional Interface
===============================
Stateless functional API for interval operations.

Usage:
    import rangeflow.functional as R
    
    x_range = R.from_epsilon_ball(x, 0.1)
    y_range = R.relu(R.linear(x_range, weight, bias))

This provides a JAX/NumPy-style functional interface for users
who prefer stateless operations over nn.Module classes.
"""

import torch
import numpy as np
from .core import RangeTensor, _op
from .backend import get_backend

xp = get_backend()


# ==========================================
# CREATION FUNCTIONS
# ==========================================

def from_range(min_val, max_val):
    """
    Create RangeTensor from explicit bounds.
    
    Args:
        min_val: Lower bounds
        max_val: Upper bounds
    
    Returns:
        RangeTensor
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_range = R.from_range(torch.tensor([1.0]), torch.tensor([2.0]))
    """
    return RangeTensor.from_range(min_val, max_val)


def from_epsilon_ball(center, epsilon):
    """
    Create L-infinity ball around center.
    
    Args:
        center: Center point
        epsilon: Radius
    
    Returns:
        RangeTensor representing [center-ε, center+ε]
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_range = R.from_epsilon_ball(torch.randn(10), 0.1)
    """
    return RangeTensor.from_epsilon_ball(center, epsilon)


def from_array(data):
    """
    Create degenerate range from array.
    
    Args:
        data: Array/tensor
    
    Returns:
        RangeTensor with min=max=data
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_range = R.from_array(torch.randn(10))
    """
    return RangeTensor.from_array(data)


# ==========================================
# BASIC OPERATIONS
# ==========================================

def add(x, y):
    """
    Range addition: [a,b] + [c,d] = [a+c, b+d]
    
    Example:
        >>> import rangeflow.functional as R
        >>> z = R.add(x_range, y_range)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(y, RangeTensor):
        y = RangeTensor.from_array(y)
    return x + y


def sub(x, y):
    """Range subtraction: [a,b] - [c,d] = [a-d, b-c]"""
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(y, RangeTensor):
        y = RangeTensor.from_array(y)
    return x - y


def mul(x, y):
    """Range multiplication with all corner evaluation"""
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(y, RangeTensor):
        y = RangeTensor.from_array(y)
    return x * y


def div(x, y):
    """Range division with zero handling"""
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(y, RangeTensor):
        y = RangeTensor.from_array(y)
    return x / y


def matmul(x, y):
    """
    Range matrix multiplication with monotonicity shortcut.
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_range = R.from_epsilon_ball(x, 0.1)
        >>> y = R.matmul(x_range, weight.T)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(y, RangeTensor):
        y = RangeTensor.from_array(y)
    return x @ y


# ==========================================
# ACTIVATION FUNCTIONS
# ==========================================

def relu(x):
    """
    Range ReLU: max(0, x)
    
    Example:
        >>> import rangeflow.functional as R
        >>> y = R.relu(x_range)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.relu()


def sigmoid(x):
    """Range sigmoid: 1/(1+e^-x)"""
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.sigmoid()


def tanh(x):
    """Range tanh: (e^x - e^-x)/(e^x + e^-x)"""
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.tanh()


def softmax(x, axis=-1):
    """
    Range softmax with conservative bounds.
    
    Args:
        x: RangeTensor
        axis: Dimension to apply softmax
    
    Returns:
        RangeTensor with softmax bounds
    
    Example:
        >>> import rangeflow.functional as R
        >>> probs = R.softmax(logits_range, axis=-1)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.softmax(axis=axis)


def gelu(x):
    """
    Range GELU activation.
    
    GELU(x) = x * Φ(x) where Φ is standard normal CDF
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    
    # GELU approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
    from .layers import RangeGELU
    gelu_layer = RangeGELU()
    return gelu_layer(x)


# ==========================================
# LAYER OPERATIONS
# ==========================================

def linear(x, weight, bias=None):
    """
    Range linear transformation: y = xW^T + b
    
    Args:
        x: Input RangeTensor (batch, in_features)
        weight: Weight matrix (out_features, in_features)
        bias: Optional bias (out_features,)
    
    Returns:
        Output RangeTensor (batch, out_features)
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_range = R.from_epsilon_ball(x, 0.1)
        >>> y_range = R.linear(x_range, W, b)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(weight, RangeTensor):
        weight = RangeTensor.from_array(weight)
    
    # Linear: x @ W.T
    output = x @ weight.transpose(-1, -2)
    
    if bias is not None:
        if not isinstance(bias, RangeTensor):
            bias = RangeTensor.from_array(bias)
        output = output + bias
    
    return output


def conv2d(x, weight, bias=None, stride=1, padding=0):
    """
    Range 2D convolution.
    
    Args:
        x: Input RangeTensor (batch, in_channels, H, W)
        weight: Conv weight (out_channels, in_channels, K, K)
        bias: Optional bias (out_channels,)
        stride: Convolution stride
        padding: Padding size
    
    Returns:
        Output RangeTensor (batch, out_channels, H_out, W_out)
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_range = R.from_epsilon_ball(images, 0.1)
        >>> y_range = R.conv2d(x_range, conv_weight, stride=1, padding=1)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(weight, RangeTensor):
        weight = RangeTensor.from_array(weight)
    
    if bias is not None and not isinstance(bias, RangeTensor):
        bias = RangeTensor.from_array(bias)
    
    return _op("conv2d", x, weight, bias, stride=stride, padding=padding)


def layer_norm(x, normalized_shape, weight=None, bias=None, eps=1e-5):
    """
    Range layer normalization.
    
    Args:
        x: Input RangeTensor
        normalized_shape: Shape to normalize over
        weight: Optional scale parameter
        bias: Optional shift parameter
        eps: Stability constant
    
    Returns:
        Normalized RangeTensor
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_norm = R.layer_norm(x_range, (128,))
    """
    from .layers import RangeLayerNorm
    
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    
    # Create temporary layer
    layer = RangeLayerNorm(normalized_shape, eps=eps)
    
    if weight is not None:
        layer.weight.data = weight
    if bias is not None:
        layer.bias.data = bias
    
    return layer(x)


def batch_norm(x, running_mean, running_var, weight=None, bias=None, 
               training=False, momentum=0.1, eps=1e-5):
    """
    Range batch normalization.
    
    Args:
        x: Input RangeTensor
        running_mean: Running mean for inference
        running_var: Running variance for inference
        weight: Optional scale
        bias: Optional shift
        training: Training mode flag
        momentum: Update momentum
        eps: Stability constant
    
    Returns:
        Normalized RangeTensor
    """
    from .layers import RangeBatchNorm1d
    
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    
    # This is simplified - full implementation would handle all cases
    raise NotImplementedError("Functional batch_norm coming soon")


# ==========================================
# POOLING OPERATIONS
# ==========================================

def max_pool2d(x, kernel_size, stride=None, padding=0):
    """
    Range max pooling.
    
    Args:
        x: Input RangeTensor (batch, channels, H, W)
        kernel_size: Pooling window size
        stride: Stride (default: kernel_size)
        padding: Padding size
    
    Returns:
        Pooled RangeTensor
    
    Example:
        >>> import rangeflow.functional as R
        >>> y = R.max_pool2d(x_range, kernel_size=2, stride=2)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    
    return _op("max_pool2d", x, kernel_size=kernel_size, stride=stride, padding=padding)


def avg_pool2d(x, kernel_size, stride=None, padding=0):
    """
    Range average pooling.
    
    Args:
        x: Input RangeTensor (batch, channels, H, W)
        kernel_size: Pooling window size
        stride: Stride (default: kernel_size)
        padding: Padding size
    
    Returns:
        Pooled RangeTensor
    
    Example:
        >>> import rangeflow.functional as R
        >>> y = R.avg_pool2d(x_range, kernel_size=2, stride=2)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    
    return _op("avg_pool2d", x, kernel_size=kernel_size, stride=stride, padding=padding)


# ==========================================
# SHAPE OPERATIONS
# ==========================================

def reshape(x, *shape):
    """
    Reshape RangeTensor.
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_flat = R.reshape(x_range, batch_size, -1)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.reshape(*shape)


def flatten(x, start_dim=1):
    """
    Flatten RangeTensor.
    
    Args:
        x: RangeTensor to flatten
        start_dim: Dimension to start flattening from
    
    Returns:
        Flattened RangeTensor
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_flat = R.flatten(x_range)  # (batch, features)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.flatten()


def transpose(x, dim0, dim1):
    """
    Transpose dimensions of RangeTensor.
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_T = R.transpose(x_range, -1, -2)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.transpose(dim0, dim1)


# ==========================================
# RANGE-SPECIFIC OPERATIONS
# ==========================================

def decay(x):
    """
    Execute computation graph and get bounds.
    
    Args:
        x: RangeTensor
    
    Returns:
        (min_bounds, max_bounds) tuple
    
    Example:
        >>> import rangeflow.functional as R
        >>> min_val, max_val = R.decay(x_range)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.decay()


def width(x):
    """
    Get uncertainty width.
    
    Example:
        >>> import rangeflow.functional as R
        >>> w = R.width(x_range)  # How uncertain is x?
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.width()


def center(x):
    """
    Get range center (average of bounds).
    
    Example:
        >>> import rangeflow.functional as R
        >>> c = R.center(x_range)  # Best estimate of x
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    return x.center()


def union(x, y):
    """
    Union of two ranges (if overlapping).
    
    Example:
        >>> import rangeflow.functional as R
        >>> z = R.union(x_range, y_range)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(y, RangeTensor):
        y = RangeTensor.from_array(y)
    return x.union(y)


def intersection(x, y):
    """
    Intersection of two ranges.
    
    Example:
        >>> import rangeflow.functional as R
        >>> z = R.intersection(x_range, y_range)
    """
    if not isinstance(x, RangeTensor):
        x = RangeTensor.from_array(x)
    if not isinstance(y, RangeTensor):
        y = RangeTensor.from_array(y)
    return x.intersection(y)


# ==========================================
# LOSS FUNCTIONS
# ==========================================

def robust_cross_entropy(y_range, target, mode='worst_case'):
    """
    Robust cross-entropy loss.
    
    Example:
        >>> import rangeflow.functional as R
        >>> loss = R.robust_cross_entropy(logits_range, labels)
    """
    from .loss import robust_cross_entropy as rce
    return rce(y_range, target, mode=mode)


def robust_mse(y_range, target, mode='worst_case'):
    """
    Robust MSE loss.
    
    Example:
        >>> import rangeflow.functional as R
        >>> loss = R.robust_mse(pred_range, y_true)
    """
    from .loss import robust_mse as rmse
    return rmse(y_range, target, mode=mode)


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def clamp(x, min_val=None, max_val=None):
    """
    Clamp RangeTensor to specified range.
    
    Args:
        x: RangeTensor
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Clamped RangeTensor
    
    Example:
        >>> import rangeflow.functional as R
        >>> x_clamped = R.clamp(x_range, min_val=0.0, max_val=1.0)
    """
    min_x, max_x = decay(x)
    
    if min_val is not None:
        min_x = torch.clamp(min_x, min=min_val)
        max_x = torch.clamp(max_x, min=min_val)
    
    if max_val is not None:
        min_x = torch.clamp(min_x, max=max_val)
        max_x = torch.clamp(max_x, max=max_val)
    
    return from_range(min_x, max_x)


def concatenate(ranges, axis=0):
    """
    Concatenate multiple RangeTensors.
    
    Args:
        ranges: List of RangeTensors
        axis: Concatenation axis
    
    Returns:
        Concatenated RangeTensor
    
    Example:
        >>> import rangeflow.functional as R
        >>> z = R.concatenate([x_range, y_range], axis=1)
    """
    # Ensure all are RangeTensors
    ranges = [r if isinstance(r, RangeTensor) else from_array(r) for r in ranges]
    
    if len(ranges) == 0:
        raise ValueError("Cannot concatenate empty list")
    
    if len(ranges) == 1:
        return ranges[0]
    
    # Use the _op system
    return _op("concatenate", *ranges, axis=axis)


# ==========================================
# PIPELINE HELPERS
# ==========================================

def sequential(*operations):
    """
    Create a sequential pipeline of operations.
    
    Args:
        *operations: List of functions to apply sequentially
    
    Returns:
        Function that applies all operations in sequence
    
    Example:
        >>> import rangeflow.functional as R
        >>> 
        >>> model = R.sequential(
        ...     lambda x: R.linear(x, W1, b1),
        ...     R.relu,
        ...     lambda x: R.linear(x, W2, b2)
        ... )
        >>> 
        >>> y = model(x_range)
    """
    def pipeline(x):
        for op in operations:
            x = op(x)
        return x
    
    return pipeline


def compose(*functions):
    """
    Compose functions (right to left).
    
    Example:
        >>> import rangeflow.functional as R
        >>> f = R.compose(R.softmax, R.relu, lambda x: R.linear(x, W))
        >>> y = f(x_range)  # Equivalent to softmax(relu(linear(x, W)))
    """
    def composed(x):
        for func in reversed(functions):
            x = func(x)
        return x
    
    return composed


# Export all public APIs
__all__ = [
    # Creation
    'from_range', 'from_epsilon_ball', 'from_array',
    
    # Basic ops
    'add', 'sub', 'mul', 'div', 'matmul',
    
    # Activations
    'relu', 'sigmoid', 'tanh', 'softmax', 'gelu',
    
    # Layers
    'linear', 'conv2d', 'layer_norm', 'batch_norm',
    
    # Pooling
    'max_pool2d', 'avg_pool2d',
    
    # Shape ops
    'reshape', 'flatten', 'transpose',
    
    # Range ops
    'decay', 'width', 'center', 'union', 'intersection',
    
    # Loss
    'robust_cross_entropy', 'robust_mse',
    
    # Utilities
    'clamp', 'concatenate', 'sequential', 'compose'
]