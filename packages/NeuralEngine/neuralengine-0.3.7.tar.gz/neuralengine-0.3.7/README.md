<p align="center">
    <img src="https://raw.githubusercontent.com/Prajjwal2404/NeuralEngine/refs/heads/main/NeuralEngine.webp" alt="NeuralEngine Cover" width="600" />
</p>

<p align="center">
    <a href="https://github.com/Prajjwal2404/NeuralEngine/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/Prajjwal2404/NeuralEngine" /></a>
    <a href="https://github.com/Prajjwal2404/NeuralEngine/graphs/contributors" alt="Contributors">
        <img src="https://img.shields.io/github/contributors/Prajjwal2404/NeuralEngine" /></a>
    <a href="https://pypi.org/project/NeuralEngine" alt="PyPI">
        <img src="https://img.shields.io/pypi/v/NeuralEngine?color=brightgreen&label=PyPI" /></a>
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/language-Python-blue">
    </a>
    <a href="mailto:prajjwalpratapshah@outlook.com">
        <img src="https://img.shields.io/badge/-Email-red?style=flat-square&logo=gmail&logoColor=white">
    </a>
    <a href="https://www.linkedin.com/in/prajjwal2404">
        <img src="https://img.shields.io/badge/-Linkedin-blue?style=flat-square&logo=linkedin">
    </a>
</p>


# NeuralEngine

