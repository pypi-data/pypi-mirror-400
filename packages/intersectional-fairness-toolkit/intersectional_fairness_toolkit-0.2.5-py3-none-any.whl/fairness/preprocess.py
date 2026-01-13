"""
fairness.preprocess
===================

Preprocessing utilities for tabular datasets used in fairness analysis.

This module includes:
- feature engineering (e.g., binning age into age_group)
- converting raw tabular data into numeric features suitable for ML
- producing reproducible train/test splits while preserving indices

Design notes
------------
- The toolkit is model-agnostic: these functions do not require sklearn pipelines,
  but they produce outputs compatible with sklearn and similar libraries.
- Protected attributes may be used for fairness analysis even if they are excluded
  from model training. Derived protected attributes (e.g. age_group) are excluded from model inputs.

Typical usage
-------------
>>> from fairness.data import load_csv
>>> from fairness.preprocess import add_age_group, preprocess_tabular, make_train_test_split
>>> df = load_csv("data/heart.csv")
>>> df = add_age_group(df)
>>> df_model = preprocess_tabular(df)
>>> split = make_train_test_split(df_model, target_col="HeartDisease", drop_cols=("age_group",))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import pandas as pd
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class SplitData:
    """
    Container for a reproducible train/test split.

    Attributes
    ----------
    X_train, X_test:
        Feature matrices for training and testing.
    y_train, y_test:
        Target vectors for training and testing.
    """

    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series


# ---------------------------------------------------------------------
# Feature engineering helpers
# ---------------------------------------------------------------------


def add_age_group(
    df: pd.DataFrame,
    age_col: str = "Age",
    new_col: str = "age_group",
    bins: Sequence[float] = (0, 55, 120),
    labels: Sequence[str] = ("young", "older"),
) -> pd.DataFrame:
    """
    Add a categorical age-group column derived from a continuous age column.

    This is useful for fairness analysis because continuous protected attributes
    (like age) create too many groups; binning yields interpretable groups.

    Parameters
    ----------
    df:
        Input dataset.
    age_col:
        Name of the column containing numeric ages.
    new_col:
        Name of the derived categorical column to create.
    bins:
        Bin edges passed to pandas.cut.
    labels:
        Labels assigned to the bins.

    Returns
    -------
    pd.DataFrame
        Copy of df with the new categorical column added.

    Raises
    ------
    ValueError
        If age_col is missing or binning produces missing values.
    """
    if age_col not in df.columns:
        raise ValueError(f"Expected column '{age_col}' to create {new_col}")

    out = df.copy()
    out[new_col] = pd.cut(out[age_col], bins=list(bins), labels=list(labels))

    if out[new_col].isna().any():
        raise ValueError(
            f"{new_col} contains NaNs after binning; check '{age_col}' values and bins"
        )
    return out


def map_binary_column(
    df: pd.DataFrame,
    *,
    col: str,
    mapping: Mapping[object, object],
    strict: bool = True,
) -> pd.DataFrame:
    """
    Map values of a binary/categorical column to new values (e.g., 'M'/'F' -> 1/0).

    Parameters
    ----------
    df:
        Input dataset.
    col:
        Column name to map.
    mapping:
        Dictionary defining how to map values.
    strict:
        If True, raise if unmapped values occur. If False, leave unmapped as-is.

    Returns
    -------
    pd.DataFrame
        Copy of df with mapped column.

    Raises
    ------
    ValueError
        If strict=True and unmapped values are found.
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found")

    out = df.copy()
    out[col] = out[col].map(mapping)

    if strict and out[col].isna().any():
        raise ValueError(f"Unmapped values found in '{col}' using mapping={mapping}")

    return out


def apply_transforms(
    df: pd.DataFrame,
    transforms: Sequence[Callable[[pd.DataFrame], pd.DataFrame]],
) -> pd.DataFrame:
    """
    Apply a sequence of DataFrame -> DataFrame transforms in order.

    Parameters
    ----------
    df:
        Input dataset.
    transforms:
        Sequence of callables each returning a modified DataFrame.

    Returns
    -------
    pd.DataFrame
        Transformed DataFrame.
    """
    out = df
    for fn in transforms:
        out = fn(out)
    return out


# ---------------------------------------------------------------------
# Core preprocessing for ML
# ---------------------------------------------------------------------


def preprocess_tabular(
    df: pd.DataFrame,
    *,
    drop_cols: Sequence[str] = (),
    one_hot: bool = True,
    drop_first: bool = True,
) -> pd.DataFrame:
    """
    Convert a tabular DataFrame into numeric ML-ready features.

    Performs one-hot encoding for categorical columns (object/category)
    and leaves numeric columns unchanged.

    Parameters
    ----------
    df:
        Input dataset.
    drop_cols:
        Columns to drop prior to encoding
    one_hot:
        Whether to one-hot encode categorical columns.
    drop_first:
        If one_hot=True, drop the first level for each categorical variable to avoid
        perfect multicollinearity in logistic regression models.

    Returns
    -------
    pd.DataFrame
        A numeric DataFrame compatible with scikit-learn.

    """
    out = df.copy()
    if drop_cols:
        out = out.drop(columns=list(drop_cols), errors="raise")

    if one_hot:
        out = pd.get_dummies(out, drop_first=drop_first)

    return out


# ---------------------------------------------------------------------
# Train/test split helpers
# ---------------------------------------------------------------------


def make_train_test_split(
    df: pd.DataFrame,
    *,
    target_col: str,
    drop_cols: Sequence[str] = (),
    test_size: float = 0.3,
    random_state: int = 42,
    stratify: bool = True,
) -> SplitData:
    """
    Create a reproducible train/test split for modelling.

    Parameters
    ----------
    df:
        Preprocessed dataset containing features and target.
    target_col:
        Name of the target column.
    drop_cols:
        Additional columns to exclude from X (e.g. derived protected attributes).
    test_size:
        Fraction of rows assigned to the test set.
    random_state:
        Random seed for reproducibility.
    stratify:
        If True, stratify split by the target to preserve class balance.

    Returns
    -------
    SplitData
        Container holding X_train, X_test, y_train, y_test.

    Raises
    ------
    ValueError
        If target_col is missing or df is empty.
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found")

    y = df[target_col]
    X = df.drop(columns=[target_col, *drop_cols], errors="raise")

    strat = y if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=strat,
    )

    return SplitData(X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)
