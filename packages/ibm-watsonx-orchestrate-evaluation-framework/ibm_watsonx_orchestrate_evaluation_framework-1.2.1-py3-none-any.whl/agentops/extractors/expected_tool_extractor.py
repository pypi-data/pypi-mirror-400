import json

import rich

from agentops.extractors.extractor_base import Extractor
from agentops.extractors.labeled_messages import ExtractLabeledMessages
from agentops.extractors.utils import (
    check_labeled_messages_empty,
    simplified_argument_matching,
)
from agentops.metrics.metrics import ExtractorData


class ExpectedToolExtractor(Extractor):
    def __init__(self, config=None):
        super().__init__(config)
        self.dependencies = [ExtractLabeledMessages()]

    def do_extract(
        self, messages, ground_truth, extracted_context={}, **kwargs
    ):
        labeled_msg_extractor = extracted_context.get("extractor").get(
            self.dependencies[0].__class__.__name__
        )
        labeled_messages = [
            item
            for item in labeled_msg_extractor
            if item.field_name == "labeled_messages"
        ]
        labeled_messages = labeled_messages[0].value
        correct_tool_calls = {}
        incorrect_param_tool_idx = []

        check_labeled_messages_empty(labeled_messages)

        for message_idx, matching_goal_details in labeled_messages.items():
            msg_tool_call = messages[message_idx]
            msg_tool_call = msg_tool_call.tool_calls[0].function

            found = False
            for goal_detail in matching_goal_details:
                # TODO flesh out to match ADK EVAL
                args_match = simplified_argument_matching(
                    expected=goal_detail.args,
                    actual=(
                        None
                        if len(msg_tool_call.arguments) == 0
                        else json.loads(msg_tool_call.arguments)
                    ),
                )

                if args_match:
                    found = True
                    correct_tool_calls[goal_detail.name] = None
                    break

            if not found:
                incorrect_param_tool_idx.append(message_idx)

        correct_tool_calls = ExtractorData(
            field_name="correct_tool_calls",
            value=list(correct_tool_calls.keys()),
        )
        incorrect_param_tool_idx = ExtractorData(
            field_name="incorrect_param_tool_idx",
            value=incorrect_param_tool_idx,
        )

        extractor_data = [correct_tool_calls, incorrect_param_tool_idx]

        return extractor_data
