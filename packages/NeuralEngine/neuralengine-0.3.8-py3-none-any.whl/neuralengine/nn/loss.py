from ..config import Typed
from ..tensor import Tensor
from ..utils import *


class Loss(metaclass=Typed):
    """Base class for all loss functions."""
    def __init__(self):
        self.loss: float = 0.0
        self.count: int = 0

    def __call__(self, z, y, *args, **kwargs) -> Tensor:
        """ Calls the loss compute method with the provided predictions and targets.
        @param z: Predictions (logits or outputs of the model).
        @param y: Ground truth labels.
        """
        z = z if isinstance(z, Tensor) else tensor(z)
        y = y if isinstance(y, Tensor) else tensor(y)
        loss = self.compute(z, y, *args, **kwargs)

        self.loss += loss.data.mean().item() # Accumulate loss value as float
        self.count += 1 # Sample count
        return loss

    def __repr__(self) -> str:
        """String representation of the loss with its value if computed."""
        if self.count > 0:
            loss = self.loss / self.count
            self.reset() # Reset after printing
            return f"{self.__class__.__name__}: {loss:.4f}"
        else: return "No loss computed yet."
        
    def reset(self) -> None:
        """Resets the accumulated loss value and count."""
        self.loss = 0.0
        self.count = 0
        
    def compute(self, z: Tensor, y: Tensor, *args, **kwargs) -> Tensor:
        """Computes the loss given predictions and targets. To be implemented by subclasses."""
        raise NotImplementedError("compute() must be implemented in subclasses")


class MSE(Loss):
    """Mean Squared Error loss."""
    def __init__(self):
        super().__init__()

    def compute(self, z: Tensor, y: Tensor) -> Tensor:
        # MSE = 1/N Σ (z - y)²
        loss = (z - y) ** 2
        return mean(loss, axis=-1, keepdims=False)
    

class MAE(Loss):
    """Mean Absolute Error loss."""
    def __init__(self):
        super().__init__()

    def compute(self, z: Tensor, y: Tensor) -> Tensor:
        # MAE = 1/N Σ |z - y|
        loss = abs(z - y)
        return mean(loss, axis=-1, keepdims=False)
    

class Huber(Loss):
    """Huber loss."""
    def __init__(self, delta: float = 1.0):
        """
        @param delta: Threshold for Huber loss
        """
        super().__init__()
        self.delta = delta

    def compute(self, z: Tensor, y: Tensor) -> Tensor:
        # Huber: if |z - y| <= δ: 1/2 (z - y)² else: δ(|z - y| - 1/2 δ)
        diff = abs(z - y)
        loss = where(diff <= self.delta, 0.5 * diff ** 2, self.delta * (diff - 0.5 * self.delta))
        return mean(loss, axis=-1, keepdims=False)
    

class CrossEntropy(Loss):
    """Cross Entropy loss."""
    def __init__(self, binary: bool = False, eps: float = 1e-7):
        """
        @param binary: Whether to use binary cross entropy (default: False)
        @param eps: Small value for numerical stability
        """
        super().__init__()
        self.binary = binary
        self.eps = eps

    def compute(self, z: Tensor, y: Tensor) -> Tensor:
        # Categorical Cross Entropy: -Σ y.log(p)
        z = clip(z, self.eps, 1 - self.eps)
        loss = -y * log(z)
        # Binary Cross Entropy: -Σ y.log(p) + (1 - y).log(1 - p)
        if self.binary:
            loss -= (1 - y) * log(1 - z)
        return sum(loss, axis=-1, keepdims=False)
    

class GaussianNLL(Loss):
    """Gaussian Negative Log Likelihood loss."""
    def __init__(self, eps: float = 1e-7):
        """
        @param eps: Small value for numerical stability
        """
        super().__init__()
        self.eps = eps

    def compute(self, z: Tensor, y: Tensor) -> Tensor:
        # NLL = 1/2 (log(σ²) + ((y - μ)²) / σ²)
        mu, log_var = z[..., 0::2], z[..., 1::2]
        variance = exp(log_var) + self.eps
        loss = 0.5 * (log_var + ((y - mu) ** 2) / variance)
        return mean(loss, axis=-1, keepdims=False)


class KLDivergence(Loss):
    """Kullback-Leibler Divergence loss."""
    def __init__(self, eps: float = 1e-7):
        """
        @param eps: Small value for numerical stability
        """
        super().__init__()
        self.eps = eps

    def compute(self, z: Tensor, y: Tensor) -> Tensor:
        # KL(y||z) = Σ y.log(y / z)
        z = where(z > 0, z, self.eps)
        y = where(y > 0, y, self.eps)
        loss = y * log(y / z)
        return sum(loss, axis=-1, keepdims=False)