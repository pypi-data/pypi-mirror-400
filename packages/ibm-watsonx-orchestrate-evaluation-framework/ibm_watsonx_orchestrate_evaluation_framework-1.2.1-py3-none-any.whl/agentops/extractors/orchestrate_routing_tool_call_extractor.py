import json
from typing import Any, Dict, List, Optional

from agentops.extractors import labeled_messages
from agentops.extractors.extractor_base import Extractor
from agentops.extractors.labeled_messages import ExtractLabeledMessages
from agentops.metrics.metrics import ExtractorData
from agentops.type import ContentType, Message


class OrchestrateRoutingToolCallExtractor(Extractor):
    """Extracts routing tool call metrics from messages."""

    def __init__(self, config=None):
        super().__init__(config)

    def do_extract(
        self,
        messages: List[Message],
        ground_truth,
        extracted_context: Dict[str, Any] = {},
        **kwargs,
    ) -> list[ExtractorData]:
        """Extract routing call metrics.

        Args:
            messages: List of conversation messages
            ground_truth: Ground truth data with goal_details
            extracted_context: Context from previous extractors
            **kwargs: Additional arguments (resource_map containing agent2tools mapping)
        """
        # Get agent2tools mapping from kwargs
        resource_map = kwargs.get("resource_map")
        # Access agent2tools from resource_map
        agent2tools = resource_map.agent2tools if resource_map else None

        ## TODO arjun-gupta1 11/21/2025 -- make this into a utility this gets re-used elsewhere
        # Build tool dictionary from ground truth
        tool_dictionary = (
            {
                goal_detail.name: goal_detail
                for goal_detail in ground_truth.goal_details
                if goal_detail.type == ContentType.tool_call
            }
            if ground_truth.goal_details
            else {}
        )

        # Initialize counters
        total_routing_calls = 0
        relevant_routing_calls = 0

        # Process messages
        for message in messages:
            if message.type == ContentType.tool_call:
                # Extract tool call from message
                try:
                    msg_tool_call = message.tool_calls[0].function
                    tool_name = msg_tool_call.name
                except (AttributeError, IndexError):
                    # Skip malformed tool calls
                    continue

                # Check if this is a routing call
                if agent2tools and tool_name in agent2tools:
                    total_routing_calls += 1

                    # Check if routing call is relevant
                    relevant = False
                    for tool in agent2tools[tool_name]:
                        for goal_detail in tool_dictionary.values():
                            if goal_detail.tool_name == tool:
                                relevant = True
                                break
                        if relevant:
                            break

                    if relevant:
                        relevant_routing_calls += 1

        # Create ExtractorData objects for each metric
        total_routing_calls_data = ExtractorData(
            field_name="total_routing_calls",
            value=total_routing_calls,
        )

        relevant_routing_calls_data = ExtractorData(
            field_name="relevant_routing_calls",
            value=relevant_routing_calls,
        )

        return [total_routing_calls_data, relevant_routing_calls_data]
