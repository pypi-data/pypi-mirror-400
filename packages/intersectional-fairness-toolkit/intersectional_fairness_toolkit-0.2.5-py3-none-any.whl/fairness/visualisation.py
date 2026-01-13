"""
Visualization helpers for fairness metrics.

This module contains lightweight plotting utilities that sit on top of the
`fairness.metrics` and `fairness.single_metrics` APIs. The functions do not
compute metrics themselves; they only visualize metric outputs computed from
group labels, predictions, and ground-truth labels.

The typical workflow is:
1) Prepare evaluation inputs (see `fairness.groups.make_eval_df` and
   `fairness.adapters`).
2) Compute or select a metric function from `fairness.metrics` or
   `fairness.single_metrics`.
3) Use the plotting helpers here to visualize metric values across groups.

All plotting helpers return a Matplotlib `Figure` so callers can further
customize or save the plots as needed.
"""

from __future__ import annotations

from typing import Callable, Iterable, Mapping, Optional, Sequence, Tuple
import itertools

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import single_metrics


def _to_list(values: Iterable) -> list:
    """
    Materialize an iterable as a list.

    Parameters
    ----------
    values : Iterable
        Any iterable object.

    Returns
    -------
    list
        List with the same elements as `values`.
    """
    return list(values)


def _unique_in_order(values: Iterable) -> list:
    """
    Return unique values while preserving the original order.

    Parameters
    ----------
    values : Iterable
        Input sequence.

    Returns
    -------
    list
        Unique values in first-seen order.
    """
    return list(dict.fromkeys(values))


def _require_equal_lengths(*values: Iterable, names: Sequence[str]) -> None:
    """
    Validate that all provided iterables have the same length.

    Parameters
    ----------
    *values : Iterable
        The sequences to check.
    names : Sequence[str]
        Names for the sequences, used in error messages.

    Raises
    ------
    ValueError
        If any input lengths are not identical.
    """
    lengths = [len(v) for v in values]
    if len(set(lengths)) != 1:
        pairs = ", ".join(f"{name}={length}" for name, length in zip(names, lengths))
        raise ValueError(f"Inputs must have the same length. Got {pairs}")


def _default_figsize(n: int, *, horizontal: bool) -> Tuple[float, float]:
    """
    Compute a reasonable default figure size for bar plots.

    Parameters
    ----------
    n : int
        Number of plotted categories.
    horizontal : bool
        If True, size is adapted for horizontal bar plots.

    Returns
    -------
    tuple[float, float]
        (width, height) in inches.
    """
    if horizontal:
        return (8.0, max(3.5, 0.35 * n))
    return (max(6.0, 0.7 * n), 4.5)


def _bar_plot(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    title: Optional[str],
    xlabel: str,
    ylabel: str,
    rotation: int,
    figsize: Optional[Tuple[float, float]],
    horizontal: bool,
) -> plt.Figure:
    """
    Draw a simple bar or horizontal bar plot.

    Parameters
    ----------
    labels : Sequence[str]
        Category labels.
    values : Sequence[float]
        Numeric values corresponding to labels.
    title : str or None
        Figure title. If None, no title is set.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    rotation : int
        Rotation angle for x tick labels (horizontal plots ignore this).
    figsize : tuple[float, float] or None
        Figure size in inches. If None, a default size is chosen.
    horizontal : bool
        If True, plot horizontal bars.

    Returns
    -------
    matplotlib.figure.Figure
        The created Matplotlib figure.
    """
    if figsize is None:
        figsize = _default_figsize(len(labels), horizontal=horizontal)

    fig, ax = plt.subplots(figsize=figsize)
    if horizontal:
        ax.barh(labels, values)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    else:
        ax.bar(labels, values)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=rotation)

    if title:
        ax.set_title(title)

    fig.tight_layout()
    return fig


