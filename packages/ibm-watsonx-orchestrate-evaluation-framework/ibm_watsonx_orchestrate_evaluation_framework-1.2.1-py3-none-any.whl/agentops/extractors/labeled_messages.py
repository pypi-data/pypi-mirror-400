import json
from typing import Any, List, Mapping

from agentops.extractors.extractor_base import Extractor
from agentops.metrics.metrics import ExtractorData
from agentops.type import ContentType, GoalDetail, Message


class ExtractLabeledMessages(Extractor):
    def __init__(self, config=None):
        super().__init__(config)

    def do_extract(
        self,
        messages: List[Message],
        ground_truth,
        extracted_context={},
        **kwargs,
    ) -> Any:
        tool_dictionary = (
            {
                goal_detail.name: goal_detail
                for goal_detail in ground_truth.goal_details
                if goal_detail.type == ContentType.tool_call
            }
            if ground_truth.goal_details
            else {}
        )
        labeled_messages = {}
        for idx, message in enumerate(messages):
            if message.type != ContentType.tool_call:
                continue
            try:
                msg_tool_call = message.tool_calls[0].function
            except Exception:
                # ignore malformed tool_call content
                continue

            matching_goal_details = [
                gd
                for gd in tool_dictionary.values()
                if gd.tool_name == msg_tool_call.name
            ]

            if matching_goal_details:
                labeled_messages[idx] = matching_goal_details

        return ExtractorData(
            field_name="labeled_messages",
            value=labeled_messages,
        )
