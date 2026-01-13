import numpy as np
import pytest
from fairness.single_metrics import (
    group_to_binary,
    calculate_TP_FN_FP_TN,
    calculate_TPR_TNR_FPR_FNR,
    calculate_EOD,
    calculate_AOD,
    calculate_DI
)

# -----------------------------------------------------
# 1. Testing for the right inputs
# -----------------------------------------------------


def test_group_to_binary_valid():
    labels = ["A", "B", "A", "A"]
    result = group_to_binary(labels, privileged_label="A")
    assert np.array_equal(result, np.array([1, 0, 1, 1]))


def test_confusion_matrix_valid():
    y_test = [1, 1, 0, 0]
    y_pred = [1, 0, 1, 0]

    tp, fn, tn, fp = calculate_TP_FN_FP_TN(y_test, y_pred)

    assert tp == 1
    assert fn == 1
    assert fp == 1
    assert tn == 1


def test_rates_valid():
    tp, fn, tn, fp = 5, 5, 8, 2
    TPR, TNR, FPR, FNR = calculate_TPR_TNR_FPR_FNR(tp, fn, tn, fp)

    assert TPR == 0.5
    assert TNR == 0.8
    assert FPR == 0.2
    assert FNR == 0.5


def test_EOD_valid():
    y_test = [1, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 0, 0, 1, 1]
    groups = ["M", "M", "M", "F", "F", "F"]

    eod = calculate_EOD(y_test, y_pred, groups, privileged_label="M")

    assert isinstance(eod, float)
    assert eod >= 0


def test_AOD_valid():
    y_test = [1, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 0, 0, 1, 1]
    groups = ["M", "M", "M", "F", "F", "F"]

    aod = calculate_AOD(y_test, y_pred, groups, privileged_label="M")

    assert isinstance(aod, float)


def test_DI_valid():
    y_pred = [1, 0, 1, 0, 1, 0]
    groups = ["M", "M", "M", "F", "F", "F"]

    di = calculate_DI(y_pred, groups, privileged_label="M")

    assert isinstance(di, float)
    assert di >= 0


# -----------------------------------------------------
# 2. Testing for Edge Cases
# -----------------------------------------------------

def test_group_to_binary_single_group():
    labels = ["A", "A", "A"]
    result = group_to_binary(labels, privileged_label="A")
    assert np.all(result == 1)


def test_confusion_matrix_all_correct_predictions():
    y_test = [1, 0, 1, 0]
    y_pred = [1, 0, 1, 0]

    tp, fn, tn, fp = calculate_TP_FN_FP_TN(y_test, y_pred)

    assert fn == 0
    assert fp == 0


def test_DI_zero_positive_privileged():
    y_pred = [0, 0, 1, 1]
    groups = ["P", "P", "U", "U"]

    with pytest.raises(ZeroDivisionError):
        calculate_DI(y_pred, groups, privileged_label="P")


def test_EOD_perfect_fairness():
    y_test = [1, 0, 1, 0]
    y_pred = [1, 0, 1, 0]
    groups = ["A", "A", "B", "B"]

    eod = calculate_EOD(y_test, y_pred, groups, privileged_label="A")
    assert eod == 0.0


# -----------------------------------------------------
# 3. Testing for Incorrect Inputs
# -----------------------------------------------------

def test_group_to_binary_invalid_privileged_label():
    labels = ["A", "B", "C"]

    with pytest.raises(ValueError):
        group_to_binary(labels, privileged_label="D")


def test_confusion_matrix_length_mismatch():
    with pytest.raises(ValueError):
        calculate_TP_FN_FP_TN([1, 0], [1])


def test_confusion_matrix_invalid_labels():
    with pytest.raises(ValueError):
        calculate_TP_FN_FP_TN([1, 2, 0], [1, 0, 1])


def test_rates_negative_counts():
    with pytest.raises(ValueError):
        calculate_TPR_TNR_FPR_FNR(1, -1, 2, 3)


def test_rates_zero_denominator():
    with pytest.raises(ZeroDivisionError):
        calculate_TPR_TNR_FPR_FNR(0, 0, 5, 2)


def test_EOD_length_mismatch():
    with pytest.raises(ValueError):
        calculate_EOD(
            y_test=[1, 0],
            y_pred=[1, 0, 1],
            group_labels=["A", "B"],
            privileged_label="A"
        )


def test_AOD_invalid_privileged_label():
    with pytest.raises(ValueError):
        calculate_AOD(
            y_test=[1, 0],
            y_pred=[1, 0],
            group_labels=["X", "Y"],
            privileged_label="Z"
        )
