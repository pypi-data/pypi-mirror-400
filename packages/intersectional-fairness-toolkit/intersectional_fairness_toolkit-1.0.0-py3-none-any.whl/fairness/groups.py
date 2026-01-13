"""
fairness.groups
===============

Minimal utilities for constructing intersectional group labels and producing
an evaluation DataFrame aligned with model predictions and true labels.

Primary output: a tidy DataFrame with columns:
- subject_label  (intersectional group label per individual)
- y_pred         (model prediction)
- y_true         (true label)
"""

from __future__ import annotations

from typing import Sequence
import pandas as pd


def make_intersectional_labels(
    df: pd.DataFrame,
    protected: Sequence[str],
    *,
    sep: str = "|",
    kv_sep: str = "=",
    missing: str = "NA",
) -> list[str]:
    """
    Create an intersectional group label for each row of df.

    Example:
        Sex=1|age_group=older

    Parameters
    ----------
    df:
        DataFrame containing protected columns.
    protected:
        Column names to intersect (order defines label format).
    sep, kv_sep:
        Formatting separators for the label.
    missing:
        Placeholder for missing values.

    Returns
    -------
    list[str]
        One label per row, aligned with df.
    """
    if not protected:
        raise ValueError("protected must be a non-empty list of column names")

    missing_cols = [c for c in protected if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Protected columns not found: {missing_cols}")

    labels: list[str] = []
    for _, row in df[list(protected)].iterrows():
        parts = []
        for col in protected:
            val = row[col]
            if pd.isna(val):
                val = missing
            parts.append(f"{col}{kv_sep}{val}")
        labels.append(sep.join(parts))

    return labels


def make_eval_df(
    *,
    df_test: pd.DataFrame,
    protected: Sequence[str],
    y_pred: Sequence,
    y_true: Sequence,
    label_col: str = "subject_label",
) -> pd.DataFrame:
    """
    Build an evaluation DataFrame for group-based metric functions.

    The handoff format for metrics such as accuracy_diff:

        subject_labels = eval_df[label_col].tolist()
        predictions    = eval_df["y_pred"].tolist()
        true_statuses  = eval_df["y_true"].tolist()

    Parameters
    ----------
    df_test:
        Test-set DataFrame in the SAME row order as y_pred and y_true
        (typically df.loc[split.X_test.index]).
    protected:
        Protected columns used to define intersectional groups.
    y_pred:
        Model predictions aligned to df_test rows.
    y_true:
        True labels aligned to df_test rows.
    label_col:
        Name of the intersectional label column.

    Returns
    -------
    pd.DataFrame
        Columns: subject_label, y_pred, y_true (index preserved).
    """
    n = len(df_test)
    if len(y_pred) != n or len(y_true) != n:
        raise ValueError("df_test, y_pred, and y_true must have the same"
                         + "length")

    subject_labels = make_intersectional_labels(df_test, protected)

    return pd.DataFrame(
        {
            label_col: subject_labels,
            "y_pred": list(y_pred),
            "y_true": list(y_true),
        },
        index=df_test.index,
    )
