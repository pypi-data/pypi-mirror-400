"""Plotting helpers for sentiment trajectories."""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..transforms.core import DCTTransform, rolling_mean

NormalizationMode = Literal["range", "zscore"]


def _normalize_signal(
        values: np.ndarray,
        mode: NormalizationMode
) -> np.ndarray:
    """
    Scale a signal using the requested normalization mode.
    """

    data = np.asarray(values, dtype=float)
    if data.size == 0:
        return data
    if mode == "range":
        min_val = data.min()
        max_val = data.max()
        span = max_val - min_val
        if span == 0:
            return np.zeros_like(data)
        return 2 * (data - min_val) / span - 1
    if mode == "zscore":
        std = data.std()
        if std == 0:
            return np.zeros_like(data)
        mean = data.mean()
        return (data - mean) / std
    raise ValueError(f"Unsupported normalization mode: {mode}")


@dataclass(slots=True)
class TrajectoryComponents:
    """
    Container holding raw and smoothed signals.

    Parameters
    ----------
    raw : numpy.ndarray
        Base sentiment signal (typically per sentence or paragraph).
    rolling : numpy.ndarray | None
        Optional rolling-average smoothing of ``raw``.
    dct : numpy.ndarray | None
        Optional discrete cosine transform smoothing of ``raw``.
    """

    raw: np.ndarray
    rolling: np.ndarray | None
    dct: np.ndarray | None


def prepare_trajectory(
    values: Sequence[float],
    *,
    rolling_window: int | None = None,
    dct_transform: DCTTransform | None = None,
    normalize: NormalizationMode | None = "range",
) -> TrajectoryComponents:
    """
    Compute optional smoothing passes for a sentiment signal.

    Parameters
    ----------
    values : Sequence[float]
        Sentiment scores ordered along the narrative timeline.
    rolling_window : int, optional
        Window length for :func:`rolling_mean`. When ``None``, skip.
    dct_transform : DCTTransform, optional
        Transformer that applies DCT smoothing. When ``None``, skip.
        If the transform already has ``scale_range=True`` or
        ``scale_values=True``, the DCT output will not be normalized again
        to avoid double-scaling.
    normalize : {"range", "zscore"}, optional
        Apply scaling to each returned series. ``"range"`` (default)
        rescales to ``[-1, 1]`` while ``"zscore"`` standardizes to zero
        mean and unit variance. Set to ``None`` to leave values untouched.

    Returns
    -------
    TrajectoryComponents
        Container with raw values and any requested smoothing outputs.

    Warnings
    --------
    If both ``normalize`` and ``dct_transform`` with internal scaling are
    provided, the DCT output is not normalized to prevent double-scaling.
    A warning is issued to alert the user.

    Examples
    --------
    >>> from moodswing import prepare_trajectory, DCTTransform
    >>>
    >>> # Basic usage with defaults
    >>> trajectory = prepare_trajectory(
    ...     scores,
    ...     rolling_window=50,
    ...     dct_transform=DCTTransform(low_pass_size=10)
    ... )
    >>>
    >>> # Without normalization (preserve original scale)
    >>> trajectory = prepare_trajectory(
    ...     scores,
    ...     dct_transform=DCTTransform(low_pass_size=5),
    ...     normalize=None
    ... )
    >>>
    >>> # Z-score normalization for statistical comparison
    >>> trajectory = prepare_trajectory(
    ...     scores,
    ...     rolling_window=30,
    ...     normalize="zscore"
    ... )
    """
    data = np.asarray(values, dtype=float)
    rolling = None
    if rolling_window:
        rolling = np.asarray(rolling_mean(data, window=rolling_window))

    dct_values = None
    dct_already_scaled = False
    if dct_transform:
        dct_values = np.asarray(dct_transform.transform(data))
        # Check if DCT transform already applies scaling
        dct_already_scaled = (
            dct_transform.scale_range or dct_transform.scale_values
        )

    if normalize is not None:
        normalized_mode = normalize
        data = _normalize_signal(data, normalized_mode)
        if rolling is not None:
            rolling = _normalize_signal(rolling, normalized_mode)
        if dct_values is not None:
            if dct_already_scaled:
                warnings.warn(
                    f"DCT transform already has scaling enabled "
                    f"(scale_range={dct_transform.scale_range}, "
                    f"scale_values={dct_transform.scale_values}). "
                    f"Skipping additional normalization of DCT output to "
                    f"prevent double-scaling. Raw and rolling components "
                    f"are still normalized.",
                    UserWarning,
                    stacklevel=2
                )
            else:
                dct_values = _normalize_signal(dct_values, normalized_mode)

    return TrajectoryComponents(raw=data, rolling=rolling, dct=dct_values)


