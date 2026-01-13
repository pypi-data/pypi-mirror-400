"""Transform helpers for sentiment trajectories."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np


@dataclass(slots=True)
class DCTTransform:
    """
    Compute a low-pass discrete cosine transform.

    Parameters
    ----------
    low_pass_size : int, optional
        Number of DCT frequency components to retain. Lower values produce
        smoother curves. Defaults to 5.

        - 2-5: Very smooth, broad narrative patterns only
        - 5-10: Balanced smoothing (recommended for most uses)
        - 10-20: Preserves more detail, shows secondary peaks
        - >20: Minimal smoothing, may retain noise

    output_length : int, optional
        Number of points in the interpolated output. Defaults to 100.
        Common values: 100-200 for visualization, 1000+ for analysis.

    scale_range : bool, optional
        When ``True``, rescale output to [-1, 1]. Mutually exclusive
        with ``scale_values``. Use for comparing texts on a common scale.

    scale_values : bool, optional
        When ``True``, standardize output (mean=0, std=1). Mutually
        exclusive with ``scale_range``. Use for statistical analysis.

    Examples
    --------
    >>> # Smooth smoothing for broad patterns
    >>> dct_smooth = DCTTransform(low_pass_size=5, output_length=100)
    >>> smoothed = dct_smooth.transform(raw_scores)
    >>>
    >>> # More detail, normalized range
    >>> dct_detailed = DCTTransform(
    ...     low_pass_size=15,
    ...     output_length=200,
    ...     scale_range=True
    ... )
    >>>
    >>> # For statistical comparison across texts
    >>> dct_stats = DCTTransform(scale_values=True)

    Notes
    -----
    You cannot set both ``scale_range`` and ``scale_values`` to ``True``.
    Choose one based on your use case:

    - Use ``scale_range=True`` for visualization and direct comparison
    - Use ``scale_values=True`` for statistical analysis
    - Use neither for preserving original scale
    """

    low_pass_size: int = 5
    output_length: int = 100
    scale_range: bool = False
    scale_values: bool = False

    def __post_init__(self) -> None:
        if self.scale_range and self.scale_values:
            raise ValueError(
                "scale_range and scale_values cannot both be True"
                )
        if self.low_pass_size <= 0:
            raise ValueError(
                "low_pass_size must be positive"
                )
        if self.output_length <= 0:
            raise ValueError(
                "output_length must be positive"
                )

    def transform(
            self,
            values: Iterable[float]
    ) -> List[float]:
        data = np.asarray(list(values), dtype=float)
        if data.size == 0:
            return []
        if self.low_pass_size > data.size:
            raise ValueError(
                "low_pass_size cannot exceed input length"
                )
        if self.low_pass_size > self.output_length:
            raise ValueError(
                "low_pass_size cannot exceed output length"
                )

        coefficients = _dct_type_ii(data)
        keepers = coefficients[: self.low_pass_size]
        padding = self.output_length - keepers.size
        if padding < 0:
            raise ValueError(
                "output length must be at least low_pass_size"
                )
        padded = np.concatenate(
            [keepers, np.zeros(padding, dtype=coefficients.dtype)]
        )
        result = _dct_type_iii(padded)
        if self.scale_values:
            result = (result - result.mean()) / (result.std() or 1)
        if self.scale_range:
            min_val = result.min()
            max_val = result.max()
            if max_val - min_val > 0:
                result = 2 * (result - min_val) / (max_val - min_val) - 1
        return result.tolist()


def rolling_mean(
        values: Iterable[float],
        window: int
) -> List[float]:
    """
    Compute a rolling (moving) average over a sequence of values.

    Parameters
    ----------
    values : Iterable[float]
        Input sequence to smooth.
    window : int
        Number of points to average over. Must be positive.

    Returns
    -------
    list[float]
        Smoothed sequence with the same length as input.

    Notes
    -----
    This function uses ``mode="same"`` convolution, which means:

    - Output has the same length as input
    - Edge values (first and last ``window//2`` points) are averaged
      over fewer points than the window size, using only available data
    - This prevents shrinkage but means edges are less smoothed

    For example, with ``window=5``, the first point averages over just
    itself plus the next 2 points, while interior points average over
    5 points centered on the current position.

    Examples
    --------
    >>> scores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> smoothed = rolling_mean(scores, window=3)
    >>> # First value: avg of [1, 2] (only 2 points available)
    >>> # Fifth value: avg of [4, 5, 6] (full 3-point window)
    """
    data = np.asarray(list(values), dtype=float)
    if data.size == 0:
        return []
    if window <= 0:
        raise ValueError("window must be positive")
    if window > data.size:
        window = data.size
    weights = np.ones(window)
    sums = np.convolve(data, weights, mode="same")
    counts = np.convolve(np.ones_like(data), weights, mode="same")
    result = sums / counts
    return result.tolist()


def _dct_type_ii(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    n = data.shape[-1]
    if n == 0:
        return np.array([], dtype=float)
    extended = np.concatenate([data, data[::-1]])
    spectrum = np.fft.rfft(extended)[:n]
    phase = np.exp(-1j * np.pi * np.arange(n) / (2 * n))
    return np.real(phase * spectrum)


def _dct_type_iii(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    n = data.shape[-1]
    if n == 0:
        return np.array([], dtype=float)
    phase = np.exp(-1j * np.pi * np.arange(n) / (2 * n))
    spectrum = np.zeros(n + 1, dtype=complex)
    spectrum[:n] = data * np.conj(phase)
    extended = np.fft.irfft(spectrum, n=2 * n)
    return (2 * n) * extended[:n]
