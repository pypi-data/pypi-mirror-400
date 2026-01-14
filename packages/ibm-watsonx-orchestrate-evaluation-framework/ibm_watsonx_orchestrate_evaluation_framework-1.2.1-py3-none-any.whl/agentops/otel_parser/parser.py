from dotenv import load_dotenv
from langfuse.api import TraceWithDetails
from langfuse.api.resources.trace.types.traces import Traces

load_dotenv()

import time
from collections import defaultdict
from functools import partial
from typing import Any, Dict, List, Optional

import rich
from langfuse import get_client

langfuse_client = None

from agentops.otel_parser import (
    claude_parser,
    crewai_parser,
    langflow_parser,
    langgraph_parser,
    pydantic_parser,
    wxo_parser,
)
from agentops.otel_parser.common import ObsNode, dfs_
from agentops.type import ContentType, Function, Message, ToolCall


def poll_messages(session_id, timeout=10, poll_interval=2):
    start_time = time.time()

    while True:
        messages = parse_session(session_id)

        if len(messages) > 0:
            return messages

        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout:
            rich.print("[r] Timeout reached, messages not available yet.[r]")
            return []

        time.sleep(poll_interval)


def parse_session(session_id) -> list[Message]:
    traces = get_traces(session_id)
    messages: list[Message] = []
    seen = []
    for tr in traces.data:
        agent_framework = get_agent_framework(tr)
        if agent_framework == "openinference":
            # this is fallback implementation that simplifies the logic
            trace_messages = openinference_fallback(tr)
        else:
            trace_messages = parse_trace(agent_framework, trace=tr)
        for msg in trace_messages:
            if msg.hash() not in seen:
                messages.append(msg)
                seen.append(msg.hash())

    return messages


def parse_trace(agent_framework, trace) -> list[Message]:
    # parse trace into a list of messages
    messages: list[Message] = []
    parsers_to_try = []
    if agent_framework == "langfuse.langgraph_agent":
        parser_func = langgraph_parser.parse_observations
    elif agent_framework == "langfuse.langflow":
        parser_func = partial(
            langflow_parser.parse_observations, dfs_callable=dfs_
        )
    elif agent_framework == "langgraph_agent":
        parser_func = langgraph_parser.parse_observations
    elif agent_framework == "pydantic_ai":
        parser_func = pydantic_parser.parse_observations
        sys_message = pydantic_parser.get_system_message(trace)
        if sys_message:
            messages.append(sys_message)
    elif agent_framework == "crewai":
        parser_func = crewai_parser.parse_observations
        sys_message = crewai_parser.get_system_message(trace)
        if sys_message:
            messages.append(sys_message)
        # Also try to parse from trace output directly
        trace_messages = crewai_parser.parse_trace_output(trace)
        messages = add_messages(messages, trace_messages)
    elif agent_framework == "claude_agent":
        parser_func = claude_parser.parse_observations
    else:
        parser_func = None
        parsers_to_try = [
            partial(langflow_parser.parse_observations, dfs_callable=dfs_),
            wxo_parser.parse_observations,
        ]
    observations = get_observations(trace.id)
    dfs_observations = dfs_(observations)
    if parser_func:
        parsed_messages = parser_func(observations, dfs_observations)
        messages = add_messages(messages, parsed_messages)
    else:
        for parser_func in parsers_to_try:
            try:
                parsed_messages = parser_func(observations, dfs_observations)
                if not parsed_messages:
                    continue
                messages = add_messages(messages, parsed_messages)
                break
            except Exception as e:
                print(e)
    return messages


def add_messages(
    messages: list[Message], parsed_messages: list[Message]
) -> list[Message]:
    ret: list[Message] = []
    seen: set[str] = set()
    for msg in messages:
        msg_hash = msg.hash()
        if msg_hash in seen:
            continue
        seen.add(msg_hash)
        ret.append(msg)
    for msg in parsed_messages:
        msg_hash = msg.hash()
        if msg_hash in seen:
            continue
        seen.add(msg_hash)
        ret.append(msg)
    return ret


