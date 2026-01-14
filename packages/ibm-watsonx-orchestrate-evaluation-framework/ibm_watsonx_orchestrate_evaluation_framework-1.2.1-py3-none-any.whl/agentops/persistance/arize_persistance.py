import os
from collections import defaultdict
from typing import Any, Dict, List

import pandas as pd
from arize.experimental.datasets import ArizeDatasetsClient
from arize.experimental.datasets.experiments.types import (
    EvaluationResultColumnNames,
    ExperimentTaskResultColumnNames,
)

from agentops.collection.collection_base import CollectionBase
from agentops.metrics.metrics import EvaluatorData
from agentops.persistance.persistance_base import PersistanceBase
from agentops.utils.rich_utils import RichLogger

logger = RichLogger(__name__)

CLIENT = None


class ArizePersistance(PersistanceBase):
    def __init__(self):
        if CLIENT is None:
            self.client = ArizeDatasetsClient(
                api_key=os.getenv("ARIZE_API_KEY")
            )
        else:
            self.client = CLIENT

    def persist(
        self,
        evaluation_results: List[List[EvaluatorData]],
        experiment_results,
        collection: CollectionBase,
        experiment_id: str = None,
        **kwargs,
    ):
        """
        Persist experiment results to Arize.

        Args:
            evaluation_results: EvaluatorData containing metrics data.
                evaluation_results.eval_name and evaluation_results.value
            experiment_results: ExperimentResult containing metrics data.
            collection: CollectionBase containing the dataset_id and dataset_name
            **kwargs: Additional arguments (e.g., experiment_results_df to populate)
        """

        dataset_id = collection.dataset_id
        dataset_name = collection.name

        session_ids = experiment_results["result"].tolist()
        logger.info(f"Session IDs: {session_ids}")

        metric_names = set(
            result["eval_name"]
            for evaluation in evaluation_results
            for result in evaluation
        )

        metrics = defaultdict(list)
        for idx, evaluation_result in enumerate(evaluation_results):
            session_id = session_ids[idx]
            for result in evaluation_result:
                name = result["eval_name"]
                value = result["value"]
                data_type = result["data_type"]
                metadata = result["metadata"]

                # TODO: come back to this
                # TODO: how to handle categorical values?
                if isinstance(value, bool):
                    value = int(value)

                metrics[name].append(value)

        df = pd.DataFrame(metrics)
        evaluator_columns = self._create_evaluation_columns(metric_names)
        experiment_df = pd.concat([experiment_results, df], axis=1)

        logged_experiment_id = self.client.log_experiment(
            space_id=os.getenv("ARIZE_SPACE_ID"),
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            experiment_name=experiment_id,
            experiment_df=experiment_df,
            task_columns=self._create_task_columns(),
            evaluator_columns=evaluator_columns,
        )
        return logged_experiment_id

    def _create_evaluation_columns(self, metric_names) -> Dict[str, List[Any]]:
        evaluator_columns = {}
        for name in metric_names:
            evaluator_columns[name] = EvaluationResultColumnNames(
                score=name,
            )
        return evaluator_columns

    def _create_task_columns(self) -> ExperimentTaskResultColumnNames:
        # TODO: come back to this
        task_columns = ExperimentTaskResultColumnNames(
            example_id="example_id",  # Column with dataset example IDs
            result="result",  # Column with task output
        )

        return task_columns
