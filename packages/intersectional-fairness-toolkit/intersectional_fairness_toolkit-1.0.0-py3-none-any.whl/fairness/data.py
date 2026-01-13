"""
fairness.data
=============

Data loading utilities used by the fairness toolkit.

This module loads tabular datasets into a pandas
DataFrame, while preserving row order and/or indices
so that downstream steps can guarantee alignment between:

- model predictions (y_pred)
- true labels (y_test)
- protected attributes used to construct intersectional groups

Dataset-specific logic (e.g., mapping target labels, binning ages, cleaning
special missing-value encodings such as '?') should live in small adapter
functions.

Typical usage
-------------
>>> from fairness.data import load_csv, load_features_and_target
>>> df = load_csv("data/heart.csv")
>>> X, y = load_features_and_target(df, target_col="HeartDisease")
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple, Union
import urllib.parse

import pandas as pd

PathLike = Union[str, Path]


def load_csv(
    path: PathLike,
    *,
    index_col: Optional[Union[int, str]] = None,
    na_values: Optional[Union[str, Sequence[str]]] = None,
) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    The CSV may be provided either as a local file path or as a URL
    (e.g. an HTTP(S) link to a raw CSV file).

    Parameters
    ----------
    path:
        Path or URL to the CSV file.
    index_col:
        Column to use as the row index (passed to pandas.read_csv). If None,
        pandas uses a default integer index.
    na_values:
        Additional strings to recognise as NA/NaN.

    Returns
    -------
    pd.DataFrame
        The dataset as a DataFrame.

    Raises
    ------
    FileNotFoundError
        If a local file path does not exist.
    ValueError
        If the loaded CSV is empty.
    """
    path_str = str(path)

    # Case 1: URL
    if urllib.parse.urlparse(path_str).scheme in {"http", "https"}:
        df = pd.read_csv(path_str, index_col=index_col, na_values=na_values)

    # Case 2: Local file path
    else:
        path_obj = Path(path_str)
        if not path_obj.exists():
            raise FileNotFoundError(f"CSV not found: {path_obj}")

        df = pd.read_csv(path_obj, index_col=index_col, na_values=na_values)

    if df.empty:
        raise ValueError(f"Loaded CSV is empty: {path_str}")

    return df


def validate_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    """
    Validate that required columns exist in the DataFrame.

    Parameters
    ----------
    df:
        Input DataFrame.
    required:
        Column names that must be present.

    Raises
    ------
    ValueError
        If any required column is missing.
    """
    required_set = set(required)
    missing = required_set - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def load_features_and_target(
    df: pd.DataFrame,
    *,
    target_col: str,
    drop_cols: Sequence[str] = (),
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Split a DataFrame into features X and target y.

    Parameters
    ----------
    df:
        Full dataset containing both features and target.
    target_col:
        Name of the target column.
    drop_cols:
        Additional columns to drop from X (e.g., derived protected attributes
        used only for fairness analysis such as 'age_group').

    Returns
    -------
    (X, y):
        X is a DataFrame of features, y is a Series of labels.

    Raises
    ------
    ValueError
        If target_col is not in df, or if resulting X is empty.
    """
    validate_columns(df, [target_col])

    y = df[target_col]
    X = df.drop(columns=[target_col, *drop_cols], errors="raise")

    if X.shape[1] == 0:
        raise ValueError("No feature columns remain after dropping"
                         + "target/drop_cols")

    return X, y


# -----------------------------
# Dataset adapters
# -----------------------------


def load_heart_csv(
    path: PathLike,
    *,
    target_col: str = "HeartDisease",
) -> pd.DataFrame:
    """
    Load the Heart Disease CSV used in the tutorial.

    This is a wrapper around load_csv()

    Parameters
    ----------
    path:
        Path to heart.csv.
    target_col:
        Expected target column name (used for validation).

    Returns
    -------
    pd.DataFrame
        Loaded dataset.

    Raises
    ------
    ValueError
        If the expected target column is missing.
    """
    df = load_csv(path)
    validate_columns(df, [target_col])
    return df