def plot_group_metric(
    metric_fn: Callable[[object, list, list, list], float],
    subject_labels: Iterable,
    predictions: Iterable,
    true_statuses: Iterable,
    *,
    groups: Optional[Sequence] = None,
    title: Optional[str] = None,
    rotation: int = 45,
    figsize: Optional[Tuple[float, float]] = None,
    sort: bool = False,
) -> plt.Figure:
    """
    Plot a group-level metric computed with `fairness.metrics` (group_*).

    This function expects a metric that takes a single group label, a list
    of subject labels, predictions, and true labels, and returns a scalar
    value for that group (e.g., `group_acc`, `group_fnr`, `group_fpr`).

    Parameters
    ----------
    metric_fn : callable
        A function from `fairness.metrics` with signature:
        (group_label, subject_labels, predictions, true_statuses) -> float.
    subject_labels : Iterable
        Group label for each sample (e.g., intersectional labels).
    predictions : Iterable
        Predicted labels aligned with `subject_labels`.
    true_statuses : Iterable
        Ground-truth labels aligned with `subject_labels`.
    groups : Sequence or None, optional
        Subset/ordering of groups to plot. If None, all unique labels are used.
    title : str or None, optional
        Plot title. Defaults to the metric function name.
    rotation : int, optional
        Rotation angle for x tick labels.
    figsize : tuple[float, float] or None, optional
        Figure size in inches. If None, a default size is chosen.
    sort : bool, optional
        If True, sort bars by metric value (NaNs placed at the end).

    Returns
    -------
    matplotlib.figure.Figure
        The created Matplotlib figure.

    Raises
    ------
    ValueError
        If inputs do not share the same length.
    """
    subject_labels = _to_list(subject_labels)
    predictions = _to_list(predictions)
    true_statuses = _to_list(true_statuses)

    _require_equal_lengths(
        subject_labels, predictions, true_statuses,
        names=("subject_labels", "predictions", "true_statuses"),
    )

    if groups is None:
        groups = _unique_in_order(subject_labels)
    groups = list(groups)

    values = [metric_fn(g, subject_labels, predictions, true_statuses) for g in groups]
    labels = [str(g) for g in groups]

    if sort:
        order = np.argsort(np.nan_to_num(values, nan=np.inf))
        labels = [labels[i] for i in order]
        values = [values[i] for i in order]

    if title is None:
        title = metric_fn.__name__.replace("_", " ")

    return _bar_plot(
        labels,
        values,
        title=title,
        xlabel="group",
        ylabel="metric value",
        rotation=rotation,
        figsize=figsize,
        horizontal=False,
    )


def plot_group_metric_from_eval_df(
    metric_fn: Callable[[object, list, list, list], float],
    eval_df: pd.DataFrame,
    *,
    label_col: str = "subject_label",
    title: Optional[str] = None,
    rotation: int = 45,
    figsize: Optional[Tuple[float, float]] = None,
    sort: bool = False,
) -> plt.Figure:
    """
    Convenience wrapper for an eval_df produced by `fairness.groups.make_eval_df`.

    Parameters
    ----------
    metric_fn : callable
        A `fairness.metrics` group_* function.
    eval_df : pandas.DataFrame
        DataFrame with columns `label_col`, `y_pred`, and `y_true`.
    label_col : str, optional
        Column name for group labels (default "subject_label").
    title : str or None, optional
        Plot title.
    rotation : int, optional
        Rotation angle for x tick labels.
    figsize : tuple[float, float] or None, optional
        Figure size in inches.
    sort : bool, optional
        If True, sort bars by metric value (NaNs placed at the end).

    Returns
    -------
    matplotlib.figure.Figure
        The created Matplotlib figure.

    Raises
    ------
    ValueError
        If required columns are missing from eval_df.
    """
    if label_col not in eval_df.columns:
        raise ValueError(f"eval_df missing '{label_col}' column.")
    for col in ("y_pred", "y_true"):
        if col not in eval_df.columns:
            raise ValueError(f"eval_df missing '{col}' column.")

    subject_labels = eval_df[label_col].tolist()
    predictions = eval_df["y_pred"].tolist()
    true_statuses = eval_df["y_true"].tolist()

    return plot_group_metric(
        metric_fn,
        subject_labels,
        predictions,
        true_statuses,
        title=title,
        rotation=rotation,
        figsize=figsize,
        sort=sort,
    )


