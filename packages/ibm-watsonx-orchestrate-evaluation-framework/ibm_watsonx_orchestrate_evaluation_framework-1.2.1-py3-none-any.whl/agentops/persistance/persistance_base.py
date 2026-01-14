from abc import ABC, abstractmethod
from typing import Any, List

from agentops.collection.collection_base import CollectionBase
from agentops.metrics.metrics import EvaluatorData


class PersistanceBase(ABC):
    @abstractmethod
    def persist(
        self,
        evaluation_results: List[EvaluatorData],
        experiment_results,
        collection: CollectionBase,
        experiment_id: str = None,
        **kwargs,
    ):
        pass

    def persist_aggregated_metrics(
        self, aggregated_metrics: List[EvaluatorData], **kwargs
    ):
        # Not implemented for ArizePersistance because Arize automatically aggregates metrics.
        pass

    def clean(self):
        pass
