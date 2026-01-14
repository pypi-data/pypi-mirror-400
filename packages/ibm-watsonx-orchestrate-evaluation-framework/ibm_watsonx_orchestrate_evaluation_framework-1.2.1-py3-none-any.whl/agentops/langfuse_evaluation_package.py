from collections import defaultdict, deque
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional, Type, Union

from langfuse.experiment import ExperimentResult

import agentops.metrics as metric_pkg
from agentops.arg_configs import TestConfig
from agentops.collection.collection_base import CollectionBase
from agentops.extractors import Extractor
from agentops.metrics.evaluations import Evaluation
from agentops.metrics.metrics import EvaluatorData
from agentops.metrics.tool_calling import ToolCalling
from agentops.otel_parser import parser as otel_parser
from agentops.persistance.persistance_base import PersistanceBase
from agentops.service_provider import get_provider
from agentops.type import DatasetModel, ExperimentResult
from agentops.utils.arize_utils import build_arize_experiment_id
from agentops.utils.rich_utils import RichLogger
from agentops.utils.telemetry_platform import TelemetryPlatform

CLIENT = None

logger = RichLogger(__name__)


def default_aggregator(session_results: List[List[Evaluation]]):
    metric_names = [
        "journey_success",
        "total_tool_calls",
        "correct_tool_calls",
        "expected_tool_calls",
        "tool_calls_with_incorrect_parameter",
        "tool_call_recall",
        "tool_call_precision",
        "orchestrate_agent_routing_accuracy",
    ]
    group_metrics = defaultdict(list)

    for result in session_results:
        for metric in result:
            if metric["eval_name"] in metric_names:
                group_metrics[metric["eval_name"]].append(
                    {"value": metric["value"], "metadata": metric["metadata"]}
                )

    average_metric = []
    for metric_name, values in group_metrics.items():
        aggr = []
        for value in values:
            aggr.append(value.get("value"))

        metric_value = EvaluatorData(
            eval_name=f"Average_{metric_name}",
            value=round(sum(aggr) / len(aggr), 2),
            metadata=values[0]["metadata"],
        )
        average_metric.append(metric_value)

    return average_metric


def load_metrics(config: TestConfig, metrics: list[str]) -> list[Evaluation]:
    """
    Load metric evaluator instances using their name. If the name can not be resolved from the metrics package, it will be skipped.

    Args:
        config: Test configuration for set up.
        metrics: List of metric names to load

    Returns:
        A list of initialized evaluator instances.
    """
    evaluators = []
    llm_client = get_provider(config.provider_config)
    logger.info(f"Loading following metrics {metrics}")
    for metric in metrics:
        try:
            metric_cls = getattr(metric_pkg, metric)
        except AttributeError:
            logger.error(
                f"Unknown metric: {metric}. Please validate metrics name."
            )
            continue
        evaluators.append(
            metric_cls(llm_client=llm_client, config=asdict(config))
        )
    return evaluators