def plot_pairwise_group_metric(
    metric_fn: Callable[[object, object, list, list, list], float],
    subject_labels: Iterable,
    predictions: Iterable,
    true_statuses: Iterable,
    *,
    group_pairs: Optional[Sequence[Tuple[object, object]]] = None,
    title: Optional[str] = None,
    rotation: int = 45,
    figsize: Optional[Tuple[float, float]] = None,
    sort: bool = True,
) -> plt.Figure:
    """
    Plot pairwise group metrics (group_*_diff, group_*_ratio).

    Pairwise metric functions compare two groups at a time and return a
    scalar (e.g., difference or ratio of accuracies).

    Parameters
    ----------
    metric_fn : callable
        A function from `fairness.metrics` with signature:
        (group_a, group_b, subject_labels, predictions, true_statuses) -> float.
    subject_labels : Iterable
        Group label for each sample.
    predictions : Iterable
        Predicted labels aligned with `subject_labels`.
    true_statuses : Iterable
        Ground-truth labels aligned with `subject_labels`.
    group_pairs : Sequence[tuple] or None, optional
        Explicit list of (group_a, group_b) pairs to plot. If None, all
        pairwise combinations of unique groups are used.
    title : str or None, optional
        Plot title. Defaults to the metric function name.
    rotation : int, optional
        Rotation angle for x tick labels (used for vertical plots only).
    figsize : tuple[float, float] or None, optional
        Figure size in inches.
    sort : bool, optional
        If True, sort bars by metric value (NaNs placed at the end).

    Returns
    -------
    matplotlib.figure.Figure
        The created Matplotlib figure.

    Raises
    ------
    ValueError
        If no group pairs are provided or generated.
    """
    subject_labels = _to_list(subject_labels)
    predictions = _to_list(predictions)
    true_statuses = _to_list(true_statuses)

    _require_equal_lengths(
        subject_labels, predictions, true_statuses,
        names=("subject_labels", "predictions", "true_statuses"),
    )

    if group_pairs is None:
        groups = _unique_in_order(subject_labels)
        group_pairs = list(itertools.combinations(groups, 2))

    if not group_pairs:
        raise ValueError("No group pairs provided to plot.")

    labels = []
    values = []
    for a, b in group_pairs:
        labels.append(f"{a} vs {b}")
        values.append(metric_fn(a, b, subject_labels, predictions, true_statuses))

    if sort:
        order = np.argsort(np.nan_to_num(values, nan=np.inf))
        labels = [labels[i] for i in order]
        values = [values[i] for i in order]

    if title is None:
        title = metric_fn.__name__.replace("_", " ")

    return _bar_plot(
        labels,
        values,
        title=title,
        xlabel="group pair",
        ylabel="metric value",
        rotation=rotation,
        figsize=figsize,
        horizontal=True,
    )


def plot_intersectional_metric(
    metric_fn: Callable[[dict, list, list], dict],
    subject_labels_dict: Mapping[str, Sequence],
    predictions: Iterable,
    true_statuses: Iterable,
    *,
    title: Optional[str] = None,
    rotation: int = 0,
    figsize: Optional[Tuple[float, float]] = None,
    sort: bool = True,
) -> plt.Figure:
    """
    Plot an all_intersect_* metric from `fairness.metrics` (dict -> bar plot).

    Functions such as `all_intersect_accs`, `all_intersect_fprs`, etc. return
    a dictionary mapping intersectional group labels to metric values. This
    helper converts that dictionary into a horizontal bar plot.

    Parameters
    ----------
    metric_fn : callable
        An `all_intersect_*` function with signature:
        (subject_labels_dict, predictions, true_statuses) -> dict.
    subject_labels_dict : Mapping[str, Sequence]
        Mapping from protected attribute name to labels per sample.
    predictions : Iterable
        Predicted labels aligned with `subject_labels_dict` values.
    true_statuses : Iterable
        Ground-truth labels aligned with `subject_labels_dict` values.
    title : str or None, optional
        Plot title. Defaults to the metric function name.
    rotation : int, optional
        Rotation angle for tick labels.
    figsize : tuple[float, float] or None, optional
        Figure size in inches.
    sort : bool, optional
        If True, sort bars by metric value (NaNs placed at the end).

    Returns
    -------
    matplotlib.figure.Figure
        The created Matplotlib figure.

    Raises
    ------
    ValueError
        If predictions and true_statuses lengths differ.
    TypeError
        If metric_fn does not return a dictionary.
    """
    predictions = _to_list(predictions)
    true_statuses = _to_list(true_statuses)
    _require_equal_lengths(
        predictions, true_statuses,
        names=("predictions", "true_statuses"),
    )

    result = metric_fn(dict(subject_labels_dict), predictions, true_statuses)
    if not isinstance(result, dict):
        raise TypeError("metric_fn must return a dict of intersectional scores.")

    labels = list(result.keys())
    values = list(result.values())

    if sort:
        order = np.argsort(np.nan_to_num(values, nan=np.inf))
        labels = [labels[i] for i in order]
        values = [values[i] for i in order]

    if title is None:
        title = metric_fn.__name__.replace("_", " ")

    return _bar_plot(
        labels,
        values,
        title=title,
        xlabel="metric value",
        ylabel="intersectional group",
        rotation=rotation,
        figsize=figsize,
        horizontal=True,
    )


