import matplotlib

matplotlib.use("Agg")

import matplotlib.figure
import pandas as pd

from fairness import metrics
from fairness import visualisation as vis


def _demo_inputs():
    subject_labels = [
        "Sex=M|age_group=young",
        "Sex=M|age_group=young",
        "Sex=F|age_group=young",
        "Sex=F|age_group=young",
        "Sex=M|age_group=older",
        "Sex=M|age_group=older",
        "Sex=F|age_group=older",
        "Sex=F|age_group=older",
    ]
    predictions = [1, 0, 1, 0, 1, 0, 1, 0]
    true_statuses = [1, 0, 0, 1, 1, 0, 0, 1]
    subject_labels_dict = {
        "Sex": ["M", "M", "F", "F", "M", "M", "F", "F"],
        "age_group": ["young", "young", "young", "young", "older", "older", "older", "older"],
    }
    return subject_labels, predictions, true_statuses, subject_labels_dict


def _assert_figure(fig):
    assert isinstance(fig, matplotlib.figure.Figure)


def test_plot_group_metric():
    subject_labels, predictions, true_statuses, _ = _demo_inputs()
    fig = vis.plot_group_metric(
        metrics.group_acc,
        subject_labels,
        predictions,
        true_statuses,
        sort=True,
    )
    _assert_figure(fig)


def test_plot_group_metric_from_eval_df():
    subject_labels, predictions, true_statuses, _ = _demo_inputs()
    eval_df = pd.DataFrame(
        {
            "subject_label": subject_labels,
            "y_pred": predictions,
            "y_true": true_statuses,
        }
    )
    fig = vis.plot_group_metric_from_eval_df(metrics.group_fnr, eval_df, sort=True)
    _assert_figure(fig)


def test_plot_pairwise_group_metric():
    subject_labels, predictions, true_statuses, _ = _demo_inputs()
    fig = vis.plot_pairwise_group_metric(
        metrics.group_acc_diff,
        subject_labels,
        predictions,
        true_statuses,
    )
    _assert_figure(fig)


def test_plot_intersectional_metric():
    subject_labels, predictions, true_statuses, subject_labels_dict = _demo_inputs()
    fig = vis.plot_intersectional_metric(
        metrics.all_intersect_accs,
        subject_labels_dict,
        predictions,
        true_statuses,
    )
    _assert_figure(fig)


def test_plot_scalar_metrics():
    subject_labels, predictions, true_statuses, subject_labels_dict = _demo_inputs()
    values = {
        "max_intersect_acc_diff": metrics.max_intersect_acc_diff(
            subject_labels_dict, predictions, true_statuses
        ),
        "max_intersect_acc_ratio": metrics.max_intersect_acc_ratio(
            subject_labels_dict, predictions, true_statuses, natural_log=False
        ),
    }
    fig = vis.plot_scalar_metrics(values)
    _assert_figure(fig)


def test_plot_single_metrics():
    y_test = [1, 0, 1, 0, 1, 0, 1, 0]
    y_pred = [1, 0, 0, 1, 1, 0, 1, 0]
    group_labels = ["M", "M", "F", "F", "M", "M", "F", "F"]
    fig = vis.plot_single_metrics(
        y_test=y_test,
        y_pred=y_pred,
        group_labels=group_labels,
        privileged_label="M",
    )
    _assert_figure(fig)


def test_plot_single_metrics_invalid_name():
    y_test = [1, 0, 1, 0]
    y_pred = [1, 0, 0, 1]
    group_labels = ["M", "M", "F", "F"]
    try:
        vis.plot_single_metrics(
            y_test=y_test,
            y_pred=y_pred,
            group_labels=group_labels,
            privileged_label="M",
            metrics=("NOPE",),
        )
    except ValueError as exc:
        assert "Unknown metric" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown single metric")
