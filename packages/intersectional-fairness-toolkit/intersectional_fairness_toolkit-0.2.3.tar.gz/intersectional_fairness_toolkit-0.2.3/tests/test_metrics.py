import math
import numpy as np
import pytest

from fairness.metrics import (
    group_acc, group_acc_ratio, group_acc_diff,
    group_fnr, group_fpr, group_for, group_fdr,
    group_fnr_ratio, group_fpr_ratio, group_for_ratio, group_fdr_ratio,
    intersect_acc, all_intersect_accs,
    max_intersect_acc_diff, max_intersect_acc_ratio,
)


def test_perfect_predictions_all_core_rates():
    # Perfect prediction => acc=1 and all error rates = 0
    # (when denominators exist)
    labels = ["A", "A", "B", "B"]
    y_true = [1, 0, 1, 0]
    y_pred = [1, 0, 1, 0]

    assert group_acc("A", labels, y_pred, y_true) == pytest.approx(1.0)
    assert group_acc("B", labels, y_pred, y_true) == pytest.approx(1.0)

    assert group_fnr("A", labels, y_pred, y_true) == pytest.approx(0.0)
    assert group_fpr("A", labels, y_pred, y_true) == pytest.approx(0.0)
    assert group_for("A", labels, y_pred, y_true) == pytest.approx(0.0)
    assert group_fdr("A", labels, y_pred, y_true) == pytest.approx(0.0)


def test_group_fnr_nan_if_no_positive_truths_in_group():
    labels = ["A", "A", "B", "B"]
    y_true = [0, 0, 1, 1]   # group A has no positives
    y_pred = [0, 0, 1, 1]
    assert np.isnan(group_fnr("A", labels, y_pred, y_true))


def test_group_fpr_nan_if_no_negative_truths_in_group():
    labels = ["A", "A", "B", "B"]
    y_true = [1, 1, 0, 0]   # group A has no negatives
    y_pred = [1, 1, 0, 0]
    assert np.isnan(group_fpr("A", labels, y_pred, y_true))


def test_group_fdr_nan_if_no_positive_predictions_in_group():
    labels = ["A", "A", "B", "B"]
    y_true = [1, 0, 1, 0]
    y_pred = [0, 0, 0, 0]   # no positive predictions anywhere => FDR undefined
    assert np.isnan(group_fdr("A", labels, y_pred, y_true))
    assert np.isnan(group_fdr("B", labels, y_pred, y_true))


def test_group_for_nan_if_no_negative_predictions_in_group():
    labels = ["A", "A", "B", "B"]
    y_true = [1, 0, 1, 0]
    y_pred = [1, 1, 1, 1]   # no negative predictions anywhere => FOR undefined
    assert np.isnan(group_for("A", labels, y_pred, y_true))
    assert np.isnan(group_for("B", labels, y_pred, y_true))


def test_ratio_metrics_return_nan_if_any_group_metric_is_zero():
    # Your ratio functions explicitly return NaN if either metric is 0
    labels = ["A", "A", "B", "B"]
    y_true = [1, 1, 1, 1]
    y_pred = [1, 1, 0, 0]
    # In group B: FNR = 1.0 (all positives misclassified)
    # In group A: FNR = 0.0 (all positives correct) -> ratio should be NaN (because 0 involved)
    assert np.isnan(group_fnr_ratio("A", "B", labels, y_pred, y_true, natural_log=True))


def test_intersect_acc_correct_for_specific_intersection():
    # Two protected categories: sex and age_group
    subject_labels_dict = {
        "Sex":      ["M", "M", "F", "F"],
        "age_group": ["young", "older", "young", "older"],
    }
    y_true = [1, 0, 1, 0]
    y_pred = [1, 1, 1, 0]

    # Intersection: Sex=M AND age_group=young -> only sample 0, predicted correct => acc=1
    group_labels_dict = {"Sex": "M", "age_group": "young"}
    acc = intersect_acc(group_labels_dict, subject_labels_dict, y_pred, y_true)
    assert acc == pytest.approx(1.0)


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



def test_max_intersect_acc_ratio_nan_if_any_zero_accuracy():
    subject_labels_dict = {
        "Sex":      ["M", "M", "M", "F"],
        "age_group": ["young", "young", "older", "young"],
    }
    y_true = [1, 0, 1, 1]
    y_pred = [1, 1, 1, 0]
    
    assert np.isnan(max_intersect_acc_ratio(subject_labels_dict,
                                            y_pred, y_true,
                                            natural_log=True))