def trajectory_to_dataframe(
    trajectory: TrajectoryComponents,
    normalize_position: bool = True,
) -> pd.DataFrame:
    """
    Convert trajectory components to a tidy pandas DataFrame.

    This helper creates a long-format DataFrame suitable for plotting with
    seaborn, plotly, or custom matplotlib code. Each row represents one
    position along one trajectory component.

    Parameters
    ----------
    trajectory : TrajectoryComponents
        The trajectory data to convert.
    normalize_position : bool, optional
        If ``True`` (default), position values are normalized to [0, 1]
        representing relative narrative time. If ``False``, use integer
        indices (0, 1, 2, ...).

    Returns
    -------
    pandas.DataFrame
        Tidy DataFrame with columns:

        - ``position`` : float or int, location along narrative
        - ``component`` : str, one of "raw", "rolling", or "dct"
        - ``value`` : float, sentiment score at this position

    Examples
    --------
    >>> from moodswing import prepare_trajectory, trajectory_to_dataframe
    >>> import matplotlib.pyplot as plt
    >>> import seaborn as sns
    >>>
    >>> # Create trajectory
    >>> trajectory = prepare_trajectory(
    ...     scores,
    ...     rolling_window=50,
    ...     dct_transform=DCTTransform(low_pass_size=10)
    ... )
    >>>
    >>> # Convert to DataFrame
    >>> df = trajectory_to_dataframe(trajectory)
    >>>
    >>> # Plot with seaborn
    >>> sns.lineplot(data=df, x='position', y='value', hue='component')
    >>> plt.show()
    >>>
    >>> # Filter to specific components
    >>> df_smooth = df[df['component'].isin(['rolling', 'dct'])]
    >>> df_smooth.pivot(index='position', columns='component', values='value').plot()  #
    >>>
    >>> # Export for further analysis
    >>> df.to_csv('sentiment_trajectory.csv', index=False)
    """  # noqa: E501
    rows = []

    # Always include raw component
    n_raw = trajectory.raw.size
    positions_raw = np.linspace(0, 1, n_raw) if normalize_position else np.arange(n_raw)  # noqa: E501
    for pos, val in zip(positions_raw, trajectory.raw):
        rows.append({"position": pos, "component": "raw", "value": val})

    # Add rolling if available
    if trajectory.rolling is not None:
        n_roll = trajectory.rolling.size
        positions_roll = np.linspace(0, 1, n_roll) if normalize_position else np.arange(n_roll)  # noqa: E501
        for pos, val in zip(positions_roll, trajectory.rolling):
            rows.append({"position": pos, "component": "rolling", "value": val})  # noqa: E501

    # Add DCT if available
    if trajectory.dct is not None:
        n_dct = trajectory.dct.size
        positions_dct = np.linspace(0, 1, n_dct) if normalize_position else np.arange(n_dct)  # noqa: E501
        for pos, val in zip(positions_dct, trajectory.dct):
            rows.append({"position": pos, "component": "dct", "value": val})

    return pd.DataFrame(rows)


def plot_trajectory(
    trajectory: TrajectoryComponents,
    *,
    title: str = "Sentiment Trajectory",
    legend_loc: str = "upper right",
    colors: dict[str, str] | None = None,
    components: set[str] | list[str] | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """
    Render a sentiment trajectory with optional overlays.

    Parameters
    ----------
    trajectory : TrajectoryComponents
        Raw and smoothed signals (as returned by :func:`prepare_trajectory`).
    title : str, optional
        Matplotlib axes title.
    legend_loc : str, optional
        Legend placement passed to :meth:`matplotlib.axes.Axes.legend`.
    colors : dict[str, str], optional
        Custom colors for plot components. Keys can be ``"raw"``,
        ``"rolling"``, and/or ``"dct"``. Defaults to grey, blue, and red
        respectively if not specified.
    components : set[str] | list[str], optional
        Which components to display. Can include ``"raw"``, ``"rolling"``,
        and/or ``"dct"``. If ``None`` (default), all available components
        are shown. Use this to reduce visual clutter by showing only
        specific trajectories.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on. Defaults to ``plt.gca()``.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the plotted trajectory.

    Examples
    --------
    >>> # Use custom colors
    >>> plot_trajectory(
    ...     trajectory,
    ...     colors={"raw": "lightgray", "rolling": "green", "dct": "purple"}
    ... )
    >>>
    >>> # Show only the DCT smoothed line
    >>> plot_trajectory(trajectory, components=["dct"])
    >>>
    >>> # Custom figure size with specific components
    >>> fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    >>> plot_trajectory(trajectory, components=["rolling", "dct"], ax=ax)
    """
    ax = ax or plt.gca()

    # Set default colors
    default_colors = {"raw": "grey", "rolling": "blue", "dct": "red"}
    if colors is not None:
        default_colors.update(colors)

    # Determine which components to show
    show_components = set(components) if components is not None else {"raw", "rolling", "dct"}  # noqa: E501

    if "raw" in show_components:
        x_raw = np.linspace(0, 1, num=trajectory.raw.size)
        ax.plot(
            x_raw,
            trajectory.raw,
            label="Raw",
            color=default_colors["raw"],
            alpha=0.5
        )
    if "rolling" in show_components and trajectory.rolling is not None:
        x_roll = np.linspace(0, 1, num=trajectory.rolling.size)
        ax.plot(
            x_roll,
            trajectory.rolling,
            label="Rolling Mean",
            color=default_colors["rolling"]
        )
    if "dct" in show_components and trajectory.dct is not None:
        x_dct = np.linspace(0, 1, num=trajectory.dct.size)
        ax.plot(
            x_dct,
            trajectory.dct,
            label="DCT Smooth",
            color=default_colors["dct"]
        )
    ax.axhline(0, color="black", linewidth=0.5, linestyle="--")
    ax.set_xlabel("Narrative Time")
    ax.set_ylabel("Sentiment")
    ax.set_title(title)
    ax.legend(loc=legend_loc)
    return ax
