import json

from agentops.otel_parser.common import dfs_
from agentops.type import ContentType, Function, Message, ToolCall


def parse_observations(observation_tree, dfs_observations=None):
    """
    Parse observations from an observation tree.

    When there are multiple root nodes (e.g., multiple LangGraph conversation turns
    within a single Arize experiment trace), we process each root separately to
    capture input messages from each turn.
    """
    messages = []

    # Process each root (conversation turn) separately
    for root in observation_tree:
        root_messages = _parse_single_tree(root)
        messages.extend(root_messages)

    return messages


def _parse_single_tree(root_node):
    """Parse a single tree rooted at root_node."""

    messages = []
    is_first_generation = True

    # DFS traversal of just this root's subtree
    dfs_observations = dfs_([root_node])

    for obs in dfs_observations:
        if obs.obs.type == "GENERATION":
            if is_first_generation:
                messages.extend(_get_input_message(obs))
                is_first_generation = False
            parent = obs.parent
            if parent and parent.obs.type == "CHAIN":
                # TODO: messages is a list. confirm, we will only see one message in the list.
                msg = parent.obs.output["messages"][0]
                content = msg["content"] or ""
                msg_type = ContentType.text
                tool_calls = msg["tool_calls"] or None
                if tool_calls is not None:
                    msg_type = ContentType.tool_call
                    tool_calls = [_to_tool_call(tc) for tc in tool_calls]
                messages.append(
                    Message(
                        role="assistant",
                        content=content,
                        tool_calls=tool_calls,
                        type=msg_type,
                    )
                )
        elif obs.obs.type == "TOOL":
            parent_node = obs.parent
            if parent_node and parent_node.obs.type == "CHAIN":
                for tool_response in parent_node.obs.output["messages"]:
                    messages.append(
                        Message(
                            role="tool",
                            content=tool_response["content"],
                            tool_call_id=tool_response["tool_call_id"],
                            type=ContentType.tool_response,
                        )
                    )
    return messages


def _get_input_message(obs_node):
    ret = []
    parent = obs_node.parent
    if parent and parent.obs.type == "CHAIN":
        for msg in parent.obs.input["messages"]:
            if msg["type"] == "system":
                ret.append(
                    Message(
                        role="system",
                        content=msg["content"],
                        type=ContentType.text,
                    )
                )
            elif msg["type"] == "human":
                ret.append(
                    Message(
                        role="user",
                        content=msg["content"],
                        type=ContentType.text,
                    )
                )
            elif msg["type"] == "tool":
                ret.append(
                    Message(
                        role="tool",
                        content=msg["content"],
                        tool_call_id=msg["tool_call_id"],
                        type=ContentType.tool_response,
                    )
                )
            elif msg["type"] == "ai":
                content = msg["content"] or ""
                tool_calls = msg["tool_calls"] or None
                msg_type = ContentType.text
                if tool_calls is not None:
                    msg_type = ContentType.tool_call
                    tool_calls = [_to_tool_call(tc) for tc in tool_calls]
                ret.append(
                    Message(
                        role="assistant",
                        content=content,
                        tool_calls=tool_calls,
                        type=msg_type,
                    )
                )
    return ret


def _to_tool_call(tool_call):
    return ToolCall(
        id=tool_call["id"],
        type="function",  # ToolCall expects literal 'function'
        function=_to_function(tool_call),
    )


def _to_function(func):
    return Function(name=func["name"], arguments=json.dumps(func["args"]))
