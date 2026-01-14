import json
from typing import Any, List, Mapping, Union

from langfuse._client.datasets import DatasetItemClient
from langfuse.api.core.api_error import ApiError

from agentops.collection.collection_base import CollectionBase
from agentops.type import DatasetModel, GoalDetail
from agentops.utils.rich_utils import RichLogger

logger = RichLogger(__name__)


class LangfuseCollection(CollectionBase):
    def _process_item(self, item: Mapping[str, Any]) -> DatasetModel:
        input = item.input
        output = item.expected_output

        return DatasetModel(
            agent=input["agent"],
            starting_sentence=input["starting_sentence"],
            story=input["story"],
            goals=output["goals"],
            goal_details=[
                GoalDetail.model_validate(goal)
                for goal in output["goal_details"]
            ],
        )

    def init_client(self):
        from langfuse import get_client

        return get_client()

    def get_dataset(self):
        langfuse_client = self.init_client()
        return langfuse_client.get_dataset(self.name)

    def get_data_items(self) -> List[DatasetItemClient]:
        dataset = self.get_dataset()
        return dataset.items

    def upload(self, paths: Union[str, List[str]], overwrite: bool = False):
        langfuse_client = self.init_client()

        collection = self._read_dataset(paths)

        logger.info(
            f"Uploading {len(collection.datasets)} datasets to '{collection.collection_name}'"
        )
        langfuse_client.create_dataset(
            name=collection.collection_name,
            description=collection.collection_description,
            metadata=collection.metadata,
        )

        indices_to_upload = self._filter_available_datasets(
            collection, overwrite
        )
        for index in indices_to_upload:
            dataset = collection.datasets[index]
            langfuse_client.create_dataset_item(
                dataset_name=collection.collection_name,
                input=dataset.input,
                expected_output=dataset.output,
            )

    def delete_item(self, item_id):
        """
        Deletes a single item given its id
        """
        langfuse_client = self.init_client()
        langfuse_client.api.dataset_items.delete(id=item_id)
        logger.info(f"Deleted item {item_id} from '{self.name}'")

    def delete_all_items(self):
        """
        Deletes all items in the collection
        """
        try:
            items = self.get_data_items()
        except ApiError as e:
            if (
                e.status_code == 404
                and e.body["message"] == "Dataset not found"
            ):
                logger.error(
                    "Dataset not found. No delete operation performed."
                )
                items = []
            else:
                # re-raise exception if the error is something other than dataset not found
                raise e

        n_items = 0
        for item in items:
            self.delete_item(item.id)
            n_items += 1
        logger.info(f"Deleted {n_items} datasets from '{self.name}'")
