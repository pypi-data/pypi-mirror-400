#Import necessary packages
import pandas as pd
import numpy as np
import itertools


def group_to_binary(labels, privileged_label):
    """
    Adapts single fairness functions to the intersectional
    ones
    labels: list of group labels (e.g. 'Male', 'Female')
    privileged_label: label considered privileged
    returns: numpy array (1 = privileged, 0 = unprivileged)
    """
    labels = np.array(labels)
    
    if privileged_label not in labels:
        raise ValueError(
            f"Privileged label '{privileged_label}' not found in group labels. "
            f"Available labels: {np.unique(labels)}"
        )

    return (labels == privileged_label).astype(int)

def calculate_TP_FN_FP_TN(y_test, y_pred):
    """
    Computes the confusion matrix components: True Positives (TP),
    False Negatives (FN), True Negatives (TN), and False Positives (FP).

    Notes
    -----
    - Binary classification is assumed.
    - Label 1 denotes the positive outcome.
    - Label 0 denotes the negative outcome.
    """

    y_test = np.array(y_test)
    y_pred = np.array(y_pred)

    if len(y_test) != len(y_pred):
        raise ValueError(
            "y_test and y_pred must have the same length."
        )

    valid_values = {0, 1}

    if not set(np.unique(y_test)).issubset(valid_values):
        raise ValueError(
            "y_test must contain only {0, 1}, where 1 is the positive outcome."
        )

    if not set(np.unique(y_pred)).issubset(valid_values):
        raise ValueError(
            "y_pred must contain only {0, 1}, where 1 is the positive outcome."
        )

    if 1 not in y_test:
        raise ValueError(
            "y_test contains no positive samples (label=1). "
            "TPR-based metrics are undefined."
        )

    if 0 not in y_test:
        raise ValueError(
            "y_test contains no negative samples (label=0). "
            "FPR-based metrics are undefined."
        )

    tp = fp = tn = fn = 0

    for a, b in zip(y_test, y_pred):
        if a == 1 and b == 1:
            tp += 1
        elif a == 1 and b == 0:
            fn += 1
        elif a == 0 and b == 1:
            fp += 1
        elif a == 0 and b == 0:
            tn += 1

    return tp, fn, tn, fp

def calculate_TPR_TNR_FPR_FNR(tp, fn, tn, fp):
    """
    Compute classification rate metrics derived from the confusion matrix.

    Notes
    -----
    - Counts must be non-negative integers.
    - Label 1 is assumed to be the positive outcome.
    """

    # Type check
    for name, value in zip(
        ["tp", "fn", "tn", "fp"], [tp, fn, tn, fp]
    ):
        if not isinstance(value, (int,)):
            raise TypeError(f"{name} must be an integer. Got {type(value)}.")

        if value < 0:
            raise ValueError(f"{name} must be non-negative. Got {value}.")

    # Denominator checks (critical for fairness metrics)
    if tp + fn == 0:
        raise ZeroDivisionError(
            "TP + FN = 0. True Positive Rate (TPR) and "
            "False Negative Rate (FNR) are undefined."
        )

    if tn + fp == 0:
        raise ZeroDivisionError(
            "TN + FP = 0. True Negative Rate (TNR) and "
            "False Positive Rate (FPR) are undefined."
        )

    TPR = tp / (tp + fn)
    TNR = tn / (tn + fp)
    FPR = fp / (tn + fp)
    FNR = fn / (tp + fn)

    return TPR, TNR, FPR, FNR

def calculate_EOD(y_test, y_pred, group_labels, privileged_label):
    """
    Compute the Equal Opportunity Difference (EOD) between demographic groups.

    Equal Opportunity Difference measures the absolute difference in
    True Positive Rates (TPR) between the underprivileged and privileged
    groups. A lower EOD indicates fairer performance with respect to
    correctly identifying positive cases across groups.

    Parameters
    ----------
    y_test : array-like of shape (n_samples,)
        Ground-truth binary labels.
        Expected values: 0 (negative outcome) or 1 (positive outcome).

    y_pred : array-like of shape (n_samples,)
        Predicted binary labels from a classifier.
        Expected values: 0 (negative outcome) or 1 (positive outcome).
        
    group_labels: categorical group membership labels for a protected attribute.
        Each entry corresponds to the same-indexed sample in y_test and y_pred.
        
    privileged_label : str
        The label within group_labels considered to be the privileged group
        (e.g. 'Male' for sex, 'Older' for age). All other labels are treated
        as unprivileged.

    Returns
    -------
    EOD : float
        Equal Opportunity Difference, defined as:

            EOD = |TPR_underprivileged − TPR_privileged|

        Values closer to 0 indicate better fairness.

    Notes
    -----
    - EOD focuses exclusively on the positive class (y = 1).
    """
    group_labels = np.array(group_labels)
    y_test = np.array(y_test)
    y_pred = np.array(y_pred)

    if not (len(y_test) == len(y_pred) == len(group_labels)):
        raise ValueError(
            "y_test, y_pred, and group_labels must have the same length."
        )

    if privileged_label not in group_labels:
        raise ValueError(
            f"Privileged label '{privileged_label}' not found in group_labels. "
            f"Available labels: {np.unique(group_labels)}"
        )
    
    privileged_group = group_to_binary(group_labels, privileged_label)
    # Masks

    mask_priv = (privileged_group == 1)
    mask_unpriv = (privileged_group == 0)
    
    
    # Privileged group
    tp_p, fn_p, fp_p, tn_p = calculate_TP_FN_FP_TN(
        y_test[mask_priv],
        y_pred[mask_priv]
    )
    TPR_p, TNR_p, FPR_p, FNR_p = calculate_TPR_TNR_FPR_FNR(tp_p,fn_p,tn_p,fp_p)
    
    # Underprivileged group
    tp_u, fn_u, fp_u, tn_u = calculate_TP_FN_FP_TN(
        y_test[mask_unpriv],
        y_pred[mask_unpriv]
    )
    TPR_u, TNR_u, FPR_u, FNR_u = calculate_TPR_TNR_FPR_FNR(tp_u,fn_u,tn_u,fp_u)
    
    # Equal Opportunity Difference
    EOD = abs(TPR_u - TPR_p)
    
    return EOD

