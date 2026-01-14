import json
from abc import ABC, abstractmethod
from typing import Any, List, Mapping, Union

from agentops.type import CollectionModel, DatasetModel
from agentops.utils.rich_utils import RichLogger

logger = RichLogger(__name__)


class CollectionBase(ABC):
    def __init__(
        self, name: str, description: str = "", metadata: Mapping[str, str] = {}
    ):
        self.name = name
        self.description = description
        self.metadata = metadata

    @property
    def dataset_id(self) -> str:
        return ""

    @abstractmethod
    def _process_item(self, item: Mapping[str, Any]) -> DatasetModel:
        pass

    def _filter_available_datasets(
        self, collection: CollectionModel, overwrite: bool = False
    ) -> List[int]:
        available_datasets = [
            self._process_item(item) for item in self.get_data_items()
        ]
        indices_to_upload = []
        for idx, dataset in enumerate(collection.datasets):
            if (not overwrite) and dataset in available_datasets:
                logger.info(
                    f"[g]Skipping upload! Dataset already available in collection '{collection.collection_name}'"
                )
                continue
            indices_to_upload.append(idx)
        return indices_to_upload

    def _read_dataset(self, paths: Union[str, List[str]]) -> CollectionModel:
        datasets = []
        if isinstance(paths, str):
            paths = [paths]

        for path in paths:
            with open(path, encoding="utf-8") as f:
                dataset = json.load(f)
                dataset = DatasetModel(
                    starting_sentence=dataset.get("starting_sentence", ""),
                    story=dataset.get("story", ""),
                    goals=dataset.get("goals"),
                    goal_details=dataset.get("goal_details"),
                    agent=dataset.get("agent"),
                )
                datasets.append(dataset)

        collection = CollectionModel(
            collection_name=self.name,
            collection_description=self.description,
            datasets=datasets,
            metadata=self.metadata,
        )

        return collection

    @abstractmethod
    def get_dataset(self):
        pass

    @abstractmethod
    def get_data_items(self):
        pass

    @abstractmethod
    def upload(self, paths: Union[str, List[str]], overwrite: bool = False):
        pass

    @abstractmethod
    def delete_item(self, item_id: str):
        pass

    @abstractmethod
    def delete_all_items(self):
        pass
