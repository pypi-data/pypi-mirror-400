import math
import numpy as np
from itertools import product


def group_acc(group_label, subject_labels, predictions, true_statuses):
    """
    Find the accuracy of a group with a specific label.

    Parameters
    ----------
    group_label : str or int
        The label of the group for which the accuracy of the model should be
        evaluated.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The accuracy of the model in the specified group. Returns
        np.nan if the group has no observations.
    """
    n_samples = len(predictions)

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_group = [False] * n_samples
    for observation in range(n_samples):
        if subject_labels[observation] == group_label:
            in_group[observation] = True
    group_results = [acc for acc, include
                     in zip(accurate_or_not, in_group)
                     if include is True]

    if len(group_results) > 0:
        accuracy = sum(group_results) / len(group_results)
    else:
        accuracy = np.nan

    return accuracy


def group_acc_diff(group_a_label, group_b_label, subject_labels,
                   predictions, true_statuses):
    """
    Calculate the absolute difference in accuracy between two groups.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The absolute difference in accuracy between the two groups. Returns
        np.nan if either group has no observations.
    """
    group_a_accuracy = group_acc(group_label=group_a_label,
                                 subject_labels=subject_labels,
                                 predictions=predictions,
                                 true_statuses=true_statuses)
    group_b_accuracy = group_acc(group_label=group_b_label,
                                 subject_labels=subject_labels,
                                 predictions=predictions,
                                 true_statuses=true_statuses)

    if np.isnan(group_a_accuracy) or np.isnan(group_b_accuracy):
        diff = np.nan
    else:
        diff = abs(group_a_accuracy - group_b_accuracy)

    return diff


def group_acc_ratio(group_a_label, group_b_label, subject_labels,
                    predictions, true_statuses, natural_log=True):
    """
    Calculate the ratio of accuracies between two groups.

    Computes the maximum of the two possible ratios (group A / group B and
    group B / group A) to ensure the ratio is always >= 1.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of accuracies between the two groups. Returns np.nan
        if either group has no observations or if either accuracy is 0.
    """
    group_a_accuracy = group_acc(group_label=group_a_label,
                                 subject_labels=subject_labels,
                                 predictions=predictions,
                                 true_statuses=true_statuses)
    group_b_accuracy = group_acc(group_label=group_b_label,
                                 subject_labels=subject_labels,
                                 predictions=predictions,
                                 true_statuses=true_statuses)

    if np.isnan(group_a_accuracy) or np.isnan(group_b_accuracy):
        ratio = np.nan
    elif group_a_accuracy == 0 or group_b_accuracy == 0:
        ratio = np.nan
    else:
        ratio_a_b = group_a_accuracy / group_b_accuracy
        ratio_b_a = group_b_accuracy / group_a_accuracy
        ratio = max(ratio_a_b, ratio_b_a)

    if natural_log is True:
        return np.log(ratio)
    else:
        return ratio


def intersect_acc(group_labels_dict, subject_labels_dict,
                  predictions, true_statuses):
    """
    Calculate accuracy for an intersectional group.

    An intersectional group is defined by membership in specific categories
    across multiple dimensions (e.g., specific age category and specific
    gender).

    Parameters
    ----------
    group_labels_dict : dict
        Dictionary mapping category names to specific group labels that define
        the intersectional group (e.g., {'age': 'Older', 'gender': 'Female'}).
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset. predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The accuracy of the model in the specified intersectional group.
        Returns np.nan if the group has no observations.
    """
    n_samples = len(predictions)
    categories = sorted(group_labels_dict.keys())

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_groups = [False] * n_samples
    for observation in range(n_samples):
        category_match = []
        for category in categories:
            group = group_labels_dict[category]
            if subject_labels_dict[category][observation] == group:
                category_match.append(1)
            else:
                category_match.append(0)
        in_intersectional_group = bool(math.prod(category_match))
        if in_intersectional_group is True:
            in_groups[observation] = True

    intersect_group_results = [acc for acc, include
                               in zip(accurate_or_not, in_groups)
                               if include is True]

    if len(intersect_group_results) > 0:
        accuracy = sum(intersect_group_results) / len(intersect_group_results)
    else:
        accuracy = np.nan

    return accuracy