def calculate_AOD(y_test, y_pred, group_labels, privileged_label):
    """
    Compute the Average Odds Difference (AOD) between demographic groups.

    Average Odds Difference measures the average difference in both
    True Positive Rates (TPR) and False Positive Rates (FPR) between the
    underprivileged and privileged groups. It captures disparities in
    model performance for both positive and negative outcomes.

    Parameters
    ----------
    y_test : array-like of shape (n_samples,)
        Ground-truth binary labels.
        Expected values: 0 (negative outcome) or 1 (positive outcome).

    y_pred : array-like of shape (n_samples,)
        Predicted binary labels from a classifier.
        Expected values: 0 (negative outcome) or 1 (positive outcome).

    group_labels: categorical group membership labels for a protected attribute.
        Each entry corresponds to the same-indexed sample in y_test and y_pred.
        
    privileged_label : str
        The label within group_labels considered to be the privileged group
        (e.g. 'Male' for sex, 'Older' for age). All other labels are treated
        as unprivileged.

    Returns
    -------
    AOD : float
        Average Odds Difference, defined as:

            AOD = 0.5 × [ (FPR_underprivileged − FPR_privileged)
                        + (TPR_underprivileged − TPR_privileged) ]

        Values closer to 0 indicate better fairness.
    """
    # Masks
    group_labels = np.array(group_labels)
    y_test = np.array(y_test)
    y_pred = np.array(y_pred)

    if not (len(y_test) == len(y_pred) == len(group_labels)):
        raise ValueError(
            "y_test, y_pred, and group_labels must have the same length."
        )

    if privileged_label not in group_labels:
        raise ValueError(
            f"Privileged label '{privileged_label}' not found in group_labels. "
            f"Available labels: {np.unique(group_labels)}"
        )
    
    privileged_group = group_to_binary(group_labels, privileged_label)
    # Masks

    mask_priv = (privileged_group == 1)
    mask_unpriv = (privileged_group == 0)
    
    
    # Privileged group
    tp_p, fn_p, fp_p, tn_p = calculate_TP_FN_FP_TN(
        y_test[mask_priv],
        y_pred[mask_priv]
    )
    TPR_p, TNR_p, FPR_p, FNR_p = calculate_TPR_TNR_FPR_FNR(tp_p,fn_p,tn_p,fp_p)
    
    # Underprivileged group
    tp_u, fn_u, fp_u, tn_u = calculate_TP_FN_FP_TN(
        y_test[mask_unpriv],
        y_pred[mask_unpriv]
    )
    TPR_u, TNR_u, FPR_u, FNR_u = calculate_TPR_TNR_FPR_FNR(tp_u,fn_u,tn_u,fp_u)
    
    # Average Odds Difference
    AOD = ((FPR_u - FPR_p) + (TPR_u - TPR_p)) / 2

    return AOD

def calculate_DI(y_pred, group_labels, privileged_label):
    """
    Compute Disparate Impact (DI) between demographic groups.

    Disparate Impact measures the ratio of positive prediction rates
    between the underprivileged and privileged groups. It evaluates
    whether one group receives favorable outcomes less frequently
    than another, regardless of ground-truth labels.

    Parameters
    ----------
    y_pred : array-like of shape (n_samples,)
        Predicted binary labels from a classifier.
        Expected values: 0 (negative outcome) or 1 (positive outcome).

    group_labels: categorical group membership labels for a protected attribute.
        Each entry corresponds to the same-indexed sample in y_test and y_pred.
        
    privileged_label : str
        The label within group_labels considered to be the privileged group
        (e.g. 'Male' for sex, 'Older' for age). All other labels are treated
        as unprivileged.
        
    Returns
    -------
    DI : float
        Disparate Impact, defined as:

            DI = P(ŷ = 1 | underprivileged) / P(ŷ = 1 | privileged)

        where P(ŷ = 1 | group) is the positive prediction rate
        for the specified group.

    """
    group_labels = np.array(group_labels)
    y_pred = np.array(y_pred)
    privileged_group = group_to_binary(group_labels, privileged_label)
    mask_priv = (privileged_group == 1)
    mask_unpriv = (privileged_group == 0)

    P_priv = np.mean(y_pred[mask_priv] == 1)
    P_unpriv = np.mean(y_pred[mask_unpriv] == 1)

    DI = P_unpriv / P_priv

    return DI