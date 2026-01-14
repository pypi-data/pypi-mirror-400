import json

from agentops.type import ContentType, Function, Message, ToolCall


def parse_observations(observation_tree, dfs_observations):
    messages = []
    for node in dfs_observations:
        if node.obs.type == "GENERATION":
            if node.parent.obs.name == "invoke_agent":
                messages.extend(_get_input_messages(node.parent.obs.input))
                messages.extend(_get_output_message(node.parent.obs.output))
    return messages


def _get_input_messages(data):
    messages = []
    for msg in data["messages"]:
        if msg["type"] == "system":
            messages.append(
                Message(
                    role="system", content=msg["content"], type=ContentType.text
                )
            )
        elif msg["type"] == "human":
            messages.append(
                Message(
                    role="user", content=msg["content"], type=ContentType.text
                )
            )
        elif msg["type"] == "tool":
            messages.append(
                Message(
                    role="tool",
                    content=msg["content"],
                    tool_call_id=msg["tool_call_id"],
                    type=ContentType.tool_response,
                )
            )
        elif msg["type"] == "ai":
            if (
                msg.get("additional_kwargs", {}).get("tool_calls", None)
                is not None
            ):
                msg_tool_calls = msg["additional_kwargs"]["tool_calls"]
                tool_calls = []
                for tc in msg_tool_calls:
                    tool_calls.append(
                        ToolCall(
                            id=tc["id"],
                            function=Function(
                                name=tc["function"]["name"],
                                arguments=tc["function"]["arguments"],
                            ),
                        )
                    )
            else:
                tool_calls = None
            messages.append(
                Message(
                    role="assistant",
                    content=msg["content"],
                    tool_calls=tool_calls,
                    type=(
                        ContentType.tool_call
                        if tool_calls
                        else ContentType.text
                    ),
                )
            )
    return messages


def _get_output_message(data):
    content = data.get("content", "")
    if data.get("tool_calls", None):
        msg_type = ContentType.tool_call
        tool_calls = []
        for tc in data["tool_calls"]:
            tool_calls.append(
                ToolCall(
                    id=tc["id"],
                    function=Function(
                        name=tc["name"],
                        arguments=json.dumps(tc.get("args", {})),
                    ),
                )
            )
    else:
        msg_type = ContentType.text
        tool_calls = None
    return [
        Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
            type=msg_type,
        )
    ]
