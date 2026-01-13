# tests/test_core.py
import math
import numpy as np
import pandas as pd
import pytest

from fairness.data import load_csv, load_features_and_target
from fairness.preprocess import add_age_group, map_binary_column, preprocess_tabular
from fairness.groups import make_intersectional_labels, make_eval_df
from fairness.metrics import group_acc, group_acc_diff, group_acc_ratio


# -----------------------
# data.py tests
# -----------------------

def test_load_csv_missing_file_raises(tmp_path):
    missing = tmp_path / "nope.csv"
    with pytest.raises(FileNotFoundError):
        load_csv(missing)


def test_load_csv_empty_csv_raises(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("") 
    p.write_text("a,b\n")
    with pytest.raises(ValueError, match="Loaded CSV is empty"):
        load_csv(p)


def test_load_features_and_target_splits_and_drops_cols():
    df = pd.DataFrame(
        {
            "Age": [40, 70],
            "Sex": ["M", "F"],
            "age_group": ["young", "older"],
            "HeartDisease": [0, 1],
        }
    )
    X, y = load_features_and_target(df, target_col="HeartDisease", drop_cols=("age_group",))
    assert list(y) == [0, 1]
    assert "HeartDisease" not in X.columns
    assert "age_group" not in X.columns
    assert X.shape == (2, 2)


def test_load_features_and_target_raises_if_no_features_left():
    df = pd.DataFrame({"target": [0, 1]})
    with pytest.raises(ValueError, match="No feature columns remain"):
        load_features_and_target(df, target_col="target")


# -----------------------
# preprocess.py tests
# -----------------------

def test_add_age_group_bins_correctly():
    df = pd.DataFrame({"Age": [10, 54, 55, 80]})
    out = add_age_group(df, bins=(0, 55, 120), labels=("young", "older"))
    assert out["age_group"].tolist() == ["young", "young", "young", "older"]
    assert out["age_group"].isna().sum() == 0


def test_add_age_group_raises_when_outside_bins():
    df = pd.DataFrame({"Age": [-1, 10]})
    with pytest.raises(ValueError, match="contains NaNs after binning"):
        add_age_group(df, bins=(0, 55, 120), labels=("young", "older"))


def test_map_binary_column_strict_raises_on_unmapped():
    df = pd.DataFrame({"Sex": ["M", "X"]})
    with pytest.raises(ValueError, match="Unmapped values"):
        map_binary_column(df, col="Sex", mapping={"M": 1, "F": 0}, strict=True)


def test_preprocess_tabular_one_hot_and_drop_cols():
    df = pd.DataFrame(
        {
            "Age": [40, 70],
            "Sex": ["M", "F"],
            "age_group": ["young", "older"],
        }
    )
    out = preprocess_tabular(df, drop_cols=("age_group",), one_hot=True, drop_first=True)

    # age_group should be gone
    assert "age_group" not in out.columns

    # Age numeric should remain
    assert "Age" in out.columns

    # Sex should be one-hot encoded with drop_first=True => only one dummy column
    sex_cols = [c for c in out.columns if c.startswith("Sex_")]
    assert len(sex_cols) == 1


# -----------------------
# groups.py tests
# -----------------------

def test_make_intersectional_labels_format_and_missing_to_NA():
    df = pd.DataFrame({"Sex": [1, np.nan], "age_group": ["older", "young"]})
    labels = make_intersectional_labels(df, protected=("Sex", "age_group"))
    assert labels[0] == "Sex=1.0|age_group=older" or labels[0] == "Sex=1|age_group=older"
    assert "Sex=NA" in labels[1]
    assert labels[1].endswith("age_group=young")


# -----------------------
# metrics.py tests
# -----------------------

def test_metrics_group_acc_diff_ratio_and_absent_group_nan():
    subject_labels = ["A", "A", "A", "B", "B"]
    y_true =        [1,   0,   1,   1,   0]
    y_pred =        [1,   1,   0,   1,   0]

    # Group A accuracy: correct at idx0 only => 1/3
    acc_a = group_acc("A", subject_labels, y_pred, y_true)
    assert acc_a == pytest.approx(1/3)

    # Group B accuracy: idx3 correct, idx4 correct => 2/2
    acc_b = group_acc("B", subject_labels, y_pred, y_true)
    assert acc_b == pytest.approx(1.0)

    diff = group_acc_diff("A", "B", subject_labels, y_pred, y_true)
    assert diff == pytest.approx(abs((1/3) - 1.0))

    # ratio returns log(max(acc_a/acc_b, acc_b/acc_a)) by default
    ratio_log = group_acc_ratio("A", "B", subject_labels, y_pred, y_true, natural_log=True)
    expected = math.log(max((1/3)/1.0, 1.0/(1/3)))
    assert ratio_log == pytest.approx(expected)

    # absent group -> NaN
    acc_c = group_acc("C", subject_labels, y_pred, y_true)
    assert np.isnan(acc_c)
