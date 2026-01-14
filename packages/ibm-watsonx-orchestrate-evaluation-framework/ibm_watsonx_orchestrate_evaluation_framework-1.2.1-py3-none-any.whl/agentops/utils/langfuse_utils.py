import rich
from langfuse import get_client


def sync(
    name, value, data_type, metadata, session_id=None, dataset_run_id=None
):
    LANGFUSE_CLIENT = get_client()
    if session_id:
        try:
            LANGFUSE_CLIENT.create_score(
                name=name,
                session_id=session_id,
                value=value,
                data_type=data_type,
                metadata=metadata,
            )
        except Exception as e:
            rich.print(
                f"[r] Uploading {name} with value {value} failed with exception {e}"
            )
    elif dataset_run_id:
        try:
            LANGFUSE_CLIENT.create_score(
                name=name,
                dataset_run_id=dataset_run_id,
                value=value,
                data_type=data_type,
                metadata=metadata,
            )
        except Exception as e:
            rich.print(
                f"[r] Uploading {name} with value {value} failed with exception {e}"
            )
    else:
        raise Exception("`dataset_run_id` or `session_id` must be passed")