def plot_scalar_metrics(
    metrics: Mapping[str, float],
    *,
    title: Optional[str] = None,
    rotation: int = 0,
    figsize: Optional[Tuple[float, float]] = None,
) -> plt.Figure:
    """
    Plot one or more scalar metrics (e.g., max_intersect_* outputs).

    Parameters
    ----------
    metrics : Mapping[str, float]
        Mapping from metric name to scalar value.
    title : str or None, optional
        Plot title.
    rotation : int, optional
        Rotation angle for x tick labels.
    figsize : tuple[float, float] or None, optional
        Figure size in inches.

    Returns
    -------
    matplotlib.figure.Figure
        The created Matplotlib figure.
    """
    labels = list(metrics.keys())
    values = list(metrics.values())

    if title is None:
        title = "Scalar metrics"

    return _bar_plot(
        labels,
        values,
        title=title,
        xlabel="metric",
        ylabel="value",
        rotation=rotation,
        figsize=figsize,
        horizontal=False,
    )


_SINGLE_METRICS = {
    "EOD": lambda y_test, y_pred, group_labels, privileged_label: (
        single_metrics.calculate_EOD(y_test, y_pred, group_labels, privileged_label)
    ),
    "AOD": lambda y_test, y_pred, group_labels, privileged_label: (
        single_metrics.calculate_AOD(y_test, y_pred, group_labels, privileged_label)
    ),
    "DI": lambda y_test, y_pred, group_labels, privileged_label: (
        single_metrics.calculate_DI(y_pred, group_labels, privileged_label)
    ),
}


def plot_single_metrics(
    y_test: Iterable,
    y_pred: Iterable,
    group_labels: Iterable,
    privileged_label: object,
    *,
    metrics: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    rotation: int = 0,
    figsize: Optional[Tuple[float, float]] = None,
) -> plt.Figure:
    """
    Plot single-attribute fairness metrics from `fairness.single_metrics`.

    This helper computes and visualizes metrics such as EOD, AOD, and DI for
    a single protected attribute with a specified privileged group. Note that
    DI uses only predictions, while EOD and AOD require y_test.

    Parameters
    ----------
    y_test : Iterable
        Ground-truth binary labels (0/1).
    y_pred : Iterable
        Predicted binary labels (0/1).
    group_labels : Iterable
        Protected attribute labels aligned to y_test/y_pred.
    privileged_label : object
        Label treated as the privileged group.
    metrics : Sequence[str] or None, optional
        Subset of {"EOD", "AOD", "DI"} to compute. Defaults to all.
    title : str or None, optional
        Plot title.
    rotation : int, optional
        Rotation angle for x tick labels.
    figsize : tuple[float, float] or None, optional
        Figure size in inches.

    Returns
    -------
    matplotlib.figure.Figure
        The created Matplotlib figure.

    Raises
    ------
    ValueError
        If an unknown metric name is requested.
    """
    y_test = _to_list(y_test)
    y_pred = _to_list(y_pred)
    group_labels = _to_list(group_labels)
    _require_equal_lengths(
        y_test, y_pred, group_labels,
        names=("y_test", "y_pred", "group_labels"),
    )

    if metrics is None:
        metrics = list(_SINGLE_METRICS.keys())

    values = {}
    for name in metrics:
        if name not in _SINGLE_METRICS:
            raise ValueError(
                f"Unknown metric '{name}'. Supported: {sorted(_SINGLE_METRICS.keys())}"
            )
        fn = _SINGLE_METRICS[name]
        values[name] = fn(y_test, y_pred, group_labels, privileged_label)

    if title is None:
        title = "Single-attribute fairness metrics"

    return plot_scalar_metrics(
        values,
        title=title,
        rotation=rotation,
        figsize=figsize,
    )
