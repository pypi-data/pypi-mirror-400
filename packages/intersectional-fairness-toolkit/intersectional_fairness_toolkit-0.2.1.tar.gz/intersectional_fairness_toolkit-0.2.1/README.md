# Intersectional Fairness Toolkit for Health Machine Learning

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Raiet-Bekirov/HPDM139_assignment/HEAD?urlpath=%2Fdoc%2Ftree%2Fexamples%2Fuci_heart_demo.ipynb)

This project provides a Python package for evaluating intersectional fairness in machine learning models applied to tabular health datasets. It supports the construction of intersectional protected groups (e.g. sex × age group) and the computation of fairness metrics such as Differential Fairness.

The toolkit is designed to be dataset-agnostic and model-agnostic, making it suitable for use in a wide range of health data science workflows.


## Fairness

Fairness in machine learning refers to the ethical requirement that models do not produce systematically biased or discriminatory outcomes for individuals or groups. In the context of health data science, unfair models may lead to unequal access to diagnosis, treatment, or follow-up.


Bias can arise when model predictions differ across protected attributes such as sex, age, ethnicity, or disability status. A growing number of tools exist to help researchers and practitioners evaluate fairness in machine learning models; however, many focus on single protected attributes in isolation.


## Intersectional Fairness

This package provides tools which allow researchers to evaluate fairness across intersections of protected attributes ([Foulds, 2019](https://arxiv.org/abs/1807.08362)), rather than considering each attribute independently.

For example, instead of checking:
- men vs women
- younger vs older patients

We check:
- young women
- older women
- young men
- older men

This approach is motivated by the observation that unfairness can be hidden when outcomes are averaged over broad groups. Disparities often emerge at the intersections of attributes, where individuals may experience compounded or 'double' disadvantage. For instance, older women may be treated less favourably than either women or older patients considered as marginal groups alone.

In this package, intersectional groups are evaluated using differential fairness metrics to quantify worst-case disparities in model outcomes.

## Installation

Install from TestPyPI (recommended):

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple intersectional-fairness-toolkit==0.1.3
```

Alternatively, clone the repository and install the package in editable mode:

```bash
git clone https://github.com/Raiet-Bekirov/HPDM139_assignment.git
cd HPDM139_assignment
pip install -e .
```

## Example usage

The example below demonstrates a typical workflow:
loading a clinical dataset, training a simple classifier, and evaluating
intersectional fairness metrics. The toolkit is model-agnostic and can be used
with any scikit-learn–compatible estimator.

```python
from fairness.data import load_heart_csv
from fairness.preprocess import add_age_group, preprocess_tabular, make_train_test_split
from fairness.groups import make_eval_df
from fairness.adapters import unpack_eval_df
from fairness.metrics import group_acc_ratio 
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# 1) Load dataset and add protected attributes
df = load_heart_csv("data/heart.csv")
df = add_age_group(df)

# 2) Prepare features for modelling
df_model = preprocess_tabular(df)

# 3) Train/test split
split = make_train_test_split(df_model, target_col="HeartDisease", stratify=True)

# 4) Train a simple model (example)
model = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=2000))
])
model.fit(split.X_train, split.y_train)
y_pred = model.predict(split.X_test)

# 5) Align predictions, labels, and protected attributes
df_test = df.loc[split.X_test.index] 
eval_df = make_eval_df(
    df_test=df_test,
    protected=["Sex", "age_group"],
    y_pred=y_pred,
    y_true=split.y_test.to_numpy(),
)

# 6) Compute intersectional fairness metric

subject_labels, predictions, true_statuses = unpack_eval_df(eval_df)

