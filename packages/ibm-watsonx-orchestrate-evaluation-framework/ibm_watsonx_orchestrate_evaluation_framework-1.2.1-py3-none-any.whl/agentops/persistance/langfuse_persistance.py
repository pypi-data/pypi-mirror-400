from typing import List

from langfuse import get_client

from agentops.metrics.metrics import EvaluatorData
from agentops.persistance.persistance_base import PersistanceBase
from agentops.utils.rich_utils import RichLogger

CLIENT = None

logger = RichLogger(__name__)


class LangfusePersistance(PersistanceBase):
    def __init__(self):
        if CLIENT is None:
            self.client = get_client()
        else:
            self.client = CLIENT

    def _sync_metrics(
        self,
        name: str,
        value: float,
        data_type: str,
        metadata: dict,
        session_id: str = None,
        dataset_run_id: str = None,
    ):

        try:
            if session_id:
                self.client.create_score(
                    name=name,
                    session_id=session_id,
                    value=value,
                    data_type=data_type,
                    metadata=metadata,
                )
            elif dataset_run_id:
                self.client.create_score(
                    name=name,
                    dataset_run_id=dataset_run_id,
                    value=value,
                    data_type=data_type,
                    metadata=metadata,
                )
            else:
                raise Exception(
                    "`dataset_run_id` or `session_id` must be passed"
                )

        except Exception as e:
            logger.error(
                f"Uploading {name} with value {value} failed with exception {e}"
            )

    def persist(
        self,
        evaluation_results: List[List[EvaluatorData]],
        experiment_results,
        experiment_id: str = None,
        **kwargs,
    ):
        session_ids = [
            entry.output for entry in experiment_results.item_results
        ]

        for idx, evaluation_result in enumerate(evaluation_results):
            session_id = session_ids[idx]
            for result in evaluation_result:
                name = result["eval_name"]
                value = result["value"]
                data_type = result["data_type"]
                metadata = result["metadata"]

                self._sync_metrics(name, value, data_type, metadata, session_id)

    def persist_aggregated_metrics(
        self, aggregated_metrics: List[EvaluatorData], **kwargs
    ):
        for metric in aggregated_metrics:
            self._sync_metrics(
                name=metric.eval_name,
                value=metric.value,
                data_type=metric.data_type,
                metadata=metric.metadata,
                dataset_run_id=metric.metadata.get("experiment_id"),
            )
