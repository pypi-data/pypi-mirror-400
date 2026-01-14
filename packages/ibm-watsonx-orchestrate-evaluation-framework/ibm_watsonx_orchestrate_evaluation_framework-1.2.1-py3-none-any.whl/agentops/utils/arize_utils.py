def build_arize_experiment_id(dataset_id: str) -> str:
    """
    Build the experiment model_id from a dataset_id.    Arize experiment traces use a model_id format:
    "experiment_traces_for_dataset_{dataset_id}"

    Args:
        dataset_id: The Arize dataset ID

    Returns:
        The experiment model_id string (e.g. "experiment_traces_for_dataset_{dataset_id}")
    """
    return f"experiment_traces_for_dataset_{dataset_id}"
