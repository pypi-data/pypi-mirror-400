from collections import defaultdict

import rich

from agentops.extractors import ExpectedToolExtractor
from agentops.metrics.evaluations import Evaluation
from agentops.metrics.metrics import EvaluatorData

"""
    - hyphens are not allowed in python function names, so it is safe to use as a dummy function name
    - purpose behind `DUMMY_GRAPH_NODE_NAME` is to append
    a dummy node to the ground truth and the labelled messages to take into account 
    single, summary step goals.
"""
DUMMY_GRAPH_NODE_NAME = "dummy-goal"


class JourneySuccessMetric(Evaluation):
    def __init__(self, llm_client=None, config=None):
        if config:
            rich.print(
                f"[bold green]INFO:[/bold green] JourneySuccessMetric initialized with config: {config}"
            )
        else:
            rich.print(
                f"[bold green]INFO:[/bold green] JourneySuccessMetric will use strict mode by default"
            )

        super().__init__(llm_client, config)
        self.dependencies = [ExpectedToolExtractor()]

    def find_terminal_nodes(self, graph: dict[str, list[str]]) -> set[str]:
        """Finds terminal nodes (nodes with no outgoing edges).

        Args:
            graph: the input graph

        Returns:
            a set of the terminal nodes
        """

        seen_nodes = set()  # track seen nodes
        non_terminal_nodes = set()  # track nodes with children

        for node in graph:
            seen_nodes.add(node)
            if graph[node]:
                non_terminal_nodes.add(node)
                for n in graph[node]:
                    seen_nodes.add(n)
        return seen_nodes - non_terminal_nodes

    def is_topological_sort(
        self,
        graph: dict[str, list[str]],
        ordering: list[str],
        is_strict: bool = True,
    ) -> bool:
        """Graph traversal to check if every node in `graph` is visited in `ordering` only after all its dependencies are visited.

        Args:
            graph: the graph representing the ground truth, where keys represent nodes and values represent its dependent nodes
            ordering: the nodes visited, in order

        Returns:
            Boolean representing if `ordering` visits all nodes in a valid order based on the dependencies in graph.
        """
        # No keyword match or goal details were achieved
        if not ordering:
            return False

        if is_strict:
            # strict matching: only consider most recent tool call
            position = {node: [i] for i, node in enumerate(ordering)}
        else:
            # lenient matching: consider all tool calls (account for all indexes of the node)
            position = defaultdict(list)
            for i, node in enumerate(ordering):
                position[node].append(i)

        terminal_nodes = self.find_terminal_nodes(graph)
        # adds a dummy node for each terminal node
        next_idx = (
            max(val for values in position.values() for val in values) + 1
        )

        for n in terminal_nodes:
            graph[n] = [DUMMY_GRAPH_NODE_NAME]
            graph[DUMMY_GRAPH_NODE_NAME] = []
            position[DUMMY_GRAPH_NODE_NAME] = [next_idx]
            next_idx += 1

        for node in graph:
            for child_nodes in graph[node]:
                # Current node/children doesn't show up in made calls
                if node not in position or child_nodes not in position:
                    return False
                # Current node doesn't show up before any of its child
                # all index in current nodes are larger than every child nodes' index
                if all(
                    curr >= max(position[child_nodes])
                    for curr in position[node]
                ):
                    return False
        return True

    def do_evaluate(
        self,
        messages,
        extracted_context,
        ground_truth=None,
        metadata=None,
        **kwargs,
    ):

        extractor_context = extracted_context.get("extractor")
        expected_tool_extractor = extractor_context.get(
            self.dependencies[0].__class__.__name__
        )
        correct_tool_calls = [
            item
            for item in expected_tool_extractor
            if item.field_name == "correct_tool_calls"
        ][0].value

        is_topological_sort = self.is_topological_sort(
            graph=ground_truth.goals,
            ordering=correct_tool_calls,
            is_strict=(
                self.config.get("is_strict", True) if self.config else True
            ),
        )

        return EvaluatorData(
            eval_name="journey_success",
            comment="",
            value=is_topological_sort,
            data_type="NUMERIC",
            metadata=metadata,
        )
