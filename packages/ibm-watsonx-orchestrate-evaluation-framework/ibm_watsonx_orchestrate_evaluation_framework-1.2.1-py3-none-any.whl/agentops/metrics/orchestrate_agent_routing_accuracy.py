from collections import defaultdict

from agentops.extractors.orchestrate_routing_tool_call_extractor import (
    OrchestrateRoutingToolCallExtractor,
)
from agentops.metrics.evaluations import Evaluation
from agentops.metrics.metrics import EvaluatorData


class OrchestrateAgentRoutingAccuracy(Evaluation):
    def __init__(self, llm_client=None, config=None):
        super().__init__(llm_client, config)
        self.dependencies = [OrchestrateRoutingToolCallExtractor()]

    def calculate_agent_routing_accuracy(
        self, total_routing_calls: int, relevant_routing_calls: int
    ) -> float:
        """Calculate agent routing accuracy as a ratio.

        Args:
            total_routing_calls: Total number of routing calls made
            relevant_routing_calls: Number of relevant routing calls

        Returns:
            Routing accuracy as a float between 0.0 and 1.0, rounded to 2 decimal places
        """
        if total_routing_calls == 0:
            return -1

        return round(relevant_routing_calls / total_routing_calls, 2)

    def do_evaluate(
        self,
        messages,
        extracted_context,
        ground_truth=None,
        metadata=None,
        **kwargs,
    ):
        ## TODO arjun-gupta1 12/02/2025: turn the whole routine below into a function, otherwise a lot of copy paste in a lot of places
        # Extract routing call data from RoutingToolCallExtractor
        routing_data = extracted_context.get("extractor").get(
            OrchestrateRoutingToolCallExtractor.__name__
        )

        total_routing_calls = [
            item
            for item in routing_data
            if item.field_name == "total_routing_calls"
        ][0].value

        relevant_routing_calls = [
            item
            for item in routing_data
            if item.field_name == "relevant_routing_calls"
        ][0].value

        # Calculate agent routing accuracy
        agent_routing_accuracy = self.calculate_agent_routing_accuracy(
            total_routing_calls, relevant_routing_calls
        )
        # Update extracted context with the metric

        return EvaluatorData(
            eval_name="orchestrate_agent_routing_accuracy",
            comment="",
            value=agent_routing_accuracy,
            data_type="NUMERIC",
            metadata=metadata,
        )
