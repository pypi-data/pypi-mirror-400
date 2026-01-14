import hashlib
import json
import re
from typing import List

from agentops.type import ContentType, Function, Message, ToolCall


def parse_crewai_messages(data: List[dict]) -> List[Message]:
    """
    Parse CrewAI messages from trace output.

    Args:
        data: List of message dictionaries with 'role' and 'content' keys

    Returns:
        List of Message objects
    """
    messages = []
    for msg in data:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "system":
            # System messages contain agent instructions and tool definitions
            messages.append(
                Message(role="system", content=content, type=ContentType.text)
            )
        elif role == "user":
            # User messages contain task instructions
            messages.append(
                Message(role="user", content=content, type=ContentType.text)
            )
        elif role == "assistant":
            # Assistant messages may contain tool calls or final answers
            # Check if this is a tool call by looking for Action/Action Input pattern
            tool_call_match = _extract_tool_call(content)

            if tool_call_match:
                # This is a tool call
                tool_name = tool_call_match["action"]
                tool_args = tool_call_match["action_input"]

                # Generate a deterministic ID for the tool call using hashlib
                hash_input = f"{tool_name}:{tool_args}".encode("utf-8")
                tool_call_id = f"call_{hashlib.md5(hash_input).hexdigest()[:8]}"

                tool_call = ToolCall(
                    id=tool_call_id,
                    function=Function(name=tool_name, arguments=tool_args),
                )

                messages.append(
                    Message(
                        role="assistant",
                        content="",
                        tool_calls=[tool_call],
                        type=ContentType.tool_call,
                    )
                )
            else:
                # Regular assistant message (thought or final answer)
                messages.append(
                    Message(
                        role="assistant", content=content, type=ContentType.text
                    )
                )

    return messages


def _extract_tool_call(content: str) -> dict | None:
    """
    Extract tool call information from CrewAI assistant message content.

    CrewAI uses the format:
    Thought: ...
    Action: tool_name
    Action Input: {"key": "value"}
    Observation: ...

    Args:
        content: The assistant message content

    Returns:
        Dictionary with 'action' and 'action_input' keys, or None if no tool call found
    """
    # Look for Action and Action Input patterns
    action_pattern = r"Action:\s*(.+?)(?:\n|$)"
    action_input_pattern = r"Action Input:\s*(\{.+?\})"

    action_match = re.search(action_pattern, content)
    action_input_match = re.search(action_input_pattern, content, re.DOTALL)

    if action_match and action_input_match:
        action = action_match.group(1).strip()
        action_input = action_input_match.group(1).strip()

        # Validate that action_input is valid JSON
        try:
            json.loads(action_input)
            return {"action": action, "action_input": action_input}
        except json.JSONDecodeError:
            return None

    return None


def parse_trace_output(trace) -> List[Message]:
    """
    Parse CrewAI messages directly from trace output.

    CrewAI stores messages in trace.output["tasks_output"][i]["messages"]

    Args:
        trace: The trace object containing output data

    Returns:
        List of Message objects
    """
    messages = []

    # Check if trace has output
    if not hasattr(trace, "output") or not trace.output:
        return messages

    output = trace.output

    # Handle case where output is a list (multiple messages)
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict) and "messages" in item:
                messages.extend(parse_crewai_messages(item["messages"]))

    # Handle case where output is a dict with tasks_output
    elif isinstance(output, dict):
        if "tasks_output" in output:
            tasks_output = output["tasks_output"]
            if isinstance(tasks_output, list):
                for task in tasks_output:
                    if isinstance(task, dict) and "messages" in task:
                        messages.extend(parse_crewai_messages(task["messages"]))
        elif "messages" in output:
            messages.extend(parse_crewai_messages(output["messages"]))

    return messages


def parse_observations(observation_tree, dfs_observations) -> List[Message]:
    """
    Parse observations from CrewAI trace tree.

    This function is compatible with the observation tree structure used
    in the agentops evaluation framework.

    Args:
        observation_tree: The observation tree structure
        dfs_observations: List of observations in depth-first order

    Returns:
        List of Message objects
    """
    messages = []

    for obs in dfs_observations:
        # Check both GENERATION and SPAN types for CrewAI data
        if obs.obs.type in ["GENERATION", "SPAN"]:
            # Extract messages from output
            output = obs.obs.output

            # Check if output contains tasks_output with messages
            if isinstance(output, dict) and "tasks_output" in output:
                tasks_output = output["tasks_output"]

                for task in tasks_output:
                    if isinstance(task, dict) and "messages" in task:
                        task_messages = task["messages"]
                        messages.extend(parse_crewai_messages(task_messages))

            # Also check if output directly contains messages
            elif isinstance(output, dict) and "messages" in output:
                messages.extend(parse_crewai_messages(output["messages"]))

            # Also check input for messages
            input_data = obs.obs.input
            if isinstance(input_data, dict) and "messages" in input_data:
                messages.extend(parse_crewai_messages(input_data["messages"]))

    return messages


def get_system_message(trace) -> Message | None:
    """
    Extract system message from CrewAI trace metadata.

    Args:
        trace: The trace object containing metadata

    Returns:
        Message object with system role, or None if not found
    """
    # Try to get system instructions from trace metadata
    sys_instruction_json = trace.metadata.get("attributes", {}).get(
        "gen_ai.system_instructions"
    )

    if not sys_instruction_json:
        return None

    try:
        instruction_data = json.loads(sys_instruction_json)
        if isinstance(instruction_data, list) and len(instruction_data) > 0:
            instruction = instruction_data[0].get("content", "")
            return Message(
                role="system", content=instruction, type=ContentType.text
            )
    except (json.JSONDecodeError, KeyError, IndexError):
        return None

    return None
