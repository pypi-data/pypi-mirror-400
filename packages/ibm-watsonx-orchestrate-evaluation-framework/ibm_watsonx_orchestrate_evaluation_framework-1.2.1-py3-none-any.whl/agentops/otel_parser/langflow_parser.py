import json

from agentops.type import ContentType, Function, Message, ToolCall


def parse_observations(
    observation_tree, dfs_observations, dfs_callable: callable
):
    messages = []
    for node in dfs_observations:
        # assume there will only be one AgentExecutor in the trace!
        if node.obs.name == "AgentExecutor":
            return _parse_agent_executor(
                node.children, dfs_callable(node.children)
            )
    return messages


def _parse_agent_executor(observation_tree, dfs_observations):
    messages = []
    for node in dfs_observations:
        if node.obs.type == "GENERATION":
            print(node.obs.id)
            messages.extend(_get_messages(node.obs.input))
            # get intemediate steps from parent
            messages.extend(_get_intermediate_steps(node.parent))
            messages.extend(_get_messages([node.obs.output]))
    return messages


def _get_messages(data):
    messages = []
    for msg in data:
        if msg["role"] == "system":
            messages.append(
                Message(
                    role="system", content=msg["content"], type=ContentType.text
                )
            )
        elif msg["role"] == "user":
            content = ""
            if isinstance(msg["content"], list):
                content = []
                for item in msg["content"]:
                    if item["type"] == ["text"]:
                        content.append(item["text"])
                content = " ".join(content)
            elif isinstance(msg["content"], str):
                content = msg["content"]

            messages.append(
                Message(role="user", content=content, type=ContentType.text)
            )
        elif msg["role"] == "assistant":
            content = msg["content"] or ""
            additional_kwargs = msg.get("additional_kwargs", {})
            tool_calls = None
            if "tool_calls" in additional_kwargs:
                tool_calls = []
                for tc in additional_kwargs["tool_calls"]:
                    id_ = tc["id"]
                    function = Function(
                        name=tc["function"]["name"],
                        arguments=tc["function"]["arguments"],
                    )
                    tool_calls.append(ToolCall(id=id_, function=function))
            messages.append(
                Message(
                    role="assistant",
                    content=content,
                    tool_calls=tool_calls,
                    type=(
                        ContentType.tool_call
                        if tool_calls
                        else ContentType.text
                    ),
                )
            )
    return messages


def _get_intermediate_steps(node):
    messages = []
    if "intermediate_steps" not in node.obs.input:
        return messages
    tool_calls_n_responses = node.obs.input["intermediate_steps"]
    for tc, tr in tool_calls_n_responses:
        if "tool" in tc and "tool_input" in tc and "tool_call_id" in tc:
            tool_call_id = tc["tool_call_id"]
            if isinstance(tr, str):
                messages.append(
                    Message(
                        role="tool",
                        content=tr,
                        tool_call_id=tool_call_id,
                        type=ContentType.tool_response,
                    )
                )
                continue
            elif isinstance(tr, dict) and "content" not in tr:
                messages.append(
                    Message(
                        role="tool",
                        content=json.dumps(tr),
                        tool_call_id=tool_call_id,
                        type=ContentType.tool_response,
                    )
                )
                continue
            elif isinstance(tr, dict) and "content" in tr:
                content = tr["content"]
                if isinstance(content, str):
                    messages.append(
                        Message(
                            role="tool",
                            content=content,
                            tool_call_id=tool_call_id,
                            type=ContentType.tool_response,
                        )
                    )
                    continue
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part["type"] == "text":
                            text = part["text"]
                            if isinstance(text, dict):
                                text = json.dumps(text)
                            messages.append(
                                Message(
                                    role="tool",
                                    content=text,
                                    tool_call_id=tool_call_id,
                                    type=ContentType.tool_response,
                                )
                            )
                            continue
                        else:
                            raise ValueError(
                                f"Unexpected part type: {type(part)} or part[type] '{part['type']}' != 'text'"
                            )
                else:
                    raise ValueError(
                        f"Unexpected content type: {type(content)}"
                    )
            elif isinstance(tr, list):
                content = json.dumps(tr)
                messages.append(
                    Message(
                        role="tool",
                        content=content,
                        tool_call_id=tool_call_id,
                        type=ContentType.tool_response,
                    )
                )
                continue
            else:
                raise ValueError(
                    f"Unexpected tool response: Type: {type(tr)}, Value: {tr}"
                )

        else:
            print("Tool Call:", tc)
            print("Tool Response:", tr)
    return messages
