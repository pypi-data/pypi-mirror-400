import json

from agentops.type import ContentType, Function, Message, ToolCall


def parse_observations(observation_tree, dfs_observations):
    messages = []
    for obs in dfs_observations:
        if obs.obs.type == "GENERATION":
            messages.extend(_get_messages(obs.obs.input))
            messages.extend(_get_messages(obs.obs.output))
    return messages


def _get_messages(data):
    messages = []
    if "message" in data:
        data = [data["message"]]

    for msg in data:
        if msg["role"] == "user":
            messages.append(
                Message(
                    role="user", content=msg["content"], type=ContentType.text
                )
            )
        elif msg["role"] == "assistant" or msg["role"] == "tool":
            content_type = "text" if not msg.get("tool_calls") else "tool_call"
            if content_type == "text":
                content = msg["content"]
                messages.append(
                    Message(
                        role="assistant", content=content, type=ContentType.text
                    )
                )
            elif content_type == "tool_call":
                tool_calls = []
                for tool_call in msg["tool_calls"]:
                    tool_call = ToolCall(
                        id=tool_call["id"],
                        function=Function(
                            name=tool_call["function"]["name"],
                            arguments=tool_call["function"]["arguments"],
                        ),
                    )
                    tool_calls.append(tool_call)
                messages.append(
                    Message(
                        role="assistant",
                        content="",
                        tool_calls=tool_calls,
                        type=ContentType.tool_call,
                    )
                )
    return messages
