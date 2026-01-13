

def unpack_eval_df(eval_df):
    """
    Convert eval_df into the list inputs expected by group_* metric functions.

    Expects eval_df columns:
      - subject_label (str)
      - y_pred (0/1)
      - y_true (0/1)

    Returns
    -------
    subject_labels : list[str]
    predictions    : list[int]
    true_statuses  : list[int]
    """
    subject_labels = eval_df["subject_label"].astype(str).tolist()

    # cast to plain Python int so you don't see np.int64 everywhere
    predictions = [int(x) for x in eval_df["y_pred"].to_list()]
    true_statuses = [int(x) for x in eval_df["y_true"].to_list()]

    return subject_labels, predictions, true_statuses


def make_subject_labels_dict(df_test, protected_cols):
    """
    Build the dict-of-lists format expected by intersect_* functions.

    Parameters
    ----------
    df_test : pd.DataFrame
        Test-set DataFrame containing the protected columns.
    protected_cols : list[str]
        E.g. ["Sex", "age_group"]

    Returns
    -------
    dict[str, list]
        {col: list_of_values_aligned_rowwise_with_eval_df}
    """
    return {col: df_test[col].tolist() for col in protected_cols}
