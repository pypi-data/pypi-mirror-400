import json
from typing import List, Union

from agentops.extractors import ExpectedToolExtractor, ExtractLabeledMessages
from agentops.metrics.evaluations import Evaluation
from agentops.metrics.metrics import EvaluatorData, ToolCallAndRoutingMetrics
from agentops.type import ContentType
from agentops.utils.gold_label import get_gold_tool_calls


class ToolCalling(Evaluation):
    def __init__(self, llm_client=None, config=None):
        super().__init__(llm_client, config)
        self.dependencies = [ExtractLabeledMessages(), ExpectedToolExtractor()]

    def do_evaluate(
        self,
        messages,
        extracted_context,
        ground_truth=None,
        metadata=None,
        **kwargs,
    ) -> Union[EvaluatorData, List[EvaluatorData]]:

        labeled_msg_extractor = extracted_context.get("extractor").get(
            self.dependencies[0].__class__.__name__
        )
        labeled_messages = [
            item
            for item in labeled_msg_extractor
            if item.field_name == "labeled_messages"
        ]
        labeled_messages = labeled_messages[0].value

        expected_tool_extractor = extracted_context.get("extractor").get(
            self.dependencies[1].__class__.__name__
        )
        expected_tools = [
            item
            for item in expected_tool_extractor
            if item.field_name == "correct_tool_calls"
        ]
        expected_tools = expected_tools[0].value

        incorrect_param_tool_idx = [
            item
            for item in expected_tool_extractor
            if item.field_name == "incorrect_param_tool_idx"
        ]
        incorrect_param_tool_idx = incorrect_param_tool_idx[0].value

        dataset_name = kwargs.get("dataset", "")

        tool_dictionary = get_gold_tool_calls(ground_truth=ground_truth)
        total_tool_calls = len(
            [
                message
                for message in messages
                if message.type == ContentType.tool_call
            ]
        )
        relevant_tool_calls = len(labeled_messages)
        tool_calls_with_incorrect_parameter = len(incorrect_param_tool_idx)
        correct_tool_calls = len(expected_tools)

        # TODO: think about the dataset name
        # TODO: total_steps
        tool_call_metrics = ToolCallAndRoutingMetrics(
            dataset_name=dataset_name,
            total_tool_calls=total_tool_calls,
            expected_tool_calls=len(tool_dictionary),
            correct_tool_calls=correct_tool_calls,
            relevant_tool_calls=relevant_tool_calls,
            tool_calls_with_incorrect_parameter=tool_calls_with_incorrect_parameter,
        )

        tool_call_metrics = tool_call_metrics.model_dump()

        metrics = []
        tools = [
            "total_tool_calls",
            "correct_tool_calls",
            "expected_tool_calls",
            "tool_calls_with_incorrect_parameter",
            "tool_call_recall",
            "tool_call_precision",
        ]
        for tool in tools:
            metric = EvaluatorData(
                eval_name=tool,
                value=tool_call_metrics.get(tool),
                metadata=metadata,
                data_type="NUMERIC",
            )
            metrics.append(metric)

        return metrics
