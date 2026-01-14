import neuralengine.config as cf
from functools import wraps
from .tensor import *


@cf.Typed.validate
def tensor(data, requires_grad: bool = False, dtype: type = None) -> Tensor:
    """Creates a Tensor from data.
    @param data: Input data (array-like)
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    return Tensor(data, requires_grad=requires_grad, dtype=dtype)

@cf.Typed.validate
def zeros(*shape: int, requires_grad: bool = False, dtype: type = None) -> Tensor:
    """Creates a Tensor of zeros.
    @param shape: Shape of tensor
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    data = cf.xp.zeros(shape)
    return Tensor(data, requires_grad=requires_grad, dtype=dtype)

@cf.Typed.validate
def ones(*shape: int, requires_grad: bool = False, dtype: type = None) -> Tensor:
    """Creates a Tensor of ones.
    @param shape: Shape of tensor
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    data = cf.xp.ones(shape)
    return Tensor(data, requires_grad=requires_grad, dtype=dtype)

@cf.Typed.validate
def rand(*shape: int, requires_grad: bool = False, dtype: type = None) -> Tensor:
    """Creates a Tensor with random values (uniform).
    @param shape: Shape of tensor
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    data = cf.xp.random.rand(*shape)
    return Tensor(data, requires_grad=requires_grad, dtype=dtype)

@cf.Typed.validate
def randn(*shape: int, xavier: bool = False, requires_grad: bool = False, \
          dtype: type = None) -> Tensor:
    """Creates a Tensor with random values (normal).
    @param shape: Shape of tensor
    @param xavier: Use Xavier scaling
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    data = cf.xp.random.randn(*shape)
    if xavier:
        # Xavier scaling: data / √(first dimension)
        data /= cf.xp.sqrt(shape[0])
    return Tensor(data, requires_grad=requires_grad, dtype=dtype)

@cf.Typed.validate
def randint(low: int, high: int, *shape: int, requires_grad: bool = False, \
            dtype: type[cf.DType.INT] = None) -> Tensor:
    """Creates a Tensor with random integers.
    @param low: Minimum value
    @param high: Maximum value
    @param shape: Shape of tensor
    @param requires_grad: Track gradients
    @param dtype: Data type (integer type)
    """
    data = cf.xp.random.randint(low, high, size=shape)
    return Tensor(data, requires_grad=requires_grad, dtype=dtype)

def zeros_like(tensor: Tensor, requires_grad: bool = None, dtype: type = None) -> Tensor:
    """Creates a zeros Tensor with same shape as input.
    @param tensor: Reference tensor
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    shape = tensor.shape
    requires_grad=requires_grad if requires_grad else tensor.requires_grad
    return zeros(*shape, requires_grad=requires_grad, dtype=dtype)

def ones_like(tensor: Tensor, requires_grad: bool = None, dtype: type = None) -> Tensor:
    """Creates a ones Tensor with same shape as input.
    @param tensor: Reference tensor
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    shape = tensor.shape
    requires_grad=requires_grad if requires_grad else tensor.requires_grad
    return ones(*shape, requires_grad=requires_grad, dtype=dtype)

def rand_like(tensor: Tensor, requires_grad: bool = None, dtype: type = None) -> Tensor:
    """Creates a random Tensor with same shape as input. (uniform)
    @param tensor: Reference tensor
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    shape = tensor.shape
    requires_grad=requires_grad if requires_grad else tensor.requires_grad
    return rand(*shape, requires_grad=requires_grad, dtype=dtype)

def randn_like(tensor: Tensor, xavier: bool = False, requires_grad: bool = None, \
               dtype: type = None) -> Tensor:
    """Creates a random normal Tensor with same shape as input. (normal)
    @param tensor: Reference tensor
    @param xavier: Use Xavier scaling
    @param requires_grad: Track gradients
    @param dtype: Data type
    """
    shape = tensor.shape
    requires_grad=requires_grad if requires_grad else tensor.requires_grad
    return randn(*shape, xavier=xavier, requires_grad=requires_grad, dtype=dtype)

def randint_like(tensor: Tensor, low: int, high: int, requires_grad: bool = None, \
                 dtype: type[cf.DType.INT] = None) -> Tensor:
    """Creates a random integer Tensor with same shape as input.
    @param tensor: Reference tensor
    @param low: Minimum value
    @param high: Maximum value
    @param requires_grad: Track gradients
    @param dtype: Data type (integer type)
    """
    shape = tensor.shape
    requires_grad=requires_grad if requires_grad else tensor.requires_grad
    return randint(low, high, *shape, requires_grad=requires_grad, dtype=dtype)

@cf.Typed.validate
def sum(tensor: Tensor, axis: int = -1, keepdims: bool = False) -> Tensor:
    """Sum over axis.
    @param tensor: Input tensor
    @param axis: Axis to sum
    @param keepdims: Keep reduced dims
    """
    return tensor.sum(axis=axis, keepdims=keepdims)

@cf.Typed.validate
def min(tensor: Tensor, axis: int = -1, keepdims: bool = False) -> Tensor:
    """Min over axis.
    @param tensor: Input tensor
    @param axis: Axis to min
    @param keepdims: Keep reduced dims
    """
    return tensor.min(axis=axis, keepdims=keepdims)