def get_agent_framework(trace):
    """
    Supported frameworks:
    - OpenInference
        - Pydantic AI
        - Langflow
        - Langgraph Agent
    - LangFuse
        - Langflow
        - LangGraph Agent
    """
    md_attrs = trace.metadata.get("attributes", {})
    scope = trace.metadata.get("scope", {})
    scope_name = scope.get("name", "")

    # Claude Agent SDK detection - trace name is "claude.conversation"
    if trace.name == "claude.conversation":
        return "claude_agent"

    if scope_name == "langfuse-sdk":
        if trace.name == "LangGraph":
            return "langfuse.langgraph_agent"

    if "langflow.project.name" in md_attrs.keys():
        return "langflow"

    if "pydantic-ai" in scope_name:
        return "openinference"

    if "crewai" in scope_name:
        return "crewai"

    if "openinference.instrumentation.langchain" in scope_name:
        # TODO: need to find a better way to detect Langgraph Agent
        return "langgraph_agent"

    if "openinfererence.instrumentation" in scope_name:
        # a much simpler fallback implementation. proves to work with a few well known types like
        # openinference.instrumentation.openai
        # reserve as fallback until more test has been conducted
        return "openinference"

    # check for langflow
    # get observations for trace
    observations = dfs_(get_observations(trace.id))
    for obs in observations:
        if "from_langflow_component" in obs.obs.metadata.keys():
            return "langfuse.langflow"
    return "UNKNOWN"


def _extract_msg(msg):
    # simplifies for downstream evaluation
    if (
        msg["role"].lower() == "tool"
        or msg["role"].lower() == "assistant"
        or msg["role"].lower() == "system"
    ):
        role = "assistant"
    else:
        role = "user"

    content = ""
    if "content" in msg:
        content = msg["content"]
    tool_calls = None
    if "tool_calls" in msg:
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

    message = Message(
        role=role,
        content=content,
        tool_calls=tool_calls,
        type=ContentType.tool_call,
    )
    return message


def openinference_fallback(trace: TraceWithDetails) -> list[Message]:
    seen = (
        set()
    )  # within fallback duplication just in case input/output overlaps
    messages = []

    if trace.input:
        for msg in trace.input:
            message: Message = _extract_msg(msg)
            if message.hash() not in seen:
                messages.append(message)
                seen.add(message.hash())
    if trace.output:
        for msg in trace.output:
            message: Message = _extract_msg(msg)
            if message.hash() not in seen:
                messages.append(message)
                seen.add(message.hash())

    return messages


def get_traces(session_id) -> Traces:
    #  TO-DO: need to refactor this
    #  too much dependency on langfuse trace client
    client = langfuse_client if langfuse_client is not None else get_client()
    traces = client.api.trace.list(
        session_id=session_id,
        limit=100,
    )
    # sort by timestamp
    traces.data.sort(key=lambda x: x.timestamp)
    return traces


def get_observations(
    trace_id: str,
    *,
    page_limit: int = 100,
    max_pages: Optional[int] = None,
):
    """
    Fetch all Langfuse observations for a trace using pagination, then build a time-sorted forest.

    Args:
        trace_id: Langfuse trace id.
        page_limit: Page size used for pagination (default: 100).
        max_pages: Optional safety cap on the number of pages to fetch.

    Returns:
        Observation forest/tree built from all fetched observations.
    """
    if page_limit <= 0:
        raise ValueError("page_limit must be a positive integer")

    client = langfuse_client if langfuse_client is not None else get_client()

    all_observations: List[Any] = []
    page = 1

    while True:
        if max_pages is not None and page > max_pages:
            break

        resp = client.api.observations.get_many(
            trace_id=trace_id,
            page=page,
            limit=page_limit,
        )

        batch = getattr(resp, "data", None) or []
        if not batch:
            break

        all_observations.extend(batch)

        # If we received fewer than requested, assume this was the last page
        if len(batch) < page_limit:
            break

        page += 1

    all_observations.sort(key=lambda x: x.start_time)
    return build_observation_forest(all_observations)


def build_observation_forest(observations: List[Any]) -> List[ObsNode]:
    """Return list of root nodes; each has .children forming a tree."""
    nodes: Dict[str, ObsNode] = {}
    children_by_parent: Dict[Optional[str], List[ObsNode]] = defaultdict(list)

    # 1. Create nodes for each observation
    for o in observations:
        node = ObsNode(o)
        nodes[o.id] = node
        parent_id = getattr(o, "parent_observation_id", None)
        children_by_parent[parent_id].append(node)

    # 2. Attach children to parents
    for parent_id, child_nodes in children_by_parent.items():
        if parent_id is None:
            continue
        parent_node = nodes.get(parent_id)
        if parent_node:
            parent_node.children.extend(child_nodes)
            for child_node in child_nodes:
                child_node.parent = parent_node

    # 3. Roots are those with parent_observation_id == None
    roots = children_by_parent[None]
    return roots


if __name__ == "__main__":
    messages = poll_messages(session_id="93a24957-dd7a-425d-b821-88de49940a6e")

    print(messages)
