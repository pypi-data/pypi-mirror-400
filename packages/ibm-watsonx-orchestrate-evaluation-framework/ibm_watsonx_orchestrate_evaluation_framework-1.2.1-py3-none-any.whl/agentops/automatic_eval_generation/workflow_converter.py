import json
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional


class WorkflowConverter:
    """
    Converts tool call sequences into goal-based workflow format.

    This class provides methods to deterministically analyze tool call sequences
    and create a DAG (Directed Acyclic Graph) that properly handles both
    sequential and parallel tool call dependencies.
    """

    @staticmethod
    def _generate_deterministic_tool_call_name(
        tool_name: str, occurrence_counts: Dict[str, int]
    ) -> str:
        """
        Generate a deterministic name for a tool call using underscores.

        Args:
            tool_name: The base tool name
            occurrence_counts: Dictionary tracking how many times each tool has been called

        Returns:
            Formatted name like "tool_name_1", "tool_name_2", etc.
        """
        occurrence_counts[tool_name] = occurrence_counts.get(tool_name, 0) + 1
        return f"{tool_name}_{occurrence_counts[tool_name]}"

    @staticmethod
    def _value_in_response(arguments: Dict[str, Any], response: Any) -> bool:
        """
        Check if any argument value appears in the response.

        This is a heuristic to detect if a tool call depends on a previous call's output.

        Args:
            arguments: Dictionary of argument name -> value
            response: Response content (can be dict, list, string, etc.)

        Returns:
            True if any argument value is found in the response
        """
        # Convert response to string for searching
        if isinstance(response, (dict, list)):
            response_str = json.dumps(response)
        else:
            response_str = str(response)

        # Check if any argument value appears in the response
        for arg_value in arguments.values():
            if arg_value and str(arg_value) in response_str:
                return True

        return False

    @staticmethod
    def _build_dependency_graph(
        tool_calls_with_responses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build a dependency graph from sequential tool calls.

        Analyzes the tool call sequence to identify which calls depend on previous calls
        by matching argument values to previous response values.

        Args:
            tool_calls_with_responses: List of dicts with tool_name, arguments, response, call_id

        Returns:
            Dictionary with:
            - nodes: List of {id, tool_name, arguments, response}
            - edges: List of {from, to} representing dependencies
            - named_calls: Dict mapping call_id to generated name
        """
        nodes = []
        edges = []
        occurrence_counts = {}
        named_calls = {}  # Map original call_id -> generated name
        call_outputs = {}  # Map generated name -> response data

        for i, call in enumerate(tool_calls_with_responses):
            # Generate deterministic name
            call_name = (
                WorkflowConverter._generate_deterministic_tool_call_name(
                    call["tool_name"], occurrence_counts
                )
            )
            named_calls[call.get("call_id", i)] = call_name

            # Store the node
            nodes.append(
                {
                    "id": call_name,
                    "tool_name": call["tool_name"],
                    "arguments": call["arguments"],
                    "response": call.get("response"),
                }
            )

            # Find dependencies by checking if any argument value appears in previous responses
            for prev_name, prev_response in call_outputs.items():
                if prev_response and WorkflowConverter._value_in_response(
                    call["arguments"], prev_response
                ):
                    edges.append({"from": prev_name, "to": call_name})

            # Store this call's output for future dependency checks
            if call.get("response"):
                call_outputs[call_name] = call.get("response")

        return {
            "nodes": nodes,
            "edges": edges,
            "named_calls": named_calls,
        }

    @staticmethod
    def _build_goals_dict(graph: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Build the goals dictionary from the dependency graph.

        Args:
            graph: Dependency graph with nodes and edges

        Returns:
            Dictionary mapping each goal to list of dependent goals
        """
        goals = defaultdict(list)

        # Build adjacency list from edges
        for edge in graph["edges"]:
            goals[edge["from"]].append(edge["to"])

        # Ensure all nodes are in the goals dict (even if they have no dependencies)
        for node in graph["nodes"]:
            if node["id"] not in goals:
                goals[node["id"]] = []

        return dict(goals)

    @staticmethod
    def _build_goal_details(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build the goal_details list from the dependency graph.

        Args:
            graph: Dependency graph with nodes

        Returns:
            List of goal detail objects
        """
        goal_details = []

        for node in graph["nodes"]:
            goal_details.append(
                {
                    "type": "tool_call",
                    "name": node["id"],
                    "tool_name": node["tool_name"],
                    "args": node["arguments"],
                }
            )

        return goal_details

    @staticmethod
    def convert_tool_calls_to_workflow(
        tool_calls: List[Dict[str, Any]],
        agent: str = None,
        story: Optional[str] = None,
        starting_sentence: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convert tool call data format into goal-based workflow format using syntactic approach.

        This function deterministically analyzes tool call sequences and creates
        a DAG (Directed Acyclic Graph) that properly handles both sequential and parallel
        tool call dependencies.

        Args:
            tool_calls: List of tool calls with tool_name, arguments, response, and call_id
            agent: Agent name (default: None)
            story: User story describing the workflow
            starting_sentence: Starting sentence for the workflow
            session_id: Optional session ID to extract final summary from trace

        Returns:
            Dict containing the converted workflow format with keys:
            - agent: Agent name
            - story: User story (if provided)
            - starting_sentence: Starting sentence (if provided)
            - goals: Dict mapping goal names to list of dependent goals
            - goal_details: List of goal detail objects

        Note:
            This is a syntactic/deterministic implementation that builds the dependency
            graph by analyzing argument values and matching them to previous tool call responses.
        """
        # Build dependency graph
        graph = WorkflowConverter._build_dependency_graph(tool_calls)

        # Build goals dictionary
        goals = WorkflowConverter._build_goals_dict(graph)

        # Build goal_details list
        goal_details = WorkflowConverter._build_goal_details(graph)

        # Build the result structure
        result = {
            "agent": agent,
            "goals": goals,
            "goal_details": goal_details,
        }

        # Add optional fields if provided
        if story:
            result["story"] = story
        if starting_sentence:
            result["starting_sentence"] = starting_sentence

        return result
