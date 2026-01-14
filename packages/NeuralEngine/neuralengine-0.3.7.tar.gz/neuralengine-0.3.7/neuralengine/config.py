import numpy as np
from functools import wraps
from inspect import signature
from typing import Any, Literal, get_origin, get_args, get_type_hints

try:
    import cupy as cp
    _has_cuda = cp.cuda.is_available()
except ImportError:
    cp = None
    _has_cuda = False
    print("Cupy is not installed or no CUDA device is available. Falling back to NumPy.")


xp = np # Backend array provider. Default to NumPy
_current_device: Literal['cpu', 'cuda'] = 'cpu' # Default device


class Typed(type):
    """A metaclass for validating data types.
    Add `STRICT = True` in class definition to enforce strict type checking."""
    _enabled: bool = True

    def __new__(cls, name, bases, dct):
        strict = dct.get('STRICT', False)

        for attr, value in dct.items(): # Only validate public methods and properties
            if not attr.startswith('_') or attr in {'__init__', '__call__'}:
                if isinstance(value, property):
                    methods = (cls.validate(m, strict) for m in (value.fget, value.fset, value.fdel))
                    dct[attr] = property(*methods, doc=value.__doc__)
                elif callable(value):
                    dct[attr] = cls.validate(value, strict)
        return super().__new__(cls, name, bases, dct)
    
    @classmethod
    def validation(cls, enabled: bool) -> None:
        """Enables or disables type validation globally.
        @param enabled: If True, enables validation; if False, disables it.
        """
        cls._enabled = enabled
    
    @classmethod
    def validate(cls, func, strict: bool = False):
        """Decorator to validate function arguments based on type hints.
        @param func: The function to validate.
        @param strict: Whether to enforce strict type checking.
        """
        if func is None or not cls._enabled: return func
        sig = signature(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            hints = get_type_hints(func)
            (bound := sig.bind(*args, **kwargs)).apply_defaults()
            for name, val in bound.arguments.items():
                param = sig.parameters[name]
                hint = hints.get(name, param.annotation)
                if hint is param.empty: continue
                # Normalize *args / **kwargs
                val = val if param.kind == param.VAR_POSITIONAL else \
                    val.values() if param.kind == param.VAR_KEYWORD else (val,)    
                  
                if not all(cls._check(v, hint, strict) for v in val):
                    raise TypeError(f"Argument '{name}' expected {hint}, got {type(val).__name__}")

            result = func(*args, **kwargs)
            ret_hint = hints.get('return', sig.return_annotation)
            if ret_hint is not sig.empty and not cls._check(result, ret_hint, strict):
                raise TypeError(f"Return value expected {ret_hint}, got {type(result).__name__}")
            return result
        return wrapper

    @classmethod
    def _check(cls, val, hint, strict) -> bool:
        """Recursively checks if a value matches a type hint."""
        # Handle Any, None and Optional
        if not hint or hint is Any or (not strict and val is None): return True
        origin, args = get_origin(hint), get_args(hint)

        # Handle Special Forms
        if 'Union' in str(origin): return any(cls._check(val, a, strict) for a in args)
        if 'Literal' in str(origin): return val in args

        if not strict: # Non-strict mode relaxations
            if hint is float and isinstance(val, int): return True
            if origin in (list, set, tuple) and not isinstance(val, (list, set, tuple)):
                return any(cls._check(val, a, strict) for a in args if a is not Ellipsis)

        # Basic type check
        if origin is None: return isinstance(val, hint)
        if not isinstance(val, origin): return False

        # Handle Non-Iterable Generics
        if not args or 'Callable' in str(origin): return True
        if origin is type: return isinstance(val, type) and issubclass(val, args[0])

        # Handle Iterable Generics
        if origin is dict:
            val = [x for pair in val.items() for x in pair] # Flatten dict items
        elif origin is tuple and not Ellipsis in args:
            if len(val) != len(args): return False # Length mismatch

        args = args[:args.index(Ellipsis)] if Ellipsis in args else args
        return all(cls._check(v, args[i % len(args)], strict) for i, v in enumerate(val))


@Typed.validate
def set_device(device: Literal['cpu', 'cuda']) -> None:
    """Sets the current device for tensor operations.
    @param device: The device to set, either 'cpu' or 'cuda'
    """
    global xp, _current_device
    if device == 'cpu':
        xp = np
    elif device == 'cuda':
        if not _has_cuda:
            raise RuntimeError("Cupy is not installed or no CUDA device is available.")
        xp = cp
    _current_device = device


def get_device() -> Literal['cpu', 'cuda']:
    """Returns the current device being used for tensor operations.
    @return: The current device, either 'cpu' or 'cuda'
    """
    return _current_device


class DType():
    """Data types supported by NeuralEngine."""
    FLOAT = xp.floating
    FLOAT16 = xp.float16
    FLOAT32 = xp.float32
    FLOAT64 = xp.float64
    INT = xp.integer
    INT8 = xp.int8
    INT16 = xp.int16
    INT32 = xp.int32
    INT64 = xp.int64
    UINT = xp.unsignedinteger
    UINT8 = xp.uint8
    UINT16 = xp.uint16
    UINT32 = xp.uint32
    UINT64 = xp.uint64
    BOOL = xp.bool_