@cf.Typed.validate
def max(tensor: Tensor, axis: int = -1, keepdims: bool = False) -> Tensor:
    """Max over axis.
    @param tensor: Input tensor
    @param axis: Axis to max
    @param keepdims: Keep reduced dims
    """
    return tensor.max(axis=axis, keepdims=keepdims)

@cf.Typed.validate
def argmax(tensor: Tensor, axis: int = -1, dtype: type[cf.DType.INT] = None) -> Tensor:
    """Argmax over axis.
    @param tensor: Input tensor
    @param axis: Axis to argmax
    @param dtype: Data type (integer type)
    """
    indices = cf.xp.argmax(tensor.data, axis=axis)
    return Tensor(indices, requires_grad=False, dtype=dtype)

@cf.Typed.validate
def mean(tensor: Tensor, axis: int = -1, keepdims: bool = False) -> Tensor:
    """Mean over axis.
    @param tensor: Input tensor
    @param axis: Axis to mean
    @param keepdims: Keep reduced dims
    """
    return tensor.mean(axis=axis, keepdims=keepdims)

@cf.Typed.validate
def var(tensor: Tensor, axis: int = -1, keepdims: bool = False) -> Tensor:
    """Variance over axis.
    @param tensor: Input tensor
    @param axis: Axis to variance
    @param keepdims: Keep reduced dims
    """
    return tensor.var(axis=axis, keepdims=keepdims)

@cf.Typed.validate
def log(tensor: Tensor) -> Tensor:
    """Elementwise natural logarithm.
    @param tensor: Input tensor
    """
    return Logarithm(tensor)()

@cf.Typed.validate
def sqrt(tensor: Tensor) -> Tensor:
    """Elementwise square root.
    @param tensor: Input tensor
    """
    return SquareRoot(tensor)()

@cf.Typed.validate
def exp(tensor: Tensor) -> Tensor:
    """Elementwise exponential.
    @param tensor: Input tensor
    """
    return Exponential(tensor)()

@cf.Typed.validate
def abs(tensor: Tensor) -> Tensor:
    """Elementwise absolute value.
    @param tensor: Input tensor
    """
    return Absolute(tensor)()

@cf.Typed.validate
def concat(*tensors: Tensor, axis: int = 0) -> Tensor:
    """Concatenates tensors along axis.
    @param tensors: Tensors to concatenate
    @param axis: Axis to concatenate
    """
    return Concatenate(tensors, axis)()

@cf.Typed.validate
def stack(*tensors: Tensor, axis: int = 0) -> Tensor:
    """Stacks tensors along axis.
    @param tensors: Tensors to stack
    @param axis: Axis to stack
    """
    return Stack(tensors, axis)()

@cf.Typed.validate
def where(condition, tensor: Tensor, value: float | Tensor) -> Tensor:
    """Elementwise selection: if condition then tensor else value.
    @param condition: Boolean mask
    @param tensor: Tensor to select
    @param value: Value to fill where condition is False
    """
    return MaskedFill(tensor, condition, value)()

@cf.Typed.validate
def clip(tensor: Tensor, minimum: float, maximum: float) -> Tensor:
    """Clips tensor values to [min, max].
    @param tensor: Input tensor
    @param min: Minimum value
    @param max: Maximum value
    """
    # min/max clipping
    tensor = tensor.masked_fill(tensor < minimum, minimum)
    tensor = tensor.masked_fill(tensor > maximum, maximum)
    return tensor

@cf.Typed.validate
def standardize(tensor: Tensor, axis: int = -1, eps: float = 1e-7) -> Tensor:
    """Standardizes tensor over axis.
    @param tensor: Input tensor
    @param axis: Axis to standardize
    @param eps: Small value for numerical stability
    """
    # x = (x - μ) / σ
    mu = mean(tensor, axis=axis, keepdims=True)
    variance = var(tensor, axis=axis, keepdims=True)
    std = sqrt(variance + eps)
    return (tensor - mu) / std

@cf.Typed.validate
def normalize(tensor: Tensor, axis: int = -1, eps: float = 1e-7) -> Tensor:
    """Normalizes tensor over axis.
    @param tensor: Input tensor
    @param axis: Axis to normalize
    @param eps: Small value for numerical stability
    """
    # x = (x - min) / (max - min)
    minimum = min(tensor, axis=axis, keepdims=True)
    maximum = max(tensor, axis=axis, keepdims=True)
    return (tensor - minimum) / (maximum - minimum + eps)

@cf.Typed.validate
def one_hot(labels, num_classes: int = None, dtype: type[cf.DType.INT] = cf.DType.INT32) -> Tensor:
    """Converts integer labels to one-hot encoding.
    @param labels: Integer labels
    @param num_classes: Number of classes
    @param dtype: Data type (integer type)
    """
    labels = array(labels, dtype=dtype)
    if num_classes is None:
        num_classes = int(cf.xp.max(labels) + 1)
    # one-hot encoding: eye(num_classes)[labels]
    encoded = cf.xp.eye(num_classes)[labels]
    return Tensor(encoded, dtype=dtype)

def no_grad(func):
    """Decorator to disable gradient tracking in a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with NoGrad():
            return func(*args, **kwargs)
    return wrapper