A framework/library for building and training neural networks in Python. NeuralEngine provides core components for constructing, training and evaluating neural networks, with support for both CPU and GPU (CUDA) acceleration. Designed for extensibility, performance and ease of use, it is suitable for research, prototyping and production.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Example Usage](#example-usage)
- [Project Structure](#project-structure)
- [Capabilities & Documentation](#capabilities--documentation)
- [Contribution Guide](#contribution-guide)
- [License](#license)
- [Attribution](#attribution)

## Features
- Custom tensor operations (CPU/GPU support via NumPy and optional CuPy)
- Configurable neural network layers (Linear, Flatten, etc.)
- Built-in dataloaders, loss functions, metrics and optimizers
- Model class for easy training and evaluation
- Device management (CPU/CUDA)
- Utilities for deep learning workflows
- Autograd capabilities using dynamic computational graphs
- Extensible design for custom layers, losses, metrics and optimizers
- Flexible data type configuration and runtime type validation

## Installation
Install via pip:
```bash
pip install NeuralEngine
```
Or clone and install locally:
```bash
pip install .
```

### Optional CUDA Support
To enable GPU acceleration, Install via pip:
```bash
pip install NeuralEngine[cuda]
```
Or install the optional dependency
```bash
pip install cupy-cuda12x
```

## Example Usage
```python
import neuralengine as ne

# Set device ('cpu' or 'cuda')
ne.set_device('cuda')

# Load your dataset (example: MNIST)
(x_train, y_train), (x_test, y_test) = load_mnist_data()

# Preprocess data
x_train, x_test = ne.tensor(x_train), ne.tensor(x_test)
x_train, x_test = ne.normalize(x_train), ne.normalize(x_test)
y_train, y_test = ne.one_hot(y_train), ne.one_hot(y_test)

train_data = ne.DataLoader(x_train, y_train, batch_size=10000, val_split=0.2)
test_data = ne.DataLoader(x_test, y_test, batch_size=10000, shuffle=False)

# Build your model
model = ne.Model(
    input_size=(28, 28),
    optimizer=ne.Adam(),
    loss=ne.CrossEntropy(),
    metrics=ne.ClassificationMetrics(),
    dtype=ne.DType.FLOAT16
)
model(
    ne.Flatten(),
    ne.Linear(64, activation=ne.ReLU()),
    ne.Linear(10, activation=ne.Softmax()),
)

# Train and evaluate
model.train(train_data, epochs=30, patience=3)
result = model.eval(test_data)
```

## Project Structure
```
neuralengine/
    __init__.py
    config.py
    tensor.py
    utils.py
    nn/
        __init__.py
        dataload.py
        layers.py
        loss.py
        metrics.py
        model.py
        optim.py
setup.py
requirements.txt
pyproject.toml
MANIFEST.in
LICENSE
README.md
```

## Capabilities & Documentation
NeuralEngine offers the following core capabilities:

### Device Management
- `ne.set_device('cpu'|'cuda')`: Switch between CPU and GPU (CUDA) for computation.
- `Tensor.to(device)`, `Layer.to(device)`: Move tensors and layers to specified device.

### Tensors & Autograd
- Custom tensor implementation supporting NumPy and CuPy backends.
- Automatic differentiation (autograd) using dynamic computational graphs for backpropagation.
- Supports gradients, data types, parameter updates and custom operations.
- Supported tensor operations:
  - Arithmetic: `+`, `-`, `*`, `/`, `**` (power)
  - Matrix multiplication: `@`
  - Mathematical: `log`, `sqrt`, `exp`, `abs`
  - Reductions: `sum`, `max`, `min`, `mean`, `var`
  - Shape: `transpose`, `reshape`, `concatenate`, `stack`, `slice`, `set_slice`
  - Elementwise: `masked_fill`
  - Comparison: `==`, `!=`, `>`, `>=`, `<`, `<=`
  - Type conversion: `dtype` (get / set)
  - Utility: `zero_grad()` (reset gradients)
  - Autograd: `backward()` (compute gradients for the computation graph)

### Layers
- `ne.Linear(out_size, *in_size, bias=True, activation=None)`: Fully connected layer with optional activation.
- `ne.LSTM(...)`: Long Short-Term Memory layer with options for attention, bidirectionality, sequence/state output. You can build deep LSTM networks by stacking multiple LSTM layers. When building encoder-decoder models, ensure that the hidden units for decoder's first layer is set correctly:
    - For a standard LSTM, the hidden state shape for the last timestep is `(batch, hidden_units)`.
    - For a bidirectional LSTM, the hidden and cell state shape becomes `(batch, hidden_units * 2)`.
    - If attention is enabled, the hidden state shape is `(batch, 2 * hidden_units)` (self-attention), if `enc_size` is provided, the hidden state shape is `(batch, hidden_units + enc_size)` (cross-attention).
    - If LSTM layers require state initializations from prior layers, set the hidden units accordingly to match the output shape of the previous LSTM (including adjustments for bidirectionality and attention).
- `ne.MultiplicativeAttention(units, *in_size)`: Soft attention mechanism for sequence models.
- `ne.MultiHeadAttention(*in_size, num_heads=1)`: Multi-head attention layer for transformer and sequence models.
- `ne.Embedding(embed_size, *vocab_size, timesteps=None)`: Embedding layer for mapping indices to dense vectors, with optional positional encoding.
- `ne.LayerNorm(*num_feat, eps=1e-7)`: Layer normalization for stabilizing training.
- `ne.Dropout(prob=0.5)`: Dropout regularization for reducing overfitting.
- `ne.Flatten()`: Flattens input tensors to 2D (batch, features).
- `ne.Layer.dtype = ne.DType`: Get or set layer parameters data types.
- `ne.Layer.freezed = True|False`: Freeze or unfreeze layer parameters during training.
- All layers inherit from a common base and support extensibility for custom architectures.

### Activations
- `ne.Sigmoid()`: Sigmoid activation function.
- `ne.Tanh()`: Tanh activation function.
- `ne.ReLU(alpha=0, parametric=False)`: ReLU, Leaky ReLU, or Parametric ReLU activation.
- `ne.SiLU(beta=False)`: SiLU (Swish) activation function.
- `ne.Softmax(axis=-1)`: Softmax activation for classification tasks.
- All activations inherit from a common base and support extensibility for custom architectures.

### Loss Functions
- `ne.CrossEntropy(binary=False, eps=1e-7)`: Categorical and binary cross-entropy loss for classification tasks.
- `ne.MSE()`: Mean Squared Error loss for regression.
- `ne.MAE()`: Mean Absolute Error loss for regression.
- `ne.Huber(delta=1.0)`: Huber loss, robust to outliers.
- `ne.GaussianNLL(eps=1e-7)`: Gaussian Negative Log Likelihood loss for probabilistic regression.
- `ne.KLDivergence(eps=1e-7)`: Kullback-Leibler Divergence loss for measuring distribution differences.
- All loss functions inherit from a common base, support autograd and loss accumulation.

### Optimizers
- `ne.Adam(lr=1e-3, betas=(0.9, 0.99), eps=1e-7, reg=0)`: Adam optimizer (switches to RMSProp if only one beta is provided).
- `ne.SGD(lr=1e-2, reg=0, momentum=0, nesterov=False)`: Stochastic Gradient Descent with optional momentum and Nesterov acceleration.
- All optimizers support L2 regularization and gradient reset.

### Metrics
- `ne.ClassificationMetrics(num_classes=None, acc=True, prec=False, rec=False, f1=False, eps=1e-7)`: Computes accuracy, precision, recall and F1 score for classification tasks.
- `ne.RMSE()`: Root Mean Squared Error for regression.
- `ne.R2(eps=1e-7)`: R2 Score for regression.
- `ne.Perplexity(eps=1e-7)`: Perplexity metric for generative models.
- All metrics store results as dictionaries, support batch evaluation and metric accumulation.

### Model API
- `ne.Model(input_size, optimizer, loss, metrics, dtype)`: Create a model specifying input size, optimizer, loss function, metrics and data type for model layers.
- Add layers by calling the model instance: `model(layer1, layer2, ...)` or using `model.build(layer1, layer2, ...)`.
- `model.train(dataloader, epochs=10, patience=0, ckpt_interval=0)`: Train the model on dataset, with support for  metric/loss reporting, early stopping and checkpointing per epoch.
- `model.eval(dataloader, validate=False)`: Evaluate the model on dataset or validation set, disables gradient tracking using `with ne.NoGrad():`, prints loss and metrics and returns output tensor.
- Layers are set to training or evaluation mode automatically during `train` and `eval`.
- `model.save(filename, weights_only=False)`: Save the model architecture or model parameters to a file.
- `model.load_params(filepath)`: Load model parameters from a saved file.
- `ne.Model.load_model(filepath)`: Load a model from a saved file.

### DataLoader
- `ne.DataLoader(x, y, dtype=(None, None), batch_size=32, val_split=0, shuffle=True, random_seed=None, bar_size=30, bar_info='')`: Create a data loader for batching, shuffling and splitting datasets during training and evaluation.
- Supports lists, tuples, numpy arrays, pandas dataframes and tensors as input data.
- Provides batching, shuffling, splitting (train/validation) and progress bar display during iteration.
- Extensible for custom data loading strategies.

### Utilities
- Tensor creation: `tensor(data, requires_grad=False, dtype=None)`, `zeros(*shape)`, `ones(*shape)`, `rand(*shape)`, `randn(*shape, xavier=False)`, `randint(low, high, *shape)` and their `_like` variants for matching shapes.
- Tensor operations: `sum`, `min`, `max`, `argmax`, `mean`, `var`, `log`, `sqrt`, `exp`, `abs`, `concat`, `stack`, `where`, `clip`, `array(data, dtype=None)` for elementwise, reduction and conversion operations.
- Preprocessing: `standardize(tensor)`, `normalize(tensor)`, `one_hot(labels)` for data preprocessing.
- Autograd management: `with NoGrad()` context manager to disable gradient tracking in a block. `@no_grad` decorator to disable gradients for specific functions.

### Type Validation
- `metaclass=ne.Typed`: Metaclass for enforcing type hints on class methods, properties and subclasses. Add `STRICT = True` in class definition to enforce strict type checking.
- `@ne.Typed.validate`: Decorator for validating function arguments and return values based on type hints.
- `ne.Typed.validation(True|False)`: Enable or disable type validation globally.
- Data type enum: `ne.DType.FLOAT32`, `ne.DType.INT8`, `ne.DType.UINT16`, etc.

### Extensibility
NeuralEngine is designed for easy extension and customization:
- **Custom Layers**: Create new layers by inheriting from the `Layer` base class and implementing the `forward(self, x)` method. You can add parameters, initialization logic and custom computations as needed. All built-in layers follow this pattern, making it simple to add your own.
- **Custom Losses**: Define new loss functions by inheriting from the `Loss` base class and implementing the `compute(self, z, y)` method. This allows you to integrate any custom loss logic with autograd support.
- **Custom Optimizers**: Implement new optimization algorithms by inheriting from the `Optimizer` base class and providing your own `step(self)` method. You can manage optimizer state and parameter updates as required.
- **Custom Metrics**: Add new metrics by inheriting from the `Metric` base class and implementing the `compute(self, z, y)` method. This allows you to track any performance measure with metric accumulation.
- **Custom DataLoaders**: Extend the `DataLoader` class to create specialized data loading strategies. Override the `__getitem__` method to define how batches are constructed.
- All core components are modular and can be replaced or extended for research or production use.

## Contribution Guide

NeuralEngine is an open-source project, and I warmly welcome all kinds of contributions whether it's code, documentation, bug reports, feature ideas, or sharing cool examples. If you want to help make NeuralEngine better, you're in the right place!

### How to Contribute
- **Fork the repository** and create a new branch for your feature, fix, or documentation update.
- **Keep it clean and consistent**: Try to follow the existing code style, naming conventions and documentation patterns. Well-commented, readable code is always appreciated!
- **Add tests** for new features or bug fixes if you can.
- **Document your changes**: Update or add docstrings and README sections so others can easily understand your work.
- **Open a pull request** describing what you've changed and why it's awesome.

### What Can You Contribute?
- New layers, loss functions, optimizers, metrics, or utility functions
- Improvements to existing components
- Bug fixes and performance tweaks
- Documentation updates and tutorials
- Example scripts and notebooks
- Feature requests, feedback and ideas

Every contribution is reviewed for quality and consistency, but don't worry—if you have questions or need help, just open an issue or start a discussion. I'm happy to help and love seeing new faces in the community!

Thanks for making NeuralEngine better, together! 🚀

## License
MIT License with attribution clause. See LICENSE file for details.

## Attribution
If you use this project, please credit the original developer: Prajjwal Pratap Shah.

Special thanks to the Autograd Framework From Scratch project by Eduardo Leitão da Cunha Opice Leão, which served as a reference for tensor operations and autograd implementations.