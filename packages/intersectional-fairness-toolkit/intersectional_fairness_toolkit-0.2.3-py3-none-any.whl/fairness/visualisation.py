from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# Validation helpers
# =========================

def _require_df(name: str, df: object) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas.DataFrame, got {type(df)}")
    return df


def _require_multiindex(df: pd.DataFrame, names: Sequence[str], df_name: str) -> None:
    if not isinstance(df.index, pd.MultiIndex):
        raise ValueError(f"{df_name} must have a MultiIndex with names {list(names)}.")
    idx_names = list(df.index.names)
    if idx_names != list(names):
        raise ValueError(f"{df_name} index names must be {list(names)}, got {idx_names}.")


def _require_cols(df: pd.DataFrame, cols: Sequence[str], df_name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{df_name} missing required columns: {missing}. Present: {list(df.columns)}")


def _as_str_list(x: Iterable) -> list[str]:
    return [str(v) for v in x]


def _pick_metrics(df: pd.DataFrame, metrics: Optional[Sequence[str]]) -> list[str]:
    if metrics is None:
        # default: all float-ish columns except 'n'
        candidates = [c for c in df.columns if c != "n"]
        numeric = []
        for c in candidates:
            if pd.api.types.is_numeric_dtype(df[c]):
                numeric.append(c)
        if not numeric:
            raise ValueError("No numeric metric columns found to plot.")
        return numeric

    metrics = list(metrics)
    missing = [m for m in metrics if m not in df.columns]
    if missing:
        raise ValueError(f"Requested metrics not found: {missing}. Available: {list(df.columns)}")
    return metrics


# =========================
# Visualization API
# =========================

@dataclass
class Plotter:
    """
    Visualization-only plotter.

    Expects (imaginary) precomputed outputs:
      - by_group_df: MultiIndex (feature, group), columns ['n', metrics...]
      - confusion_df: MultiIndex (feature, group), columns ['tp','tn','fp','fn'] (optional)
      - threshold_df: MultiIndex (feature, group, threshold), columns [metrics...] (optional)
      - models_df: columns ['model', perf_metric, fairness_metric] (optional)
    """

    # --- Core plots ---

    def metrics_bars(
        self,
        by_group_df: pd.DataFrame,
        feature: str,
        metrics: Optional[Sequence[str]] = None,
        sort_groups: bool = False,
        rotation: int = 45,
        figsize: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
    ) -> plt.Figure:
        """
        Bar chart: for one sensitive feature, plot selected metrics across groups
        as small multiples (one subplot per metric).
        """
        by_group_df = _require_df("by_group_df", by_group_df)
        _require_multiindex(by_group_df, ["feature", "group"], "by_group_df")
        _require_cols(by_group_df, ["n"], "by_group_df")

        # slice the feature
        if feature not in by_group_df.index.get_level_values("feature"):
            feats = sorted(set(_as_str_list(by_group_df.index.get_level_values("feature"))))
            raise ValueError(f"feature='{feature}' not found. Available features: {feats}")

        df = by_group_df.xs(feature, level="feature").copy()  # index now = group
        df.index = df.index.astype(str)

        metric_cols = _pick_metrics(df, metrics)

        if sort_groups:
            df = df.sort_index()

        n_metrics = len(metric_cols)
        cols = min(3, n_metrics)
        rows = int(np.ceil(n_metrics / cols))

        if figsize is None:
            figsize = (4.5 * cols, 3.2 * rows)

        fig, axes = plt.subplots(rows, cols, figsize=figsize, squeeze=False)
        axes = axes.ravel()

        groups = df.index.tolist()
        for i, m in enumerate(metric_cols):
            ax = axes[i]
            ax.bar(groups, df[m].astype(float).values)
            ax.set_title(m)
            ax.tick_params(axis="x", rotation=rotation)
            ax.set_xlabel("group")
            ax.set_ylabel(m)

        for j in range(n_metrics, len(axes)):
            axes[j].axis("off")

        if title is None:
            title = f"Metrics by group: {feature}"
        fig.suptitle(title)
        fig.tight_layout()
        return fig

    def disparity(
        self,
        by_group_df: pd.DataFrame,
        feature: str,
        metric: str,
        ref_group: Union[str, int, float],
        mode: str = "ratio",     # "ratio" or "diff"
        epsilon: Optional[float] = 0.8,
        figsize: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
    ) -> plt.Figure:
        """
        Disparity plot vs reference group:
          - mode='ratio' : metric(group) / metric(ref)
          - mode='diff'  : metric(group) - metric(ref)

        epsilon:
          - if mode='ratio' and epsilon is not None, draws lines at [epsilon, 1/epsilon]
          - if mode='diff', draws line at 0
        """
        by_group_df = _require_df("by_group_df", by_group_df)
        _require_multiindex(by_group_df, ["feature", "group"], "by_group_df")
        _require_cols(by_group_df, ["n", metric], "by_group_df")

        if feature not in by_group_df.index.get_level_values("feature"):
            feats = sorted(set(_as_str_list(by_group_df.index.get_level_values("feature"))))
            raise ValueError(f"feature='{feature}' not found. Available features: {feats}")

        df = by_group_df.xs(feature, level="feature").copy()  # index=group
        df.index = df.index.astype(str)

        ref_group_str = str(ref_group)
        if ref_group_str not in df.index:
            raise ValueError(f"ref_group='{ref_group_str}' not found in groups: {sorted(df.index.tolist())}")

        vals = df[metric].astype(float)
        ref_val = float(vals.loc[ref_group_str])

        if mode not in ("ratio", "diff"):
            raise ValueError("mode must be 'ratio' or 'diff'")

        if mode == "ratio":
            if ref_val == 0:
                score = pd.Series(np.nan, index=vals.index)
            else:
                score = vals / ref_val
            xlabel = f"{metric} / {metric}({ref_group_str})"
            center_line = 1.0
        else:
            score = vals - ref_val
            xlabel = f"{metric} - {metric}({ref_group_str})"
            center_line = 0.0

        score = score.sort_values()  # horizontal bar: sorted for readability

        if figsize is None:
            figsize = (7.5, max(3.0, 0.35 * len(score)))

        fig, ax = plt.subplots(figsize=figsize)
        ax.barh(score.index.tolist(), score.values)

        ax.axvline(center_line, linestyle="--", linewidth=1)
        if mode == "ratio" and epsilon is not None:
            if epsilon <= 0:
                raise ValueError("epsilon must be > 0 for ratio mode.")
            ax.axvline(float(epsilon), linestyle=":", linewidth=1)
            ax.axvline(float(1.0 / epsilon), linestyle=":", linewidth=1)

        ax.set_xlabel(xlabel)
        ax.set_ylabel("group")

        if title is None:
            title = f"Disparity ({mode}) for '{metric}' by {feature} (ref: {ref_group_str})"
        ax.set_title(title)

        fig.tight_layout()
        return fig

    def error_breakdown(
        self,
        confusion_df: pd.DataFrame,
        feature: str,
        normalize: bool = True,
        figsize: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
        rotation: int = 45,
    ) -> plt.Figure:
        """
        Stacked bars by group:
          - FP and FN are the most common error breakdown
        normalize=True:
          - plots rates: fp/(fp+tn) and fn/(fn+tp) are NOT directly comparable,
            so instead we show fp and fn as shares of total errors (fp+fn).
        normalize=False:
          - plots raw counts fp and fn stacked.
        """
        confusion_df = _require_df("confusion_df", confusion_df)
        _require_multiindex(confusion_df, ["feature", "group"], "confusion_df")
        _require_cols(confusion_df, ["tp", "tn", "fp", "fn"], "confusion_df")

        if feature not in confusion_df.index.get_level_values("feature"):
            feats = sorted(set(_as_str_list(confusion_df.index.get_level_values("feature"))))
            raise ValueError(f"feature='{feature}' not found. Available features: {feats}")

        df = confusion_df.xs(feature, level="feature").copy()
        df.index = df.index.astype(str)

        fp = df["fp"].astype(float)
        fn = df["fn"].astype(float)

        if normalize:
            denom = (fp + fn)
            fp_plot = fp / denom.replace(0, np.nan)
            fn_plot = fn / denom.replace(0, np.nan)
            ylabel = "share of errors (fp+fn)"
        else:
            fp_plot = fp
            fn_plot = fn
            ylabel = "count"

        groups = df.index.tolist()

        if figsize is None:
            figsize = (7.5, 4.5)

        fig, ax = plt.subplots(figsize=figsize)
        ax.bar(groups, fp_plot.values, label="FP")
        ax.bar(groups, fn_plot.values, bottom=fp_plot.values, label="FN")

        ax.set_ylabel(ylabel)
        ax.set_xlabel("group")
        ax.tick_params(axis="x", rotation=rotation)
        ax.legend()

        if title is None:
            title = f"Error breakdown by group: {feature}"
        ax.set_title(title)

        fig.tight_layout()
        return fig

    def threshold_sweep(
        self,
        threshold_df: pd.DataFrame,
        feature: str,
        group: Union[str, int, float],
        metrics: Sequence[str],
        figsize: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
    ) -> plt.Figure:
        """
        Line plot across thresholds for a single (feature, group).
        Expects index: (feature, group, threshold).
        """
        threshold_df = _require_df("threshold_df", threshold_df)
        _require_multiindex(threshold_df, ["feature", "group", "threshold"], "threshold_df")

        group_str = str(group)
        if feature not in threshold_df.index.get_level_values("feature"):
            feats = sorted(set(_as_str_list(threshold_df.index.get_level_values("feature"))))
            raise ValueError(f"feature='{feature}' not found. Available features: {feats}")

        if group_str not in threshold_df.index.get_level_values("group").astype(str):
            groups = sorted(set(_as_str_list(threshold_df.index.get_level_values("group"))))
            raise ValueError(f"group='{group_str}' not found. Available groups: {groups}")

        # Slice
        df = threshold_df.copy()
        df = df.reset_index()
        df["group"] = df["group"].astype(str)

        df = df[(df["feature"] == feature) & (df["group"] == group_str)].copy()
        if df.empty:
            raise ValueError("No rows found for the specified (feature, group).")

        for m in metrics:
            if m not in df.columns:
                raise ValueError(f"Metric '{m}' not found in threshold_df columns: {list(df.columns)}")

        df = df.sort_values("threshold")

        if figsize is None:
            figsize = (7.5, 4.5)

        fig, ax = plt.subplots(figsize=figsize)
        x = df["threshold"].astype(float).values

        for m in metrics:
            ax.plot(x, df[m].astype(float).values, label=m)

        ax.set_xlabel("threshold")
        ax.set_ylabel("value")
        ax.legend()

        if title is None:
            title = f"Threshold sweep: {feature}={group_str}"
        ax.set_title(title)

        fig.tight_layout()
        return fig

    def model_tradeoff(
        self,
        models_df: pd.DataFrame,
        perf_metric: str,
        fairness_metric: str,
        label_col: str = "model",
        figsize: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
    ) -> plt.Figure:
        """
        Scatter plot: performance vs fairness/disparity for multiple models.
        """
        models_df = _require_df("models_df", models_df)
        _require_cols(models_df, [label_col, perf_metric, fairness_metric], "models_df")

        df = models_df.copy()
        if figsize is None:
            figsize = (7.5, 5.0)

        fig, ax = plt.subplots(figsize=figsize)
        ax.scatter(df[perf_metric].astype(float).values, df[fairness_metric].astype(float).values)

        for _, r in df.iterrows():
            ax.annotate(str(r[label_col]), (float(r[perf_metric]), float(r[fairness_metric])), fontsize=9)

        ax.set_xlabel(perf_metric)
        ax.set_ylabel(fairness_metric)

        if title is None:
            title = f"Model trade-off: {perf_metric} vs {fairness_metric}"
        ax.set_title(title)

        fig.tight_layout()
        return fig


# =========================
# Convenience functional API
# =========================

_plotter = Plotter()

def plot_metrics_bars(*args, **kwargs) -> plt.Figure:
    return _plotter.metrics_bars(*args, **kwargs)

def plot_disparity(*args, **kwargs) -> plt.Figure:
    return _plotter.disparity(*args, **kwargs)

def plot_error_breakdown(*args, **kwargs) -> plt.Figure:
    return _plotter.error_breakdown(*args, **kwargs)

def plot_threshold_sweep(*args, **kwargs) -> plt.Figure:
    return _plotter.threshold_sweep(*args, **kwargs)

def plot_model_tradeoff(*args, **kwargs) -> plt.Figure:
    return _plotter.model_tradeoff(*args, **kwargs)
