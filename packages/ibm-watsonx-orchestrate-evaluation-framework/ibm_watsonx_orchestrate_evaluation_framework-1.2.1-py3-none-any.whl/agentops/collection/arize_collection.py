import json
import os
from functools import cached_property
from typing import Any, List, Mapping, Optional, Union

import pandas as pd
import rich
from arize.experimental.datasets.utils.constants import GENERATIVE

from agentops.collection.collection_base import CollectionBase
from agentops.type import DatasetModel, GoalDetail
from agentops.utils.rich_utils import RichLogger

logger = RichLogger(__name__)


class ArizeCollection(CollectionBase):
    @cached_property
    def dataset_id(self):
        list_datasets = self.init_client().list_datasets(
            space_id=self.space_id,
        )

        filtered_datasets = list_datasets[
            list_datasets["dataset_name"] == self.name
        ]
        if filtered_datasets.empty:
            return None
            # raise ValueError(f"Dataset {self.name} does not exist. Please upload the dataset first using the `upload` method.")

        return filtered_datasets["dataset_id"].values[0]

    @property
    def space_id(self):
        return os.getenv("ARIZE_SPACE_ID")

    @property
    def api_key(self):
        return os.getenv("ARIZE_API_KEY")

    def _process_item(self, item: Mapping[str, Any]) -> DatasetModel:
        input = json.loads(item.input)
        output = json.loads(item.expected_output)

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
        from arize.experimental.datasets import ArizeDatasetsClient

        return ArizeDatasetsClient(api_key=self.api_key)

    def upload(self, paths: Union[str, List[str]], overwrite: bool = False):
        client = self.init_client()
        collection = self._read_dataset(paths)

        logger.info(
            f"Uploading {len(collection.datasets)} datasets to '{collection.collection_name}'"
        )

        indices_to_upload = self._filter_available_datasets(
            collection, overwrite
        )

        rows = []
        for index in indices_to_upload:
            dataset = collection.datasets[index]
            # serialize dicts to json strings - arize can't handle raw dict objects
            output = dataset.output
            output["goal_details"] = [
                goal.model_dump() for goal in output["goal_details"]
            ]

            row = {
                "input": json.dumps(dataset.input),
                "expected_output": json.dumps(output),
            }
            rows.append(row)

        if rows:
            df = pd.DataFrame(rows)
            dataset_id = client.create_dataset(
                space_id=self.space_id,
                dataset_name=collection.collection_name,
                dataset_type=GENERATIVE,
                data=df,
            )
            logger.info(f"Created dataset: {dataset_id}")
            self.dataset_id = dataset_id

    def get_dataset(self):
        client = self.init_client()
        return client.get_dataset(
            space_id=self.space_id,
            dataset_name=self.name,
        )

    def get_data_items(self) -> pd.DataFrame:
        # TODO - what happens if the data exists
        # TODO - figure out what columns are returned
        try:
            df = self.get_dataset()
            return df.itertuples()
        except Exception as e:
            logger.error(f"Error getting data items: {e}")
            return []

    def delete_item(self, item_id: Union[str, List[str]]):
        if self.dataset_id is None:
            logger.error(
                f"Please upload the dataset first using the `upload` method"
            )
            raise ValueError("`dataset_id` is None")

        client = self.init_client()

        df = self.get_data_items()

        row_ids_to_delete = [item_id] if isinstance(item_id, str) else item_id
        rows_before = len(df)
        rows_to_delete = df["id"].isin(row_ids_to_delete)

        if not rows_to_delete.any():
            logger.warning(
                f"Row ID(s) {row_ids_to_delete} not found in dataset"
            )
            return False

        # Filter out the rows to delete
        df_filtered = df[~rows_to_delete].copy()
        rows_after = len(df_filtered)
        rows_deleted = rows_before - rows_after

        if rows_deleted == 0:
            logger.warning("No rows were deleted")
            return False

        # Update the dataset with the filtered data
        # Note: update_dataset creates a new version
        updated_dataset_id = client.update_dataset(
            space_id=self.space_id,
            data=df_filtered,
            dataset_id=self.dataset_id,
            dataset_name=self.name,
        )
        logger.info(f"Updated dataset: {updated_dataset_id}")
        self.dataset_id = updated_dataset_id

        return True

    def delete_all_items(self):
        if self.dataset_id is None:
            logger.error(f"Dataset ID is None. No delete operation performed.")
            return False

        client = self.init_client()
        client.delete_dataset(
            space_id=self.space_id,
            dataset_id=self.dataset_id,
            dataset_name=self.name,
        )
        logger.info(f"Deleted dataset: {self.dataset_id}")
        self.dataset_id = None

        return True
