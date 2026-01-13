"""
nnmerge - A library to merge multiple neural network models for parallel hyperparameter search
"""

__version__ = "0.1.0"
__all__ = []

from .pytorch import convert_to_multi_model
__all__.append("convert_to_multi_model")


