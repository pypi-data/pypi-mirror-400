import os
import pickle as pkl
from ..config import Typed, DType, get_device
from ..tensor import Tensor, NoGrad
from ..utils import concat
from .layers import Layer, LSTM
from .loss import Loss
from .metrics import Metric
from .optim import Optimizer
from .dataload import DataLoader


class Model(metaclass=Typed):
    """A class to build and train a neural network model.
    Allows for defining the model architecture, optimizer, loss function and metrics.
    The model can be trained and evaluated.
    """
    def __init__(self, input_size: tuple[int, ...] | int, optimizer: Optimizer, loss: Loss, \
                 metrics: list[Loss | Metric] = [], dtype: type = DType.FLOAT32):
        """
        @param input_size: Tuple or int, shape of input data samples (int if 1D).
        @param optimizer: Optimizer instance.
        @param loss: Loss instance.
        @param metrics: List/tuple of Metric or Loss instances.
        @param dtype: Data type for the model parameters.
        """
        self.input_size = input_size
        self.dtype = dtype
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics if isinstance(metrics, list) else [metrics]


    def __call__(self, *layers: Layer) -> None:
        """Allows the model to be called with layers to build the model.
        @param layers: Variable number of Layer instances to add to the model.
        """
        self.build(*layers)


    def build(self, *layers: Layer) -> None:
        """Builds the model by adding layers.
        @param layers: Variable number of Layer instances to add to the model.
        """
        self.parameters, prev_layer = {}, None
        for i, layer in enumerate(layers):
            layer.dtype = self.dtype

            # If stacking LSTM layers, update input size and output selection
            if isinstance(layer, LSTM) and isinstance(prev_layer, LSTM):
                out_size = prev_layer.out_size
                if prev_layer.attention: out_size += prev_layer.enc_size or out_size
                if prev_layer.bidirectional: out_size *= 2
                self.input_size = (*prev_layer.in_size[:-1], out_size)
                prev_layer.return_seq = True
                if not 0 in prev_layer.use_output:
                    prev_layer.use_output = (0, 1, 2) if prev_layer.return_state else (0,)

            prev_layer = layer
            layer.in_size = layer.in_size or self.input_size
            self.input_size = getattr(layer, 'out_size', self.input_size)

            self.parameters[f"layer_{i}"] = layer.parameters() # Collect parameters from the layer
            
        self.layers = layers
        self.optimizer.parameters = [p for params in self.parameters.values() for p in params] # Flatten lists


    @classmethod
    def load_model(cls, filepath: str) -> 'Model':
        """Loads the model from a file.
        @param filepath: Path to the file from which the model will be loaded.
        @return: Loaded Model instance.
        """
        filepath = filepath if filepath.endswith('.pkl') else filepath + '.pkl'
        with open(filepath, 'rb') as file:
            model = pkl.load(file)

        if not isinstance(model, cls):
            raise ValueError("Loaded object is not a Model instance")

        device = get_device()
        for layer in model.layers:
            layer.to(device)
        return model


    def load_params(self, filepath: str) -> None:
        """Loads the model parameters from a file.
        @param filepath: Path to the file from which model parameters will be loaded.
        """
        filepath = filepath if filepath.endswith('.pkl') else filepath + '.pkl'
        with open(filepath, 'rb') as file:
            saved_params = pkl.load(file)

        device = get_device()
        for i in range(len(self.layers)):
            layer_new = self.parameters.get(f"layer_{i}", [])
            layer_old = saved_params.get(f"layer_{i}", [])

            if len(layer_new) != len(layer_old): 
                print(f"Skipping layer_{i} parameter load due to mismatch.")
                continue

            for p_new, p_old in zip(layer_new, layer_old):
                if p_new.shape != p_old.shape:
                    print(f"Skipping parameter load due to mismatch: {p_new.shape} vs {p_old.shape}")
                    continue 
                p_new.data = p_old.to(device).data.copy() # Load parameter weights


    def save(self, filename: str, weights_only: bool = False) -> None:
        """Saves the model or model parameters to a file.
        @param filename: Name of the file where model will be saved.
        @param weights_only: If True, saves only weights; else saves entire model structure.
        """
        filename = filename if filename.endswith('.pkl') else filename + '.pkl'
        filepath = os.path.join(os.getcwd(), filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True) # Ensure directory exists

        with open(filepath, 'wb') as file:
            if weights_only: pkl.dump(self.parameters, file)
            else: pkl.dump(self, file)


    def train(self, dataloader: DataLoader, epochs: int = 10, patience: int = 0, ckpt_interval: int = 0) -> None:
        """Trains the model on data.
        @param dataloader: DataLoader instance providing training data.
        @param epochs: Number of epochs to train
        @param patience: Early stopping patience (in epochs), saves best weights
        @param ckpt_interval: Interval (in epochs) to save checkpoints
        """
        for layer in self.layers:
            layer.mode = 'train'

        if patience: best = 1e999
        for epoch in dataloader(epochs):

            for batch in dataloader:
                x, y = batch
                # Forward pass
                for layer in self.layers:
                    x = layer(x)
                    # For stacked LSTM, pass outputs accordingly
                    if isinstance(layer, LSTM): x = x[layer.use_output[0]]
                    
                loss = self.loss(x, y) # Compute loss
                loss.backward() # Backward pass

                # Compute metrics
                for metric in self.metrics:
                    metric(x, y)

                # Update parameters
                self.optimizer.step()
                self.optimizer.reset_grad() # Reset gradients

                print(dataloader, end='', flush=True) # Show progress bar

            output_strs = [f"(Train Loss) {self.loss}", *self.metrics] # Prepare epoch summary

            # Validation step
            if dataloader.val_split:
                val_loss = self.eval(dataloader, validate=True) # Evaluate on validation set
                for layer in self.layers: layer.mode = 'train'

                if patience: # Early stopping check
                    if val_loss < best: 
                        best, wait = val_loss, 0
                        self.save("checkpoints/best_model.pkl", weights_only=True)
                    elif (wait := wait + 1) > patience:
                        return print(f"Early stopping at epoch {epoch}. Best model saved.")

            # Save checkpoint
            if ckpt_interval and epoch % ckpt_interval == 0:
                self.save(f"checkpoints/epoch_{epoch}.pkl", weights_only=True)
                output_strs.append("Checkpoint saved")
            print(*output_strs, sep=', ', flush=True) # Print epoch summary


    def eval(self, dataloader: DataLoader, validate: bool = False) -> Tensor | float:
        """Evaluates the model on data.
        @param dataloader: DataLoader instance providing evaluation data.
        @param validate: If True, evaluates on validation set; else on test set.
        @return: Output tensor after evaluation or validation loss if validate is True.
        """
        for layer in self.layers:
            layer.mode = 'eval'

        if not validate: z = []
        for batch in dataloader:
            x, y = batch
            # Forward pass
            with NoGrad():
                for layer in self.layers:
                    x = layer(x)
                    # For stacked LSTM, pass outputs accordingly
                    if isinstance(layer, LSTM): x = x[layer.use_output[0]]

                self.loss(x, y) # Compute loss

            if not validate:
                # Compute metrics
                for metric in self.metrics:
                    metric(x, y)
                z.append(x) # Accumulate outputs

            print(dataloader, end='', flush=True) # Show progress bar

        if validate:
            loss_val = self.loss.loss_val / self.loss.count
            print(f"(Val Loss) {self.loss}", end=', ', flush=True) # Print validation summary
            return loss_val # Return validation loss

        print(f"(Eval Loss) {self.loss}", *self.metrics, sep=', ') # Print evaluation summary
        return concat(*z, axis=0) # Combine outputs and return