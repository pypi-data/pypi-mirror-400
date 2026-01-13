"""Signal processing helpers exposed at package import time."""

from .core import DCTTransform, rolling_mean

__all__ = ["DCTTransform", "rolling_mean"]