def all_intersect_accs(subject_labels_dict, predictions, true_statuses):
    """
    Calculate accuracies for all possible intersectional groups.

    Computes accuracy for every combination of categories in the dataset
    (e.g., all age-group-gender combinations).

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    dict
        Dictionary mapping intersectional group names (formatted as
        "label1 + label2 + ...") to their respective accuracies.
    """
    category_names = sorted(subject_labels_dict.keys())
    unique_groups = {}
    for category in category_names:
        unique_groups[category] = sorted(set(subject_labels_dict[category]))

    all_combinations = list(product(*[unique_groups[category]
                            for category in category_names]))

    accuracies = {}
    for combination in all_combinations:
        combination_dict = {}
        for i, category_name in enumerate(category_names):
            combination_dict[category_name] = combination[i]
        intersect_accuracy = intersect_acc(
                                group_labels_dict=combination_dict,
                                subject_labels_dict=subject_labels_dict,
                                predictions=predictions,
                                true_statuses=true_statuses)
        intersect_group_name = " + ".join(str(group) for group in combination)
        accuracies[intersect_group_name] = intersect_accuracy

    return accuracies


def max_intersect_acc_diff(subject_labels_dict, predictions, true_statuses):
    """
    Calculate the maximum difference in accuracy across intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The maximum difference between any two intersectional group accuracies.
        Returns np.nan if any group has no observations.
    """
    accuracies = all_intersect_accs(
                    subject_labels_dict=subject_labels_dict,
                    predictions=predictions,
                    true_statuses=true_statuses)
    accuracy_values = np.array(list(accuracies.values()))

    if any(np.isnan(accuracy_values)):
        max_diff = np.nan
    else:
        max_diff = max(accuracy_values) - min(accuracy_values)

    return max_diff


def max_intersect_acc_ratio(subject_labels_dict, predictions, true_statuses,
                            natural_log=True):
    """
    Calculate the maximum ratio of accuracies across intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of the maximum to minimum accuracy across all
        intersectional groups. Returns np.nan if any group has no observations
        or if any accuracy is 0.
    """
    accuracies = all_intersect_accs(
                    subject_labels_dict=subject_labels_dict,
                    predictions=predictions,
                    true_statuses=true_statuses)
    accuracy_values = np.array(list(accuracies.values()))

    if any(np.isnan(accuracy_values)):
        max_ratio = np.nan
    elif np.any(accuracy_values == 0):
        max_ratio = np.nan
    else:
        max_ratio = max(accuracy_values) / min(accuracy_values)

    if natural_log is True:
        return np.log(max_ratio)
    else:
        return max_ratio


def group_fnr(group_label, subject_labels, predictions, true_statuses):
    """
    Find the false negative rate of a group with a specific label.

    Parameters
    ----------
    group_label : str or int
        The label of the group for which the false negative rate of the model
        should be evaluated.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false negative rate of the model in the specified group. Returns
        np.nan if the group has no observations.
    """
    n_samples = len(predictions)

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_group = [False] * n_samples
    for observation in range(n_samples):
        if subject_labels[observation] == group_label:
            in_group[observation] = True
    results_for_pos_cases = [acc for acc, include, truth
                             in zip(accurate_or_not, in_group, true_statuses)
                             if include is True and bool(truth) is True]

    if len(results_for_pos_cases) > 0:
        false_neg_rate = (len(results_for_pos_cases)
                          - sum(results_for_pos_cases)) \
                         / len(results_for_pos_cases)
    else:
        false_neg_rate = np.nan

    return false_neg_rate


