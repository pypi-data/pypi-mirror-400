import neuralengine.config as cf
from ..tensor import Tensor
from ..utils import tensor


class DataLoader(metaclass=cf.Typed):
    """Data loader class for batching, shuffling and splitting data."""
    def __init__(self, x, y, dtype: tuple[type, type] = (cf.DType.FLOAT32, None), batch_size: int = 32, \
                 val_split: float = 0, shuffle: bool = True, random_seed: int = None, bar_size: int = 30, \
                 bar_info: str = ''):
        """
        @param x: Input data (array-like).
        @param y: Target data (array-like).
        @param dtype: Data types for the dataset.
        @param batch_size: Number of samples per batch.
        @param val_split: Fraction of data to use for validation.
        @param shuffle: Whether to shuffle the data at the start of each epoch.
        @param random_seed: Seed for random number generator to ensure reproducibility.
        @param bar_size: Length of the progress bar.
        @param bar_info: Additional info to display with the progress bar.
        """
        dtype = dtype if isinstance(dtype, tuple) else (dtype,)

        self.x = tensor(x, dtype=dtype[0])
        self.y = tensor(y, dtype=dtype[-1])
        self.batch_size = batch_size
        self.val_split = val_split
        self.shuffle = shuffle
        self.num_samples = int(self.x.shape[0])
        self.num_batches = (self.num_samples + batch_size - 1) // batch_size
        self.indices = cf.xp.arange(self.num_samples) # Indices for shuffling
        self.rng = cf.xp.random.RandomState(random_seed) # Random number generator
        self.bar_size = bar_size
        self.bar_info = bar_info
        self.curr_batch = 0 # Initialize batch counter

    def __call__(self, epochs: int = 10) -> range:
        """Sets the number of epochs for progress tracking.
        @param epochs: Total number of epochs.
        @return: Range object for the number of epochs.
        """
        self.epochs = epochs
        self.current_epoch = 1
        return range(1, epochs + 1)

    def __len__(self) -> int:
        """Returns the number of batches per epoch."""
        return int(self.num_batches * (1 - self.val_split))

    def __getitem__(self, index: int | slice) -> tuple[Tensor, Tensor]:
        """Gets a batch of data by index or slice. Override for custom behavior."""
        indices = self.indices[index]
        return self.x[indices], self.y[indices]

    def __iter__(self) -> 'DataLoader':
        """Returns the iterator object."""
        if self.curr_batch == 0:
            self.limit = len(self) # Reset for training set
            if self.shuffle: self.rng.shuffle(self.indices)
        return self

    def __next__(self) -> tuple[Tensor, Tensor]:
        """Returns the next batch of data."""
        if self.curr_batch < self.limit:
            start = self.curr_batch * self.batch_size
            end = min(start + self.batch_size, self.num_samples)
            batch_data = self[start:end]
            self.curr_batch += 1
            return batch_data
        elif self.curr_batch < self.num_batches:
            self.limit = self.num_batches # Switch to validation set
            raise StopIteration
        else:
            self.curr_batch = 0 # Reset for next epoch
            if hasattr(self, 'epochs'): self.current_epoch += 1
            raise StopIteration

    def __repr__(self) -> str:
        """String representation showing progress bar."""
        progress = self.curr_batch / self.num_batches
        fill = int(self.bar_size * progress) # Filled position
        split = int(self.bar_size * (1 - self.val_split)) # Val split position
        bar = f"{'█' * min(fill, split) + '░' * (fill - split) :-<{self.bar_size}}"
        info = self.bar_info + ' ' if self.bar_info else '' # Additional info
        if hasattr(self, 'epochs'): info += f"Epoch {self.current_epoch}/{self.epochs} "
        return f"\r{info}|{bar}| {progress:.0%} "