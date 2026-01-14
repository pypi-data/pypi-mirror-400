import json

from agentops.type import ContentType, Function, Message, ToolCall


class TmpMessage(Message):
    """Temporary message with tool metadata for matching tool calls to responses"""

    model_config = {"frozen": False}
    tool_name: str | None = None
    tool_arguments: str | None = None


def parse_observations(observation_tree, dfs_observations):
    """Parse Claude agent observations into messages"""
    messages = []
    seen_spans = set()
    for node in dfs_observations:
        if node.obs.type == "GENERATION":
            parent = node.parent
            if parent and parent.obs.id not in seen_spans:
                seen_spans.add(parent.obs.id)
                messages.extend(_parse_messages_from_span(parent))
    return messages


def _parse_messages_from_span(span_node):
    """Parse all messages from a claude.conversation span"""
    messages = []
    if not span_node:
        return messages

    # System prompt from span input
    if system_prompt := span_node.obs.input.get("system"):
        messages.append(
            Message(role="system", content=system_prompt, type=ContentType.text)
        )

    # User message from span input
    if user_msg := span_node.obs.input.get("prompt"):
        messages.append(
            Message(role="user", content=user_msg, type=ContentType.text)
        )

    # Parse child observations (GENERATION and TOOL)
    tmp_messages = []
    for node in sorted(span_node.children, key=lambda x: x.obs.start_time):
        if node.obs.type == "GENERATION":
            out = node.obs.output
            if out.get("role") != "assistant":
                continue

            content = []
            tool_calls = []
            for x in out.get("content", []):
                if x["type"] == "text":
                    content.append(x["text"])
                elif x["type"] == "tool_use":
                    tool_calls.append(
                        ToolCall(
                            id=x["id"],
                            function=Function(
                                name=x["name"], arguments=json.dumps(x["input"])
                            ),
                        )
                    )

            tmp_messages.append(
                Message(
                    role="assistant",
                    content=" ".join(content) if content else "",
                    tool_calls=tool_calls if tool_calls else None,
                    type=(
                        ContentType.tool_call
                        if tool_calls
                        else ContentType.text
                    ),
                )
            )

        elif node.obs.type == "TOOL":
            content = _extract_tool_content(node.obs.output)
            tmp_messages.append(
                TmpMessage(
                    role="tool",
                    content=content,
                    type=ContentType.tool_response,
                    tool_name=node.obs.name,
                    tool_arguments=json.dumps(node.obs.input.get("input", {})),
                )
            )

    # Merge consecutive assistant messages
    compressed_messages = _merge_assistant_messages(tmp_messages)

    # Match tool responses with their tool calls
    final_messages = _match_tool_responses(compressed_messages)

    messages.extend(final_messages)
    return messages


def _extract_tool_content(output):
    """Extract text content from tool output"""
    if "content" in output:
        texts = []
        for x in output.get("content", []):
            if x.get("type") == "text":
                texts.append(x["text"])
        return " ".join(texts) if texts else ""
    elif "output" in output:
        response = output["output"]
        return response if isinstance(response, str) else json.dumps(response)
    elif isinstance(output, str):
        return output
    elif isinstance(output, dict):
        return json.dumps(output)
    return ""


def _merge_assistant_messages(tmp_messages):
    """Merge consecutive assistant messages"""
    if not tmp_messages:
        return []

    compressed = []
    prev_msg = None

    for msg in tmp_messages:
        if prev_msg and msg.role == prev_msg.role == "assistant":
            # Merge with previous assistant message
            if prev_msg.type == ContentType.tool_call:
                if msg.type == ContentType.tool_call:
                    # Merge tool calls
                    prev_msg = Message(
                        role="assistant",
                        content=prev_msg.content,
                        tool_calls=list(prev_msg.tool_calls)
                        + list(msg.tool_calls),
                        type=ContentType.tool_call,
                    )
                    compressed[-1] = prev_msg
                else:
                    # Add text to existing
                    prev_msg = Message(
                        role="assistant",
                        content=(prev_msg.content + " " + msg.content).strip(),
                        tool_calls=prev_msg.tool_calls,
                        type=ContentType.tool_call,
                    )
                    compressed[-1] = prev_msg
            elif prev_msg.type == ContentType.text:
                if msg.type == ContentType.tool_call:
                    # Upgrade to tool_call
                    new_msg = Message(
                        role="assistant",
                        content=prev_msg.content,
                        tool_calls=msg.tool_calls,
                        type=ContentType.tool_call,
                    )
                    compressed[-1] = new_msg
                    prev_msg = new_msg
                else:
                    # Merge text
                    prev_msg = Message(
                        role="assistant",
                        content=(prev_msg.content + " " + msg.content).strip(),
                        type=ContentType.text,
                    )
                    compressed[-1] = prev_msg
        else:
            prev_msg = msg
            compressed.append(msg)

    return compressed


def _match_tool_responses(compressed_messages):
    """Match tool responses with their corresponding tool calls"""
    if not compressed_messages:
        return []

    final = [compressed_messages[0]]
    prev_assistant = (
        compressed_messages[0]
        if compressed_messages[0].role == "assistant"
        else None
    )

    for msg in compressed_messages[1:]:
        if (
            msg.role == "tool"
            and prev_assistant
            and prev_assistant.type == ContentType.tool_call
        ):
            # Find matching tool call by name and arguments
            matched = False
            for tc in prev_assistant.tool_calls:
                if (
                    hasattr(msg, "tool_name")
                    and tc.function.name == msg.tool_name
                ):
                    if (
                        hasattr(msg, "tool_arguments")
                        and tc.function.arguments == msg.tool_arguments
                    ):
                        final.append(
                            Message(
                                role="tool",
                                content=msg.content,
                                tool_call_id=tc.id,
                                type=ContentType.tool_response,
                            )
                        )
                        matched = True
                        break
            if not matched:
                # Fallback: include without matching (shouldn't happen normally)
                final.append(
                    Message(
                        role="tool",
                        content=msg.content,
                        type=ContentType.tool_response,
                    )
                )
        elif msg.role == "assistant":
            prev_assistant = msg
            final.append(msg)
        else:
            final.append(msg)

    return final
