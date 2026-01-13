"""
fairness.pipeline
=================

A convenience "one-stop" workflow for demos and internal testing.

This module is intentionally **not** part of the core fairness-metric API.
It exists to help quickly:
1) load a dataset
2) apply optional fairness-oriented transforms (e.g., add_age_group)
3) preprocess to model-ready numeric features (one-hot encoding)
4) create a train/test split
5) train a simple classifier to produce y_pred
6) build eval_df aligned to the test set (subject_label, y_pred, y_true)

The fairness toolkit remains model-agnostic; any model can be used externally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence

import pandas as pd

from fairness.data import load_csv
from fairness.groups import make_eval_df
from fairness.preprocess import SplitData, apply_transforms, make_train_test_split, preprocess_tabular


@dataclass(frozen=True)
class PipelineResult:
    """
    Outputs from the demo pipeline.

    Attributes
    ----------
    df_raw:
        Raw loaded DataFrame.
    df_fair:
        DataFrame after fairness-oriented transforms (e.g., age binning).
        This retains protected columns used to build group labels.
    df_model:
        Model-ready numeric DataFrame (after one-hot encoding etc.).
    split:
        Train/test split container with X_train, X_test, y_train, y_test.
    model:
        Fitted model object (e.g., scikit-learn estimator).
    y_pred:
        Predictions for X_test (aligned with split.X_test and split.y_test).
    eval_df:
        Tidy evaluation DataFrame aligned row-by-row with the test set:
        columns: subject_label, y_pred, y_true.
    """

    df_raw: pd.DataFrame
    df_fair: pd.DataFrame
    df_model: pd.DataFrame
    split: SplitData
    model: Any
    y_pred: Any
    eval_df: pd.DataFrame


def run_demo_pipeline(
    *,
    csv_path: str,
    target_col: str,
    protected_cols: Sequence[str],
    fairness_transforms: Optional[Sequence[Callable[[pd.DataFrame], pd.DataFrame]]] = None,
    drop_from_X: Sequence[str] = (),
    test_size: float = 0.3,
    random_state: int = 42,
    stratify: bool = True,
    model: Optional[Any] = None,
    model_fit_kwargs: Optional[dict] = None,
    predict_proba: bool = False,
) -> PipelineResult:
    """Run an end-to-end demo workflow and return aligned outputs."""
    df_raw = load_csv(csv_path)

    # 1) fairness-oriented transforms (optional)
    df_fair = df_raw
    if fairness_transforms:
        df_fair = apply_transforms(df_fair, fairness_transforms)

    missing = [c for c in protected_cols if c not in df_fair.columns]
    if missing:
        raise ValueError(f"Protected columns missing after transforms: {missing}")

    # 2) model-oriented preprocessing (one-hot etc.)
    df_model = preprocess_tabular(df_fair, drop_cols=drop_from_X)

    # 3) split for modelling (uses df_model)
    split = make_train_test_split(
        df_model,
        target_col=target_col,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )

    # 4) fit model and predict
    if model is None:
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000)),
        ])

    fit_kwargs = model_fit_kwargs or {}
    model.fit(split.X_train, split.y_train, **fit_kwargs)

    if predict_proba:
        if not hasattr(model, "predict_proba"):
            raise ValueError("predict_proba=True but model has no predict_proba method")
        y_pred = model.predict_proba(split.X_test)[:, 1]
    else:
        y_pred = model.predict(split.X_test)

    # 5) build eval_df from df_fair (so protected cols like age_group still exist)
    df_test = df_fair.loc[split.X_test.index]

    eval_df = make_eval_df(
        df_test=df_test,
        protected=protected_cols,
        y_pred=y_pred,
        y_true=split.y_test.to_numpy(),
    )

    return PipelineResult(
        df_raw=df_raw,
        df_fair=df_fair,
        df_model=df_model,
        split=split,
        model=model,
        y_pred=y_pred,
        eval_df=eval_df,
    )