class EvaluationRunner:
    def __init__(
        self,
        evaluation_name: str,
        run_name: str,
        metrics: List[Evaluation],
        aggregator: Callable,
        experiment_results: Any,
        exporters: List[PersistanceBase],
        collection: Optional[CollectionBase] = None,
        operator_configs: Dict[str, dict] = None,
        resource_map: Optional[Any] = None,
        messages=None,
    ):
        self.evaluation_name = evaluation_name
        self.run_name = run_name

        self.collection = collection
        self.test_cases: List[DatasetModel] = []
        self.experiment_results = experiment_results

        if self.collection:
            for item in self.collection.get_data_items():
                data_model = self.collection._process_item(item)
                self.test_cases.append(data_model)

        self.telemetry_platform = TelemetryPlatform()

        # initialize telemetry platform specific variables
        if self.telemetry_platform.is_langfuse:
            self.session_ids = [
                entry.output for entry in experiment_results.item_results
            ]
            self.experiment_id = f"{self.evaluation_name}.{self.run_name}"
            # TODO: REFACTOR FOR LANGFUSE TO USE IN MEMORY EXPORTER
            self.messages = [
                otel_parser.poll_messages(id) for id in self.session_ids
            ]
        elif self.telemetry_platform.is_arize:
            self.session_ids = experiment_results["result"].tolist()
            self.experiment_id = build_arize_experiment_id(
                self.collection.dataset_id
            )

        if messages:
            self.messages = messages

        # Arize/Langfuse, Disk, in the future we can have S3, etc.
        self.exporters = exporters

        if self.is_referenceless:
            assert len(self.session_ids) == len(self.messages)
        else:
            assert (
                len(self.session_ids)
                == len(self.messages)
                == len(self.test_cases)
            )

        self.metrics = metrics
        self.aggregator = aggregator
        self.operator_configs = operator_configs
        self.resource_map = resource_map

    @property
    def is_referenceless(self):
        return self.collection is None

    @classmethod
    def _gather(cls, nodes):
        """Extract all the `operators` for the provided metrics.

        Here `operators` means either an evaluator or extractor.
        A `metric` may depend on another `extractor` or `evaluator`.
        We first gather all the dependencies that each metric and it's dependencies rely on.

        Return:
        - We return a mapping between the operator and the object.
        For example:
        {
            "Journey Success": journey_success,
            "Expected Tool Extractor": expected_tool_call_extractor
        }
        """

        op_mapping = {}

        while nodes:
            curr_node = nodes.pop()
            if curr_node.__class__.__name__ not in op_mapping:
                op_mapping[curr_node.__class__.__name__] = curr_node

            for deps in curr_node.dependencies:
                if deps.__class__.__name__ not in op_mapping:
                    nodes.append(deps)

        return op_mapping

    @classmethod
    def _scheduler(cls, metrics):
        op_mapping = cls._gather(nodes=metrics)

        eval_dag = defaultdict(list)
        in_degree = defaultdict(int)
        for op in op_mapping.values():
            for dependency in op.dependencies:
                eval_dag[dependency.__class__.__name__].append(
                    op.__class__.__name__
                )
                in_degree[op.__class__.__name__] += 1

            if op.__class__.__name__ not in in_degree:
                in_degree[op.__class__.__name__] = 0

        ordering = []
        queue = deque(
            [op for op, num_deps in in_degree.items() if num_deps == 0]
        )

        while queue:
            op = queue.popleft()
            ordering.append(op)

            for operator in eval_dag[op]:
                in_degree[operator] -= 1
                if in_degree[operator] == 0:
                    queue.append(operator)

        ordering = {op: op_mapping.get(op) for op in ordering}
        logger.info(
            f"Executing the following operations: {list(ordering.keys())}"
        )
        return ordering

    def evaluate(self):
        schedule = self._scheduler(metrics=self.metrics)
        metadata = {"experiment_id": self.experiment_id}
        total_metrics = []

        if self.is_referenceless:
            evaluation_items = self.messages
        else:
            evaluation_items = self.test_cases

        for idx, item in enumerate(evaluation_items):
            messages = self.messages[idx]
            context = {"extractor": {}, "metric": {}}

            ground_truth = None if self.is_referenceless else item
            try:
                for operator in schedule.values():
                    if self.operator_configs is not None:
                        operator.config = self.operator_configs.get(
                            operator.__class__.__name__
                        )
                    else:
                        operator.config = None
                    if isinstance(operator, Evaluation):
                        context = operator.evaluate(
                            messages=messages,
                            ground_truth=ground_truth,
                            extracted_context=context,
                            metadata=metadata,
                        )
                    if isinstance(operator, Extractor):
                        context = operator.extract(
                            messages=messages,
                            ground_truth=ground_truth,
                            extracted_context=context,
                            metadata=metadata,
                            resource_map=self.resource_map,
                        )

                metrics = context.get("metric")
                metric_results = []

                for outputs in metrics.values():
                    for output in outputs:
                        metric_results.append(output.model_dump())

                total_metrics.append(metric_results)
            except Exception as e:
                logger.error(
                    f'Error calculating metrics for test case session "{self.session_ids[idx]}"',
                    e,
                )

        aggregate_metrics = self.aggregator(total_metrics)

        for exporter in self.exporters:
            exporter.persist(
                evaluation_results=total_metrics,
                experiment_results=self.experiment_results,
                collection=self.collection,
                experiment_id=self.experiment_id,
                metadata=metadata,
            )
            exporter.persist_aggregated_metrics(
                aggregated_metrics=aggregate_metrics
            )

        return ExperimentResult(
            experiment_name=self.evaluation_name,
            run_id=self.run_name,
            experiment_id=self.experiment_id,
            metrics=total_metrics,
            session_ids=self.session_ids,
            aggregate_metrics=aggregate_metrics,
        )


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--collection_name", "-c", required=False, type=str)
    parser.add_argument("--session_ids", "-s", nargs="+", required=True)

    args = parser.parse_args()

    collection_name = args.collection_name
    langfuse_collection = LangfuseCollection(name=collection_name)
    journey_sucess_metric = JourneySuccessMetric()
    tool_calling = ToolCalling()

    operator_configs = {
        "ExpectedToolExtractor": {"parameter": 10},
        "ExtractLabeledMessages": {"parameter": "default"},
        "JourneySuccessMetric": {"is_strict": False},
    }

    run = EvaluationRunner(
        evaluation_name="sample_evaluation",
        run_name="1",
        session_ids=args.session_ids,
        collection=langfuse_collection,
        metrics=[tool_calling, journey_sucess_metric],
        aggregator=default_aggregator,
        operator_configs=operator_configs,
    )

    experiment_results = run.evaluate()

    logger.info("----- Experiment Results ---- ")
    logger.info(str(experiment_results))
    logger.info("----------------------------- ")