acc = group_acc_ratio(
    "Sex=0|age_group=older",
    "Sex=1|age_group=older",
    subject_labels,
    predictions,
    true_statuses,
    natural_log=True
)
print("Accuracy ratio:", acc)
```

A complete end-to-end example using the UCI Heart Disease dataset is provided at [`examples/uci_heart_demo.ipynb`](https://github.com/Raiet-Bekirov/HPDM139_assignment/blob/main/examples/uci_heart_demo.ipynb)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Raiet-Bekirov/HPDM139_assignment/HEAD?urlpath=%2Fdoc%2Ftree%2Fexamples%2Fuci_heart_demo.ipynb)

## Documentation

The following documentation is provided:

- [Tutorial](https://raiet-bekirov.github.io/HPDM139_assignment/tutorial/) 
- [API reference](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/)
- [Data loading and preprocessing demo](https://github.com/Raiet-Bekirov/HPDM139_assignment/blob/main/examples/data_demo.ipynb)
- [Metrics useage demo](https://github.com/Raiet-Bekirov/HPDM139_assignment/blob/main/examples/single_metrics_demo.ipynb)


## Fairness Metrics Supported

| Metric function                                                                                                                             | Purpose                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| [`group_acc`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_acc)                                 | Find the accuracy of a group with a specific label                                    |
| [`group_acc_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_acc_diff)                       | Calculate the absolute difference in accuracy between two groups                      |
| [`group_acc_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_acc_ratio)                     | Calculate the ratio of accuracies between two groups                                  |
| [`intersect_acc`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.intersect_acc)                         | Calculate accuracy for an intersectional group                                        |
| [`all_intersect_accs`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.all_intersect_accs)               | Calculate accuracies for all possible intersectional groups                           |
| [`max_intersect_acc_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_acc_diff)       | Calculate the maximum difference in accuracy across intersectional groups             |
| [`max_intersect_acc_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_acc_ratio)     | Calculate the maximum ratio of accuracies across intersectional groups                |
| [`group_fnr`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fnr)                                 | Find the false negative rate of a group with a specific label                         |
| [`group_fnr_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fnr_diff)                       | Absolute difference in false negative rate between two groups                         |
| [`group_fnr_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fnr_ratio)                     | Calculate the ratio of false negative rates between two groups                        |
| [`intersect_fnr`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.intersect_fnr)                         | Calculate false negative rate for an intersectional group                             |
| [`all_intersect_fnrs`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.all_intersect_fnrs)               | Calculate false negative rates for all possible intersectional groups                 |
| [`max_intersect_fnr_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_fnr_diff)       | Calculate the maximum difference in false negative rate across intersectional groups  |
| [`max_intersect_fnr_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_fnr_ratio)     | Calculate the maximum ratio of false negative rates across intersectional groups      |
| [`group_fpr`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fpr)                                 | Find the false positive rate of a group with a specific label                         |
| [`group_fpr_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fpr_diff)                       | Absolute difference in false positive rate between two groups                         |
| [`group_fpr_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fpr_ratio)                     | Calculate the ratio of false positive rates between two groups                        |
| [`intersect_fpr`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.intersect_fpr)                         | Calculate false positive rate for an intersectional group                             |
| [`all_intersect_fprs`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.all_intersect_fprs)               | Calculate false positive rates for all possible intersectional groups                 |
| [`max_intersect_fpr_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_fpr_diff)       | Calculate the maximum difference in false positive rate across intersectional groups  |
| [`max_intersect_fpr_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_fpr_ratio)     | Calculate the maximum ratio of false positive rates across intersectional groups      |
| [`group_for`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_for)                                 | Find the false omission rate of a group with a specific label                         |
| [`group_for_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_for_diff)                       | Absolute difference in false omission rate between two groups                         |
| [`group_for_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_for_ratio)                     | Calculate the ratio of false omission rates between two groups                        |
| [`intersect_for`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.intersect_for)                         | Calculate false omission rate for an intersectional group                             |
| [`all_intersect_fors`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.all_intersect_fors)               | Calculate false omission rates for all possible intersectional groups                 |
| [`max_intersect_for_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_for_diff)       | Calculate the maximum difference in false omission rate across intersectional groups  |
| [`max_intersect_for_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_for_ratio)     | Calculate the maximum ratio of false omission rates across intersectional groups      |
| [`group_fdr`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fdr)                                 | Find the false discovery rate of a group with a specific label                        |
| [`group_fdr_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fdr_diff)                       | Absolute difference in false discovery rate between two groups                        |
| [`group_fdr_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.group_fdr_ratio)                     | Calculate the ratio of false discovery rates between two groups                       |
| [`intersect_fdr`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.intersect_fdr)                         | Calculate false discovery rate for an intersectional group                            |
| [`all_intersect_fdrs`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.all_intersect_fdrs)               | Calculate false discovery rates for all possible intersectional groups                |
| [`max_intersect_fdr_diff`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_fdr_diff)       | Calculate the maximum difference in false discovery rate across intersectional groups |
| [`max_intersect_fdr_ratio`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.metrics.max_intersect_fdr_ratio)     | Calculate the maximum ratio of false discovery rates across intersectional groups     |
| [`group_to_binary`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.single_metrics.group_to_binary)                     | Wrap single-group fairness functions so they work with intersectional groups          |
| [`calculate_TP_FN_FP_TN`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.single_metrics.calculate_tp_fn_fp_tn)         | Compute confusion-matrix counts (TP, FN, FP, TN)                                      |
| [`calculate_TPR_TNR_FPR_FNR`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.single_metrics.calculate_tpr_tnr_fpr_fnr) | Compute rate metrics (TPR, TNR, FPR, FNR) from confusion-matrix counts                |
| [`calculate_EOD`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.single_metrics.calculate_eod)                         | Equal Opportunity Difference between demographic groups                               |
| [`calculate_AOD`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.single_metrics.calculate_aod)                         | Average Odds Difference between demographic groups                                    |
| [`calculate_DI`](https://raiet-bekirov.github.io/HPDM139_assignment/api_reference/#fairness.single_metrics.calculate_di)                           | Disparate Impact between demographic groups                                           |


## Project context

This package was developed as part of the HPDM139 module (Health Data Science) at the University of Exeter.

- [Design decisions](https://raiet-bekirov.github.io/HPDM139_assignment/design_decisions/)

## Reference

- Foulds, J. R., Islam, R., Keya, K. N., & Pan, S. (2019).
An intersectional definition of fairness. Proceedings of the 2019 AAAI/ACM Conference on AI, Ethics, and Society, 191–198.
https://doi.org/10.1145/3306618.3314287 (Accessed at https://arxiv.org/abs/1807.08362 )

## License

Apache-2.0 license
