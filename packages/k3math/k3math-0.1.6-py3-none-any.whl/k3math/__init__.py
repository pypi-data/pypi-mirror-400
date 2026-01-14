from importlib.metadata import version

__version__ = version("k3math")

from .mth import Matrix
from .mth import Polynomial
from .mth import Vector

__all__ = [
    "Vector",
    "Matrix",
    "Polynomial",
]