def group_fnr_diff(group_a_label, group_b_label, subject_labels,
                   predictions, true_statuses):
    """
    Calculate the absolute difference in false negative rate between two
    groups.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The absolute difference in false negative rate between the two groups.
        Returns np.nan if either group has no observations.
    """
    group_a_fnr = group_fnr(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_fnr = group_fnr(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_fnr) or np.isnan(group_a_fnr):
        diff = np.nan
    else:
        diff = abs(group_a_fnr - group_b_fnr)

    return diff


def group_fnr_ratio(group_a_label, group_b_label, subject_labels,
                    predictions, true_statuses, natural_log=True):
    """
    Calculate the ratio of false negative rates between two groups.

    Computes the maximum of the two possible ratios (group A / group B and
    group B / group A) to ensure the ratio is always >= 1.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of false negative rates between the two groups. Returns
        np.nan if either group has no observations or if either false negative
        rate is 0.
    """
    group_a_fnr = group_fnr(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_fnr = group_fnr(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_fnr) or np.isnan(group_a_fnr):
        ratio = np.nan
    elif group_a_fnr == 0 or group_b_fnr == 0:
        ratio = np.nan
    else:
        ratio_a_b = group_a_fnr / group_b_fnr
        ratio_b_a = group_b_fnr / group_a_fnr
        ratio = max(ratio_a_b, ratio_b_a)

    if natural_log is True:
        return np.log(ratio)
    else:
        return ratio


def intersect_fnr(group_labels_dict, subject_labels_dict,
                  predictions, true_statuses):
    """
    Calculate false negative rate for an intersectional group.

    An intersectional group is defined by membership in specific categories
    across multiple dimensions (e.g., specific age category and specific
    gender).

    Parameters
    ----------
    group_labels_dict : dict
        Dictionary mapping category names to specific group labels that define
        the intersectional group (e.g., {'age': 'Older', 'gender': 'Female'}).
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false negative rate of the model in the specified intersectional
        group. Returns np.nan if the group has no observations.
    """
    n_samples = len(predictions)
    categories = sorted(group_labels_dict.keys())

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_groups = [False] * n_samples
    for observation in range(n_samples):
        category_match = []
        for category in categories:
            group = group_labels_dict[category]
            if subject_labels_dict[category][observation] == group:
                category_match.append(1)
            else:
                category_match.append(0)
        in_intersectional_group = bool(math.prod(category_match))
        if in_intersectional_group is True:
            in_groups[observation] = True

    inter_pos_case_results = [acc for acc, include, truth
                              in zip(accurate_or_not, in_groups, true_statuses)
                              if include is True and bool(truth) is True]

    if len(inter_pos_case_results) > 0:
        false_neg_rate = (len(inter_pos_case_results)
                          - sum(inter_pos_case_results)) \
                         / len(inter_pos_case_results)
    else:
        false_neg_rate = np.nan

    return false_neg_rate


def all_intersect_fnrs(subject_labels_dict, predictions, true_statuses):
    """
    Calculate false negative rates for all possible intersectional groups.

    Computes false negative rate for every combination of categories in the
    dataset (e.g., all age-group-gender combinations).

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    dict
        Dictionary mapping intersectional group names (as strings with ' + '
        separating categories) to their false negative rates.
    """
    category_names = sorted(subject_labels_dict.keys())
    unique_groups = {}
    for category in category_names:
        unique_groups[category] = sorted(set(subject_labels_dict[category]))

    all_combinations = list(product(*[unique_groups[category]
                            for category in category_names]))

    fnrs = {}
    for combination in all_combinations:
        combination_dict = {}
        for i, category_name in enumerate(category_names):
            combination_dict[category_name] = combination[i]
        intersect_fn_rate = intersect_fnr(
                                group_labels_dict=combination_dict,
                                subject_labels_dict=subject_labels_dict,
                                predictions=predictions,
                                true_statuses=true_statuses)
        intersect_group_name = " + ".join(str(group) for group in combination)
        fnrs[intersect_group_name] = intersect_fn_rate

    return fnrs


def max_intersect_fnr_diff(subject_labels_dict, predictions, true_statuses):
    fnrs = all_intersect_fnrs(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    """
    Calculate the maximum difference in false negative rate across all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The difference between the maximum and minimum false negative rate
        across all intersectional groups. Returns np.nan if any group has no
        observations.
    """
    fnrs = all_intersect_fnrs(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    fnr_values = np.array(list(fnrs.values()))

    if any(np.isnan(fnr_values)):
        max_diff = np.nan
    else:
        max_diff = max(fnr_values) - min(fnr_values)

    return max_diff


def max_intersect_fnr_ratio(subject_labels_dict, predictions, true_statuses,
                            natural_log=True):
    """
    Calculate the ratio of the maximum to minimum false negative rate across
    all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of the maximum to minimum false negative rate across
        all intersectional groups. Returns np.nan if any group has no
        observations or if any false negative rate is 0.
    """
    fnrs = all_intersect_fnrs(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    fnr_values = np.array(list(fnrs.values()))

    if any(np.isnan(fnr_values)):
        max_ratio = np.nan
    elif np.any(fnr_values == 0):
        max_ratio = np.nan
    else:
        max_ratio = max(fnr_values) / min(fnr_values)

    if natural_log is True:
        return np.log(max_ratio)
    else:
        return max_ratio


def group_fpr(group_label, subject_labels, predictions, true_statuses):
    """
    Find the false positive rate of a group with a specific label.

    Parameters
    ----------
    group_label : str or int
        The label of the group for which the false positive rate of the model
        should be evaluated.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false positive rate of the model in the specified group. Returns
        np.nan if the group has no observations.
    """
    n_samples = len(predictions)

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_group = [False] * n_samples
    for observation in range(n_samples):
        if subject_labels[observation] == group_label:
            in_group[observation] = True
    results_for_neg_cases = [acc for acc, include, truth
                             in zip(accurate_or_not, in_group, true_statuses)
                             if include is True and bool(truth) is False]

    if len(results_for_neg_cases) > 0:
        false_pos_rate = (len(results_for_neg_cases)
                          - sum(results_for_neg_cases)) \
                         / len(results_for_neg_cases)
    else:
        false_pos_rate = np.nan

    return false_pos_rate


def group_fpr_diff(group_a_label, group_b_label, subject_labels,
                   predictions, true_statuses):
    """
    Calculate the absolute difference in false positive rate between two
    groups.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The absolute difference in false positive rate between the two groups.
        Returns np.nan if either group has no observations.
    """
    group_a_fpr = group_fpr(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_fpr = group_fpr(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_fpr) or np.isnan(group_a_fpr):
        diff = np.nan
    else:
        diff = abs(group_a_fpr - group_b_fpr)

    return diff


def group_fpr_ratio(group_a_label, group_b_label, subject_labels,
                    predictions, true_statuses, natural_log=True):
    """
    Calculate the ratio of false positive rates between two groups.

    Computes the maximum of the two possible ratios (group A / group B and
    group B / group A) to ensure the ratio is always >= 1.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of false positive rates between the two groups. Returns
        np.nan if either group has no observations or if either false positive
        rate is 0.
    """
    group_a_fpr = group_fpr(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_fpr = group_fpr(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_fpr) or np.isnan(group_a_fpr):
        ratio = np.nan
    elif group_a_fpr == 0 or group_b_fpr == 0:
        ratio = np.nan
    else:
        ratio_a_b = group_a_fpr / group_b_fpr
        ratio_b_a = group_b_fpr / group_a_fpr
        ratio = max(ratio_a_b, ratio_b_a)

    if natural_log is True:
        return np.log(ratio)
    else:
        return ratio


def intersect_fpr(group_labels_dict, subject_labels_dict,
                  predictions, true_statuses):
    """
    Calculate false positive rate for an intersectional group.

    An intersectional group is defined by membership in specific categories
    across multiple dimensions (e.g., specific age category and specific
    gender).

    Parameters
    ----------
    group_labels_dict : dict
        Dictionary mapping category names to specific group labels that define
        the intersectional group (e.g., {'age': 'Older', 'gender': 'Female'}).
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false positive rate of the model in the specified intersectional
        group. Returns np.nan if the group has no observations.
    """
    n_samples = len(predictions)
    categories = sorted(group_labels_dict.keys())

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_groups = [False] * n_samples
    for observation in range(n_samples):
        category_match = []
        for category in categories:
            group = group_labels_dict[category]
            if subject_labels_dict[category][observation] == group:
                category_match.append(1)
            else:
                category_match.append(0)
        in_intersectional_group = bool(math.prod(category_match))
        if in_intersectional_group is True:
            in_groups[observation] = True

    inter_neg_case_results = [acc for acc, include, truth
                              in zip(accurate_or_not, in_groups, true_statuses)
                              if include is True and bool(truth) is False]

    if len(inter_neg_case_results) > 0:
        false_pos_rate = (len(inter_neg_case_results)
                          - sum(inter_neg_case_results)) \
                         / len(inter_neg_case_results)
    else:
        false_pos_rate = np.nan

    return false_pos_rate


def all_intersect_fprs(subject_labels_dict, predictions, true_statuses):
    """
    Calculate false positive rates for all possible intersectional groups.

    Computes false positive rate for every combination of categories in the
    dataset (e.g., all age-group-gender combinations).

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    dict
        Dictionary mapping intersectional group names (as strings with ' + '
        separating categories) to their false positive rates.
    """
    category_names = sorted(subject_labels_dict.keys())
    unique_groups = {}
    for category in category_names:
        unique_groups[category] = sorted(set(subject_labels_dict[category]))

    all_combinations = list(product(*[unique_groups[category]
                            for category in category_names]))

    fprs = {}
    for combination in all_combinations:
        combination_dict = {}
        for i, category_name in enumerate(category_names):
            combination_dict[category_name] = combination[i]
        intersect_fp_rate = intersect_fpr(
                                group_labels_dict=combination_dict,
                                subject_labels_dict=subject_labels_dict,
                                predictions=predictions,
                                true_statuses=true_statuses)
        intersect_group_name = " + ".join(str(group) for group in combination)
        fprs[intersect_group_name] = intersect_fp_rate

    return fprs


def max_intersect_fpr_diff(subject_labels_dict, predictions, true_statuses):
    """
    Calculate the maximum difference in false positive rate across all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The difference between the maximum and minimum false positive rate
        across all intersectional groups. Returns np.nan if any group has no
        observations.
    """
    fprs = all_intersect_fprs(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    fpr_values = np.array(list(fprs.values()))

    if any(np.isnan(fpr_values)):
        max_diff = np.nan
    else:
        max_diff = max(fpr_values) - min(fpr_values)

    return max_diff


def max_intersect_fpr_ratio(subject_labels_dict, predictions, true_statuses,
                            natural_log=True):
    """
    Calculate the ratio of the maximum to minimum false positive rate across all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of the maximum to minimum false positive rate across
        all intersectional groups. Returns np.nan if any group has no
        observations or if any false positive rate is 0.
    """
    fprs = all_intersect_fprs(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    fpr_values = np.array(list(fprs.values()))

    if any(np.isnan(fpr_values)):
        max_ratio = np.nan
    elif np.any(fpr_values == 0):
        max_ratio = np.nan
    else:
        max_ratio = max(fpr_values) / min(fpr_values)

    if natural_log is True:
        return np.log(max_ratio)
    else:
        return max_ratio


def group_for(group_label, subject_labels, predictions, true_statuses):
    """
    Find the false omission rate of a group with a specific label.

    Parameters
    ----------
    group_label : str or int
        The label of the group for which the false omission rate of the model
        should be evaluated.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false omission rate of the model in the specified group. Returns
        np.nan if the group has no observations.
    """
    n_samples = len(predictions)

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_group = [False] * n_samples
    for observation in range(n_samples):
        if subject_labels[observation] == group_label:
            in_group[observation] = True
    group_neg_results = [acc for acc, include, pos
                         in zip(accurate_or_not, in_group, predictions)
                         if include is True and bool(pos) is False]

    if len(group_neg_results) > 0:
        false_omi_rate = (len(group_neg_results)-sum(group_neg_results)) \
                         / len(group_neg_results)
    else:
        false_omi_rate = np.nan

    return false_omi_rate


def group_for_diff(group_a_label, group_b_label, subject_labels,
                   predictions, true_statuses):
    """
    Calculate the absolute difference in false omission rate between two
    groups.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The absolute difference in false omission rate between the two groups.
        Returns np.nan if either group has no observations.
    """
    group_a_for = group_for(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_for = group_for(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_for) or np.isnan(group_b_for):
        diff = np.nan
    else:
        diff = abs(group_a_for - group_b_for)

    return diff


def group_for_ratio(group_a_label, group_b_label, subject_labels,
                    predictions, true_statuses, natural_log=True):
    """
    Calculate the ratio of false omission rates between two groups.

    Computes the maximum of the two possible ratios (group A / group B and
    group B / group A) to ensure the ratio is always >= 1.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of false omission rates between the two groups. Returns
        np.nan if either group has no observations or if either false omission
        rate is 0.
    """
    group_a_for = group_for(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_for = group_for(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_for) or np.isnan(group_b_for):
        ratio = np.nan
    elif group_a_for == 0 or group_b_for == 0:
        ratio = np.nan
    else:
        ratio_a_b = group_a_for / group_b_for
        ratio_b_a = group_b_for / group_a_for
        ratio = max(ratio_a_b, ratio_b_a)

    if natural_log is True:
        return np.log(ratio)
    else:
        return ratio


def intersect_for(group_labels_dict, subject_labels_dict,
                  predictions, true_statuses):
    """
    Calculate false omission rate for an intersectional group.

    An intersectional group is defined by membership in specific categories
    across multiple dimensions (e.g., specific age category and specific
    gender).

    Parameters
    ----------
    group_labels_dict : dict
        Dictionary mapping category names to specific group labels that define
        the intersectional group (e.g., {'age': 'Older', 'gender': 'Female'}).
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false omission rate of the model in the specified intersectional
        group. Returns np.nan if the group has no observations.
    """
    n_samples = len(predictions)
    categories = sorted(group_labels_dict.keys())

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_groups = [False] * n_samples
    for observation in range(n_samples):
        category_match = []
        for category in categories:
            group = group_labels_dict[category]
            if subject_labels_dict[category][observation] == group:
                category_match.append(1)
            else:
                category_match.append(0)
        in_intersectional_group = bool(math.prod(category_match))
        if in_intersectional_group is True:
            in_groups[observation] = True

    inter_neg_results = [acc for acc, include, pos
                         in zip(accurate_or_not, in_groups, predictions)
                         if include is True and bool(pos) is False]

    if len(inter_neg_results) > 0:
        false_omi_rate = (len(inter_neg_results)-sum(inter_neg_results)) \
                          / len(inter_neg_results)
    else:
        false_omi_rate = np.nan

    return false_omi_rate


def all_intersect_fors(subject_labels_dict, predictions, true_statuses):
    """
    Calculate false omission rates for all possible intersectional groups.

    Computes false omission rate for every combination of categories in the
    dataset (e.g., all age-group-gender combinations).

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    dict
        Dictionary mapping intersectional group names (as strings with ' + '
        separating categories) to their false omission rates.
    """
    category_names = sorted(subject_labels_dict.keys())
    unique_groups = {}
    for category in category_names:
        unique_groups[category] = sorted(set(subject_labels_dict[category]))

    all_combinations = list(product(*[unique_groups[category]
                            for category in category_names]))

    fors = {}
    for combination in all_combinations:
        combination_dict = {}
        for i, category_name in enumerate(category_names):
            combination_dict[category_name] = combination[i]
        intersect_fo_rate = intersect_for(
                                group_labels_dict=combination_dict,
                                subject_labels_dict=subject_labels_dict,
                                predictions=predictions,
                                true_statuses=true_statuses)
        intersect_group_name = " + ".join(str(group) for group in combination)
        fors[intersect_group_name] = intersect_fo_rate

    return fors


def max_intersect_for_diff(subject_labels_dict, predictions, true_statuses):
    """
    Calculate the maximum difference in false omission rate across all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The difference between the maximum and minimum false omission rate
        across all intersectional groups. Returns np.nan if any group has no
        observations.
    """
    fors = all_intersect_fors(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    for_values = np.array(list(fors.values()))

    if any(np.isnan(for_values)):
        max_diff = np.nan
    else:
        max_diff = max(for_values) - min(for_values)

    return max_diff


def max_intersect_for_ratio(subject_labels_dict, predictions, true_statuses,
                            natural_log=True):
    """
    Calculate the ratio of the maximum to minimum false omission rate across all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of the maximum to minimum false omission rate across
        all intersectional groups. Returns np.nan if any group has no
        observations or if any false omission rate is 0.
    """
    fors = all_intersect_fors(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    for_values = np.array(list(fors.values()))

    if any(np.isnan(for_values)):
        max_ratio = np.nan
    elif np.any(for_values == 0):
        max_ratio = np.nan
    else:
        max_ratio = max(for_values) / min(for_values)

    if natural_log is True:
        return np.log(max_ratio)
    else:
        return max_ratio


def group_fdr(group_label, subject_labels, predictions, true_statuses):
    """
    Find the false discovery rate of a group with a specific label.

    Parameters
    ----------
    group_label : str or int
        The label of the group for which the false discovery rate of the model
        should be evaluated.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false discovery rate of the model in the specified group. Returns
        np.nan if the group has no observations.
    """
    n_samples = len(predictions)

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_group = [False] * n_samples
    for observation in range(n_samples):
        if subject_labels[observation] == group_label:
            in_group[observation] = True
    group_pos_results = [acc for acc, include, pos
                         in zip(accurate_or_not, in_group, predictions)
                         if include is True and bool(pos) is True]

    if len(group_pos_results) > 0:
        false_dis_rate = (len(group_pos_results)-sum(group_pos_results)) \
                         / len(group_pos_results)
    else:
        false_dis_rate = np.nan

    return false_dis_rate


def group_fdr_diff(group_a_label, group_b_label, subject_labels,
                   predictions, true_statuses):
    """
    Calculate the absolute difference in false discovery rate between two
    groups.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The absolute difference in false discovery rate between the two groups.
        Returns np.nan if either group has no observations.
    """
    group_a_fdr = group_fdr(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_fdr = group_fdr(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_fdr) or np.isnan(group_b_fdr):
        diff = np.nan
    else:
        diff = abs(group_a_fdr - group_b_fdr)

    return diff


def group_fdr_ratio(group_a_label, group_b_label, subject_labels,
                    predictions, true_statuses, natural_log=True):
    """
    Calculate the ratio of false discovery rates between two groups.

    Computes the maximum of the two possible ratios (group A / group B and
    group B / group A) to ensure the ratio is always >= 1.

    Parameters
    ----------
    group_a_label : str or int
        The label of the first group.
    group_b_label : str or int
        The label of the second group.
    subject_labels : dict
        A dictionary containing subject labels for every observation in the
        evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of false discovery rates between the two groups.
        Returns np.nan if either group has no observations or if either false
        discovery rate is 0.
    """
    group_a_fdr = group_fdr(group_label=group_a_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)
    group_b_fdr = group_fdr(group_label=group_b_label,
                            subject_labels=subject_labels,
                            predictions=predictions,
                            true_statuses=true_statuses)

    if np.isnan(group_a_fdr) or np.isnan(group_b_fdr):
        ratio = np.nan
    elif group_a_fdr == 0 or group_b_fdr == 0:
        ratio = np.nan
    else:
        ratio_a_b = group_a_fdr / group_b_fdr
        ratio_b_a = group_b_fdr / group_a_fdr
        ratio = max(ratio_a_b, ratio_b_a)

    if natural_log is True:
        return np.log(ratio)
    else:
        return ratio


def intersect_fdr(group_labels_dict, subject_labels_dict,
                  predictions, true_statuses):
    """
    Calculate false discovery rate for an intersectional group.

    An intersectional group is defined by membership in specific categories
    across multiple dimensions (e.g., specific age category and specific
    gender).

    Parameters
    ----------
    group_labels_dict : dict
        Dictionary mapping category names to specific group labels that define
        the intersectional group (e.g., {'age': 'Older', 'gender': 'Female'}).
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The false discovery rate of the model in the specified intersectional
        group. Returns np.nan if the group has no observations.
    """
    n_samples = len(predictions)
    categories = sorted(group_labels_dict.keys())

    accurate_or_not = [pred == truth
                       for pred, truth
                       in zip(predictions, true_statuses)]

    in_groups = [False] * n_samples
    for observation in range(n_samples):
        category_match = []
        for category in categories:
            group = group_labels_dict[category]
            if subject_labels_dict[category][observation] == group:
                category_match.append(1)
            else:
                category_match.append(0)
        in_intersectional_group = bool(math.prod(category_match))
        if in_intersectional_group is True:
            in_groups[observation] = True

    inter_pos_results = [acc for acc, include, pos
                         in zip(accurate_or_not, in_groups, predictions)
                         if include is True and bool(pos) is True]

    if len(inter_pos_results) > 0:
        false_dis_rate = (len(inter_pos_results)-sum(inter_pos_results)) \
                          / len(inter_pos_results)
    else:
        false_dis_rate = np.nan

    return false_dis_rate


def all_intersect_fdrs(subject_labels_dict, predictions, true_statuses):
    """
    Calculate false discovery rates for all possible intersectional groups.

    Computes false discovery rate for every combination of categories in the
    dataset (e.g., all age-group-gender combinations).

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    dict
        Dictionary mapping intersectional group names (as strings with ' + '
        separating categories) to their false discovery rates.
    """
    category_names = sorted(subject_labels_dict.keys())
    unique_groups = {}
    for category in category_names:
        unique_groups[category] = sorted(set(subject_labels_dict[category]))

    all_combinations = list(product(*[unique_groups[category]
                            for category in category_names]))

    fdrs = {}
    for combination in all_combinations:
        combination_dict = {}
        for i, category_name in enumerate(category_names):
            combination_dict[category_name] = combination[i]
        intersect_fd_rate = intersect_fdr(
                                group_labels_dict=combination_dict,
                                subject_labels_dict=subject_labels_dict,
                                predictions=predictions,
                                true_statuses=true_statuses)
        intersect_group_name = " + ".join(str(group) for group in combination)
        fdrs[intersect_group_name] = intersect_fd_rate

    return fdrs


def max_intersect_fdr_diff(subject_labels_dict, predictions, true_statuses):
    """
    Calculate the maximum difference in false discovery rate across all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.

    Returns
    -------
    float
        The difference between the maximum and minimum false discovery rate
        across all intersectional groups. Returns np.nan if any group has no
        observations.
    """
    fdrs = all_intersect_fdrs(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    fdr_values = np.array(list(fdrs.values()))

    if any(np.isnan(fdr_values)):
        max_diff = np.nan
    else:
        max_diff = max(fdr_values) - min(fdr_values)

    return max_diff


def max_intersect_fdr_ratio(subject_labels_dict, predictions, true_statuses,
                            natural_log=True):
    """
    Calculate the ratio of the maximum to minimum false discovery rate across
    all intersectional groups.

    Parameters
    ----------
    subject_labels_dict : dict
        Dictionary mapping category names to lists of labels for each
        observation in the evaluation dataset.
    predictions : list[bool]
        A list of predicted diagnoses for each observation in the
        evaluation dataset.
    true_statuses : list[bool]
        A list of true diagnoses for each observation in the
        evaluation dataset.
    natural_log : bool, optional
        If True, return the natural logarithm of the ratio. Default is True.

    Returns
    -------
    float
        The (log) ratio of the maximum to minimum false discovery rate across
        all intersectional groups. Returns np.nan if any group has no
        observations or if any false discovery rate is 0.
    """
    fdrs = all_intersect_fdrs(subject_labels_dict=subject_labels_dict,
                              predictions=predictions,
                              true_statuses=true_statuses)
    fdr_values = np.array(list(fdrs.values()))

    if any(np.isnan(fdr_values)):
        max_ratio = np.nan
    elif np.any(fdr_values == 0):
        max_ratio = np.nan
    else:
        max_ratio = max(fdr_values) / min(fdr_values)

    if natural_log is True:
        return np.log(max_ratio)
    else:
        return max_ratio
